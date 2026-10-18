from __future__ import annotations
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import average_precision_score
from sklearn.calibration import CalibratedClassifierCV
try:
    from sklearn.frozen import FrozenEstimator
except Exception:
    FrozenEstimator=None
from xgboost import XGBClassifier
from .metrics import choose_threshold, evaluate

META_COLS={"patient_id","day","sex","age_group"}

def split_by_patient(df,target,seed=42):
    groups=df["patient_id"].astype(str)
    gss=GroupShuffleSplit(n_splits=1,test_size=.20,random_state=seed)
    trainval_idx,test_idx=next(gss.split(df,df[target],groups))
    tv=df.iloc[trainval_idx].reset_index(drop=True); test=df.iloc[test_idx].reset_index(drop=True)
    gss2=GroupShuffleSplit(n_splits=1,test_size=.20,random_state=seed+1)
    tr_idx,val_idx=next(gss2.split(tv,tv[target],tv["patient_id"]))
    return tv.iloc[tr_idx].reset_index(drop=True),tv.iloc[val_idx].reset_index(drop=True),test

def feature_columns(df,target):
    drop={target,"patient_id","day"}
    drop.update(c for c in df.columns if c.startswith("target_") or c.startswith("future_event_types_"))
    return [c for c in df.columns if c not in drop]

def make_preprocessor(X):
    num=[c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    cat=[c for c in X.columns if c not in num]
    prep=ColumnTransformer([
        ("num",Pipeline([("impute",SimpleImputer(strategy="median",add_indicator=True)),("scale",StandardScaler())]),num),
        ("cat",Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore",sparse_output=False))]),cat),
    ],sparse_threshold=0)
    return prep,num,cat

def add_anomaly_feature(train,val,test,features,target,seed=42):
    numeric=[c for c in features if pd.api.types.is_numeric_dtype(train[c])]
    pipe=Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())])
    Xfit=pipe.fit_transform(train[numeric])
    normal_mask=train[target].to_numpy()==0
    fit_x=Xfit[normal_mask] if normal_mask.sum()>=10 else Xfit
    iso=IsolationForest(n_estimators=300,contamination="auto",random_state=seed,n_jobs=-1)
    iso.fit(fit_x)
    outs=[]
    for frame in (train,val,test):
        z=pipe.transform(frame[numeric])
        f=frame.copy(); f["iforest_anomaly"]=-iso.decision_function(z); outs.append(f)
    return (*outs, {"preprocessor":pipe,"model":iso,"numeric_features":numeric})


def static_rule_prob(frame):
    """Published TIHM-style static threshold baseline using same-day measurements only."""
    f=frame.copy()
    flag=np.zeros(len(f),dtype=bool)
    def outside(col,lo=None,hi=None):
        nonlocal flag
        if col in f:
            x=pd.to_numeric(f[col],errors="coerce")
            m=pd.Series(False,index=f.index)
            if lo is not None: m |= x < lo
            if hi is not None: m |= x > hi
            flag |= m.fillna(False).to_numpy()
    outside("phys_systolic_blood_pressure",80,190)
    outside("phys_diastolic_blood_pressure",50,110)
    outside("phys_heart_rate",55,100)
    outside("phys_body_temperature",35,37.6)
    outside("phys_o_e_total_body_water",40,70)
    if "phys_o_e_body_weight" in f and "phys_o_e_body_weight_hist7_mean" in f:
        cur=pd.to_numeric(f["phys_o_e_body_weight"],errors="coerce")
        hist=pd.to_numeric(f["phys_o_e_body_weight_hist7_mean"],errors="coerce")
        flag |= (cur < .95*hist).fillna(False).to_numpy()
    return np.where(flag,.90,.10)

def train_all(df,horizon,model_dir,report_dir,seed=42):
    target=f"target_{horizon}h"
    if target not in df: raise ValueError(f"Missing {target}")
    df=df.dropna(subset=["patient_id","day"]).copy()
    df["day"]=pd.to_datetime(df["day"])
    train,val,test=split_by_patient(df,target,seed)
    base_features=feature_columns(train,target)
    train,val,test,anomaly=add_anomaly_feature(train,val,test,base_features,target,seed)
    features=feature_columns(train,target)
    Xtr,Xv,Xte=train[features],val[features],test[features]
    ytr,yv,yte=train[target].astype(int),val[target].astype(int),test[target].astype(int)
    rule_val=static_rule_prob(val); rule_test=static_rule_prob(test)
    rule_val_pr=float(average_precision_score(yv,rule_val)) if yv.nunique()>1 else 0.0
    prep,_,_=make_preprocessor(Xtr)
    pos=max(int(ytr.sum()),1); neg=max(len(ytr)-pos,1); spw=neg/pos
    candidates={
        "logistic":LogisticRegression(max_iter=3000,class_weight="balanced",random_state=seed),
        "random_forest":RandomForestClassifier(n_estimators=500,min_samples_leaf=2,class_weight="balanced_subsample",random_state=seed,n_jobs=-1),
        "xgboost":XGBClassifier(n_estimators=450,max_depth=4,learning_rate=.035,subsample=.85,colsample_bytree=.85,
                                eval_metric="logloss",scale_pos_weight=spw,random_state=seed,n_jobs=-1),
    }
    fitted={}; scores={}
    for name,est in candidates.items():
        model=Pipeline([("preprocess",prep),("model",est)])
        model.fit(Xtr,ytr)
        p=model.predict_proba(Xv)[:,1]
        scores[name]=float(average_precision_score(yv,p)) if yv.nunique()>1 else 0.0
        fitted[name]=model
    best_name=max(scores,key=scores.get); best=fitted[best_name]
    if FrozenEstimator is not None:
        calibrated=CalibratedClassifierCV(FrozenEstimator(best),method="sigmoid")
        calibrated.fit(Xv,yv)
    else:
        calibrated=CalibratedClassifierCV(best,method="sigmoid",cv="prefit")
        calibrated.fit(Xv,yv)
    pv=calibrated.predict_proba(Xv)[:,1]
    threshold=choose_threshold(yv,pv)
    pte=calibrated.predict_proba(Xte)[:,1]
    metrics=evaluate(yte,pte,threshold,patient_days=len(test))
    model_dir=Path(model_dir); report_dir=Path(report_dir); model_dir.mkdir(parents=True,exist_ok=True); report_dir.mkdir(parents=True,exist_ok=True)
    joblib.dump(calibrated,model_dir/"model_calibrated.joblib")
    joblib.dump(best,model_dir/"model_base.joblib")
    joblib.dump(anomaly,model_dir/"anomaly.joblib")
    metadata={
        "project":"HealthGuard-AI","horizon_hours":horizon,"target":target,"best_model":best_name,
        "validation_pr_auc_by_model":{"static_rules":rule_val_pr,**scores},"threshold":threshold,"features":features,"seed":seed,
        "train_patients":int(train.patient_id.nunique()),"validation_patients":int(val.patient_id.nunique()),"test_patients":int(test.patient_id.nunique()),
        "train_rows":len(train),"validation_rows":len(val),"test_rows":len(test),"test_metrics":metrics,
        "static_rule_test_metrics":evaluate(yte,rule_test,0.5,patient_days=len(test)),
    }
    (model_dir/"metadata.json").write_text(json.dumps(metadata,indent=2))
    (report_dir/"metrics.json").write_text(json.dumps(metadata,indent=2))
    test_out=test[["patient_id","day",target]].copy(); test_out["probability"]=pte; test_out["prediction"]=(pte>=threshold).astype(int)
    test_out.to_csv(report_dir/"test_predictions.csv",index=False)
    return metadata

class HealthGuardPredictor:
    def __init__(self,model_dir):
        p=Path(model_dir)
        self.model=joblib.load(p/"model_calibrated.joblib")
        self.anomaly=joblib.load(p/"anomaly.joblib")
        self.meta=json.loads((p/"metadata.json").read_text())
        self.features=self.meta["features"]
    def _with_anomaly(self, frame):
        frame=frame.copy()
        if "iforest_anomaly" not in frame.columns:
            a=self.anomaly; nums=a["numeric_features"]
            for c in nums:
                if c not in frame: frame[c]=np.nan
            z=a["preprocessor"].transform(frame[nums])
            frame["iforest_anomaly"]=-a["model"].decision_function(z)
        return frame
    def predict(self,feature_dict):
        f=pd.DataFrame([feature_dict])
        f=self._with_anomaly(f)
        for c in self.features:
            if c not in f: f[c]=np.nan
        p=float(self.model.predict_proba(f[self.features])[:,1][0])
        threshold=float(self.meta["threshold"])
        if p>=max(.85,threshold): band="critical"
        elif p>=threshold: band="high"
        elif p>=max(.35,threshold*.6): band="moderate"
        else: band="low"
        return {"probability":p,"threshold":threshold,"risk_band":band,"positive":bool(p>=threshold)}
