from pathlib import Path as _Path
import sys
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import argparse,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from sqlalchemy import select
from src.healthguard.db import init_db,SessionLocal,Patient,Reading,Alert
from src.healthguard.modeling import HealthGuardPredictor
from src.healthguard.config import settings
p=argparse.ArgumentParser(); p.add_argument("--dataset",required=True); p.add_argument("--limit-per-patient",type=int,default=20); p.add_argument("--model-dir",default=None); a=p.parse_args()
model_dir=a.model_dir or settings.model_dir; pred=HealthGuardPredictor(model_dir); df=pd.read_csv(a.dataset,parse_dates=["day"]); init_db(); db=SessionLocal()
try:
  for raw_pid,g in df.groupby("patient_id"):
    pseudo="HG-"+hashlib.sha256(str(raw_pid).encode()).hexdigest()[:10].upper()
    pat=db.scalar(select(Patient).where(Patient.pseudonym==pseudo))
    if not pat:
      first=g.iloc[0]; pat=Patient(pseudonym=pseudo,sex=str(first.get("sex","")),age_group=str(first.get("age_group",""))); db.add(pat); db.flush()
    for _,row in g.tail(a.limit_per_patient).iterrows():
      features={k:(None if pd.isna(v) else (v.item() if hasattr(v,"item") else v)) for k,v in row.items() if k in pred.features and k!="iforest_anomaly"}
      result=pred.predict(features); r=Reading(patient_id=pat.id,observed_at=row.day.to_pydatetime(),risk_probability=result["probability"],risk_band=result["risk_band"],model_horizon_hours=pred.meta["horizon_hours"],features=features); db.add(r); db.flush()
      if result["positive"]: db.add(Alert(patient_id=pat.id,reading_id=r.id,severity=result["risk_band"],status="open"))
  db.commit(); print("Database seeded with pseudonymous model outputs.")
finally: db.close()
