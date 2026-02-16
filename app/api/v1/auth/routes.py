from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db.connect import get_db
from app.api.v1.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.api.v1.auth.services import register_user, authenticate_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, data)
    return {"message": "User created", "id": user.id}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)

    if not user:
        raise HTTPException(401, "Invalid credentials")

    token = login_user(user)
    return {"access_token": token}

