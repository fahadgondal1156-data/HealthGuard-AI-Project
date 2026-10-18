from __future__ import annotations
import numpy as np
from sklearn.metrics import (average_precision_score, roc_auc_score, precision_score, recall_score,
    f1_score, confusion_matrix, brier_score_loss, precision_recall_curve)

def choose_threshold(y, p):
    precision, recall, thresholds=precision_recall_curve(y,p)
    if len(thresholds)==0: return 0.5
    f1=2*precision[:-1]*recall[:-1]/(precision[:-1]+recall[:-1]+1e-12)
    return float(thresholds[int(np.nanargmax(f1))])

def expected_calibration_error(y,p,bins=10):
    y=np.asarray(y); p=np.asarray(p)
    edges=np.linspace(0,1,bins+1); ece=0.0
    for lo,hi in zip(edges[:-1],edges[1:]):
        mask=(p>=lo)&((p<hi) if hi<1 else (p<=hi))
        if mask.any(): ece += mask.mean()*abs(y[mask].mean()-p[mask].mean())
    return float(ece)

def evaluate(y,p,threshold,patient_days=None):
    pred=(np.asarray(p)>=threshold).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    out={
        "pr_auc": float(average_precision_score(y,p)) if len(set(y))>1 else None,
        "auroc": float(roc_auc_score(y,p)) if len(set(y))>1 else None,
        "precision": float(precision_score(y,pred,zero_division=0)),
        "recall_sensitivity": float(recall_score(y,pred,zero_division=0)),
        "f1": float(f1_score(y,pred,zero_division=0)),
        "specificity": float(tn/(tn+fp)) if tn+fp else None,
        "ppv": float(tp/(tp+fp)) if tp+fp else None,
        "npv": float(tn/(tn+fn)) if tn+fn else None,
        "brier": float(brier_score_loss(y,p)),
        "ece_10bin": expected_calibration_error(y,p,10),
        "threshold": float(threshold),
        "tp":int(tp),"tn":int(tn),"fp":int(fp),"fn":int(fn),
        "missed_event_rate": float(fn/(tp+fn)) if tp+fn else None,
    }
    if patient_days:
        out["false_alerts_per_patient_day"]=float(fp/patient_days)
    return out
