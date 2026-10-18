from __future__ import annotations
from pathlib import Path as _Path
import sys
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import argparse, json
from pathlib import Path
import joblib, pandas as pd, numpy as np
import matplotlib.pyplot as plt
import shap
from sklearn.inspection import permutation_importance

p=argparse.ArgumentParser(); p.add_argument("--dataset",required=True); p.add_argument("--model-dir",required=True); p.add_argument("--max-rows",type=int,default=300); a=p.parse_args()
mdir=Path(a.model_dir); meta=json.loads((mdir/"metadata.json").read_text()); base=joblib.load(mdir/"model_base.joblib")
df=pd.read_csv(a.dataset); target=meta["target"]; features=meta["features"]
an=joblib.load(mdir/"anomaly.joblib"); nums=an["numeric_features"]
z=an["preprocessor"].transform(df[nums]); df["iforest_anomaly"]=-an["model"].decision_function(z)
for c in features:
    if c not in df: df[c]=np.nan
sample=df.sample(min(len(df),a.max_rows),random_state=42)
out=Path("reports")/f"{meta['horizon_hours']}h"; out.mkdir(parents=True,exist_ok=True)

# Model-agnostic permutation importance on original features.
r=permutation_importance(base,sample[features],sample[target].astype(int),scoring="average_precision",n_repeats=5,random_state=42,n_jobs=-1)
imp=pd.DataFrame({"feature":features,"importance":r.importances_mean,"std":r.importances_std}).sort_values("importance",ascending=False)
imp.to_csv(out/"feature_importance_permutation.csv",index=False)
top=imp.head(20).sort_values("importance"); plt.figure(figsize=(9,7)); plt.barh(top.feature,top.importance,xerr=top["std"]); plt.xlabel("Permutation importance (PR-AUC decrease)"); plt.tight_layout(); plt.savefig(out/"feature_importance_permutation.png",dpi=180); plt.close()

# SHAP on the selected estimator after the fitted preprocessing layer.
prep=base.named_steps["preprocess"]; est=base.named_steps["model"]
Z=prep.transform(sample[features]); names=prep.get_feature_names_out()
if Z.shape[0] > 200: Z=Z[:200]
try:
    if meta["best_model"] in {"xgboost","random_forest"}:
        exp=shap.TreeExplainer(est); sv=exp.shap_values(Z)
        if isinstance(sv,list): sv=sv[-1]
        arr=np.asarray(sv)
        if arr.ndim==3: arr=arr[:,:,1]
    else:
        background=Z[:min(100,len(Z))]
        exp=shap.LinearExplainer(est,background); arr=np.asarray(exp.shap_values(Z))
    shap_imp=pd.DataFrame({"feature":names,"mean_abs_shap":np.abs(arr).mean(axis=0)}).sort_values("mean_abs_shap",ascending=False)
    shap_imp.to_csv(out/"shap_global_importance.csv",index=False)
    top2=shap_imp.head(20).sort_values("mean_abs_shap"); plt.figure(figsize=(9,7)); plt.barh(top2.feature,top2.mean_abs_shap); plt.xlabel("Mean |SHAP value|"); plt.tight_layout(); plt.savefig(out/"shap_global_importance.png",dpi=180); plt.close()
    print("SHAP global importance written to",out)
except Exception as e:
    (out/"shap_error.txt").write_text(str(e)); print("SHAP calculation skipped:",e)
print(imp.head(20).to_string(index=False))
