from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from app.api.v1.user.models import User
from app.core.security.security import (
    create_access_token, 
    create_refresh_token, 
    generate_temp_token, 
    hash_password,
    verify_password
)
from jose import jwt, JWTError
from app.core.config.config import settings
from app.core.db.connect import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  

def create_user(db:Session, email: str, username:str, password: str):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already exists")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(email=email, username=username)
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:  
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.ACCESS_TOKEN_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
