from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import secrets
import hashlib
from app.core.config.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# ---------------- Password ----------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ---------------- JWT Tokens ----------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.ACCESS_TOKEN_SECRET, algorithm="HS256")

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET, algorithm="HS256")

# ---------------- Temporary Token ----------------
def generate_temp_token():
    un_hashed = secrets.token_hex(20)
    hashed = hashlib.sha256(un_hashed.encode()).hexdigest()
    expiry = datetime.utcnow() + timedelta(minutes=settings.TEMP_TOKEN_EXPIRE_MINUTES)
    return un_hashed, hashed, expiry
