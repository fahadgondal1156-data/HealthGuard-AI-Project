from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from .config import settings

_hasher=PasswordHasher()
def hash_password(password:str)->str: return _hasher.hash(password)
def verify_password(password:str,hashed:str)->bool:
    try:
        return bool(_hasher.verify(hashed,password))
    except VerifyMismatchError:
        return False
def create_token(username:str,role:str)->str:
    now=datetime.now(timezone.utc)
    payload={"sub":username,"role":role,"iat":now,"exp":now+timedelta(minutes=settings.access_token_minutes)}
    return jwt.encode(payload,settings.jwt_secret,algorithm=settings.jwt_algorithm)
def decode_token(token:str)->dict:
    return jwt.decode(token,settings.jwt_secret,algorithms=[settings.jwt_algorithm])
