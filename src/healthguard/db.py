from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from .config import settings

connect_args={"check_same_thread":False} if settings.database_url.startswith("sqlite") else {}
engine=create_engine(settings.database_url,pool_pre_ping=True,connect_args=connect_args)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
class Base(DeclarativeBase): pass

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    username: Mapped[str]=mapped_column(String(100),unique=True,index=True)
    password_hash: Mapped[str]=mapped_column(String(300))
    role: Mapped[str]=mapped_column(String(30),default="clinician")
    active: Mapped[bool]=mapped_column(Boolean,default=True)

class Patient(Base):
    __tablename__="patients"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    pseudonym: Mapped[str]=mapped_column(String(100),unique=True,index=True)
    sex: Mapped[str|None]=mapped_column(String(30),nullable=True)
    age_group: Mapped[str|None]=mapped_column(String(50),nullable=True)

class Reading(Base):
    __tablename__="readings"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    patient_id: Mapped[int]=mapped_column(ForeignKey("patients.id"),index=True)
    observed_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),index=True)
    risk_probability: Mapped[float]=mapped_column(Float)
    risk_band: Mapped[str]=mapped_column(String(30),index=True)
    model_horizon_hours: Mapped[int]=mapped_column(Integer,default=24)
    features: Mapped[dict]=mapped_column(JSON)
    patient: Mapped[Patient]=relationship()

class Alert(Base):
    __tablename__="alerts"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    patient_id: Mapped[int]=mapped_column(ForeignKey("patients.id"),index=True)
    reading_id: Mapped[int]=mapped_column(ForeignKey("readings.id"))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    severity: Mapped[str]=mapped_column(String(30),index=True)
    status: Mapped[str]=mapped_column(String(30),default="open",index=True)
    acknowledged_by: Mapped[str|None]=mapped_column(String(100),nullable=True)
    acknowledged_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    patient: Mapped[Patient]=relationship()

class AuditEvent(Base):
    __tablename__="audit_events"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    occurred_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),index=True)
    actor: Mapped[str]=mapped_column(String(100),index=True)
    action: Mapped[str]=mapped_column(String(100),index=True)
    resource: Mapped[str|None]=mapped_column(String(200),nullable=True)
    result: Mapped[str]=mapped_column(String(30),default="success")
    details: Mapped[dict|None]=mapped_column(JSON,nullable=True)

def init_db(): Base.metadata.create_all(bind=engine)
def audit(db,actor,action,resource=None,result="success",details=None):
    db.add(AuditEvent(actor=actor,action=action,resource=resource,result=result,details=details)); db.commit()
