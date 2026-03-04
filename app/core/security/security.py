# =====================================
# Standard Library
# =====================================
from datetime import datetime, timedelta, UTC
import secrets
import hashlib

# =====================================
# Third-Party
# =====================================
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt
from fastapi import Response

# =====================================
# Local
# =====================================
from app.core.config.config import settings

# =====================================
# Password Hasher
# =====================================
ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its Argon2 hash."""
    try:
        return ph.verify(hashed, password)
    except VerifyMismatchError:
        return False

# =====================================
# JWT Tokens
# =====================================
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.ACCESS_TOKEN_SECRET, algorithm="HS256")

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET, algorithm="HS256")

# =====================================
# Temporary Token
# =====================================
def generate_temp_token():
    """Generate a temporary token (hashed + expiry)."""
    un_hashed = secrets.token_hex(20)
    hashed = hashlib.sha256(un_hashed.encode()).hexdigest()
    expiry = datetime.now(UTC) + timedelta(minutes=settings.TEMP_TOKEN_EXPIRE_MINUTES)
    return un_hashed, hashed, expiry

# =====================================
# Cookie Helpers
# =====================================
def set_cookies(response: Response, access_token: str, refresh_token: str, secure: bool = False):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="Lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="Lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        path="/api/v1/users/refresh",
    )

def clear_cookies(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/users/refresh")
    