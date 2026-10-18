from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from src.healthguard.config import settings
from src.healthguard.db import SessionLocal, User, Patient, Reading, Alert, AuditEvent, audit
from src.healthguard.security import verify_password, create_token, decode_token
from src.healthguard.modeling import HealthGuardPredictor

app=FastAPI(title="HealthGuard-AI API",version="1.0.0",description="Research-only secure RPM prediction API")
security=HTTPBearer()
_predictor=None

def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()

def get_predictor():
    global _predictor
    if _predictor is None:
        try: _predictor=HealthGuardPredictor(settings.model_dir)
        except Exception as e: raise HTTPException(503,f"Model unavailable: {e}")
    return _predictor

def current_user(creds:HTTPAuthorizationCredentials=Depends(security),db:Session=Depends(get_db)):
    try: payload=decode_token(creds.credentials)
    except jwt.PyJWTError: raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid or expired token")
    user=db.scalar(select(User).where(User.username==payload.get("sub"),User.active==True))
    if not user: raise HTTPException(401,"Inactive or unknown user")
    return user

def require(*roles):
    def dep(u:User=Depends(current_user)):
        if u.role not in roles: raise HTTPException(403,"Insufficient role")
        return u
    return dep

class Login(BaseModel): username:str; password:str
class ScoreRequest(BaseModel):
    patient_id:str=Field(...,description="Pseudonymous identifier")
    observed_at:datetime|None=None
    features:dict[str,Any]

@app.get("/health")
def health(): return {"status":"ok","service":settings.app_name}

@app.post("/auth/login")
def login(body:Login,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.username==body.username))
    if not u or not u.active or not verify_password(body.password,u.password_hash):
        if u: audit(db,body.username,"LOGIN",result="failed")
        raise HTTPException(401,"Invalid credentials")
    token=create_token(u.username,u.role); audit(db,u.username,"LOGIN")
    return {"access_token":token,"token_type":"bearer","role":u.role}

@app.get("/model/metadata")
def metadata(u:User=Depends(current_user)):
    return get_predictor().meta

@app.post("/monitoring/score")
def score(body:ScoreRequest,db:Session=Depends(get_db),u:User=Depends(require("admin","clinician"))):
    pred=get_predictor().predict(body.features)
    p=db.scalar(select(Patient).where(Patient.pseudonym==body.patient_id))
    if not p:
        p=Patient(pseudonym=body.patient_id); db.add(p); db.flush()
    r=Reading(patient_id=p.id,observed_at=body.observed_at or datetime.now(timezone.utc),risk_probability=pred["probability"],
              risk_band=pred["risk_band"],model_horizon_hours=get_predictor().meta["horizon_hours"],features=body.features)
    db.add(r); db.flush()
    if pred["positive"]:
        db.add(Alert(patient_id=p.id,reading_id=r.id,severity=pred["risk_band"],status="open"))
    db.commit(); audit(db,u.username,"MODEL_INFERENCE",resource=body.patient_id,details={"risk":pred["probability"],"band":pred["risk_band"]})
    return pred

@app.get("/monitoring/patients")
def patients(db:Session=Depends(get_db),u:User=Depends(require("admin","clinician","researcher","auditor"))):
    rows=db.scalars(select(Patient).order_by(Patient.pseudonym)).all(); out=[]
    for p in rows:
        latest=db.scalar(select(Reading).where(Reading.patient_id==p.id).order_by(desc(Reading.observed_at)).limit(1))
        out.append({"patient_id":p.pseudonym,"sex":p.sex,"age_group":p.age_group,
                    "latest_risk":latest.risk_probability if latest else None,"risk_band":latest.risk_band if latest else None})
    audit(db,u.username,"PATIENT_LIST_VIEW")
    return out

@app.get("/monitoring/patients/{patient_id}/timeline")
def timeline(patient_id:str,db:Session=Depends(get_db),u:User=Depends(require("admin","clinician","researcher","auditor"))):
    p=db.scalar(select(Patient).where(Patient.pseudonym==patient_id))
    if not p: raise HTTPException(404,"Patient not found")
    rows=db.scalars(select(Reading).where(Reading.patient_id==p.id).order_by(Reading.observed_at)).all()
    audit(db,u.username,"PATIENT_VIEW",resource=patient_id)
    return [{"observed_at":r.observed_at,"risk_probability":r.risk_probability,"risk_band":r.risk_band,"features":r.features} for r in rows]

@app.get("/monitoring/alerts")
def alerts(status_filter:str|None=None,db:Session=Depends(get_db),u:User=Depends(require("admin","clinician","auditor"))):
    stmt=select(Alert).order_by(desc(Alert.created_at))
    if status_filter: stmt=stmt.where(Alert.status==status_filter)
    rows=db.scalars(stmt.limit(500)).all(); audit(db,u.username,"ALERT_LIST_VIEW")
    return [{"id":a.id,"patient_id":a.patient.pseudonym,"created_at":a.created_at,"severity":a.severity,"status":a.status,
             "acknowledged_by":a.acknowledged_by,"acknowledged_at":a.acknowledged_at} for a in rows]

@app.post("/monitoring/alerts/{alert_id}/acknowledge")
def acknowledge(alert_id:int,db:Session=Depends(get_db),u:User=Depends(require("admin","clinician"))):
    a=db.get(Alert,alert_id)
    if not a: raise HTTPException(404,"Alert not found")
    a.status="acknowledged"; a.acknowledged_by=u.username; a.acknowledged_at=datetime.now(timezone.utc); db.commit()
    audit(db,u.username,"ALERT_ACKNOWLEDGED",resource=str(alert_id)); return {"ok":True}

@app.get("/security/audit")
def audit_events(limit:int=200,db:Session=Depends(get_db),u:User=Depends(require("admin","auditor"))):
    rows=db.scalars(select(AuditEvent).order_by(desc(AuditEvent.occurred_at)).limit(min(limit,1000))).all()
    return [{"time":x.occurred_at,"actor":x.actor,"action":x.action,"resource":x.resource,"result":x.result,"details":x.details} for x in rows]
