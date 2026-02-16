from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.core.config.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------
# Password
# -------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash_password(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# -------------------------
# JWT
# -------------------------
def create_access_token(data: dict):
    payload = data.copy()
    payload['exp'] = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MIN
    )
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
def decode_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

