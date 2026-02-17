from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.v1.user.schemas import UserOut, TokenSchema, UserCreate
from app.api.v1.user.services import authenticate_user, create_user, me
from app.core.db.connect import get_db
from app.api.v1.user.models import User
from app.core.security.security import create_access_token, create_refresh_token

router = APIRouter(
    prefix="",
    tags=["Authentication"],
)

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, email=user_data.email, username=user_data.username, password=user_data.password)

@router.post("/login", response_model=TokenSchema)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    user.refresh_token = refresh_token
    db.add(user)
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(me)):
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(me), db: Session = Depends(get_db)):
    current_user.refresh_token = None
    db.add(current_user)
    db.commit()
    return {"status": "success", "message": "Logged out successfully"}
