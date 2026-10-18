from pathlib import Path as _Path
import sys
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import argparse,getpass
from sqlalchemy import select
from src.healthguard.db import init_db,SessionLocal,User
from src.healthguard.security import hash_password
p=argparse.ArgumentParser(); p.add_argument("--username",default="admin"); p.add_argument("--password"); p.add_argument("--role",default="admin",choices=["admin","clinician","researcher","auditor"]); a=p.parse_args()
pw=a.password or getpass.getpass("Password: ");
if len(pw)<12: raise SystemExit("Use at least 12 characters.")
init_db(); db=SessionLocal()
try:
    u=db.scalar(select(User).where(User.username==a.username))
    if u: raise SystemExit("User already exists")
    db.add(User(username=a.username,password_hash=hash_password(pw),role=a.role)); db.commit(); print(f"Created {a.role} user {a.username}")
finally: db.close()
