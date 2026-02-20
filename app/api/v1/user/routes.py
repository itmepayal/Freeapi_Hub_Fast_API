# =====================================
# FastAPI / SQLAlchemy
# =====================================
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# =====================================
# Schemas
# =====================================
from app.api.v1.user.schemas import (
    UserOut, 
    TokenSchema, 
    UserCreate, 
    RefreshTokenRequest, 
    ChangePasswordRequest, 
    ForgotPasswordRequest,
    ResetPasswordRequest,
    EmailSchema,
    AssignRoleSchema
)

# =====================================
# Services
# =====================================
from app.api.v1.user.services import (
    authenticate_user, 
    login_user,
    create_user, me, 
    refresh_user_token, 
    change_password_service,
    forgot_password_service,
    reset_password_service,
    verify_email_service,
    resend_verification_service,
    handle_google_callback,
    handle_github_callback
)
from starlette.responses import RedirectResponse

# =====================================
# Database
# =====================================
from app.core.db.connect import get_db
from app.core.oauth.oauth import oauth

# =====================================
# Models
# =====================================
from app.api.v1.user.models import User

# =====================================
# Security Utilities
# =====================================
from app.core.security.security import create_access_token, create_refresh_token
from app.core.config.config import settings

# =====================================
# Response Wrapper
# =====================================
from app.utils.response import APIResponse

# =====================================
# Router Configuration
# =====================================
router = APIRouter(
    prefix="",
    tags=["Authentication"],
)

# =====================================
# Register User Endpoint
# =====================================
@router.post("/register", response_model=UserOut)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    user_obj = create_user(
        db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password
    )
    
    return APIResponse(
        data=user_obj,
        message="User created successfully",
    )

# =====================================
# Login Endpoint
# =====================================
@router.post("/login", response_model=TokenSchema)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    token_data = login_service(
        db,
        form_data.username,
        form_data.password
    )

    return APIResponse(
        data=token_data,
        message="Login successful"
    )
    
# =====================================
# Current User Endpoint
# =====================================
@router.get("/me", response_model=UserOut)
def read_current_user(
    current_user: User = Depends(me)
):
    return current_user

# =====================================
# Logout Endpoint
# =====================================
@router.post("/logout")
def logout(
    current_user: User = Depends(me),
    db: Session = Depends(get_db)
):
    
    current_user.refresh_token = None

    db.add(current_user)
    db.commit()

    return {
        "status": "success",
        "message": "Logged out successfully"
    }

# =====================================
# Refresh Token Endpoint
# =====================================
@router.post("/refresh", response_model=TokenSchema)
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),

):
    return refresh_user_token(
        db=db,
        refresh_token=payload.refresh_token
    )

# =====================================
# Change Password Endpoint
# =====================================
@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(me),
    db: Session = Depends(get_db),
):
    return change_password_service(
        db=db,
        user=current_user,
        old_password=payload.old_password,
        new_password=payload.new_password,
    )
    
# =====================================
# Forgot Password Endpoint
# =====================================
@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    return forgot_password_service(
        db=db,
        email=payload.email
    )

# =====================================
# Reset Password Endpoint
# =====================================
@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    return reset_password_service(
        db=db,
        token=payload.token,
        new_password=payload.new_password
    )

# =====================================
# Verify Email Endpoint
# =====================================
@router.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    return verify_email_service(db, token)

# =====================================
# Resend Verify Email Endpoint
# =====================================
@router.post("/resend-email-verification")
def resend_verification(
    body: EmailSchema,
    db: Session = Depends(get_db)
):
    return resend_verification_service(db, body.email)

# =====================================
# Assign Role Endpoint
# =====================================
@router.post("/assign-role/{user_id}")
def assign_role(
    user_id: str,
    body: AssignRoleSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(me), 
):
    return assign_role_service(db, user_id, body.role, current_user)

# =====================================
# Google Endpoint
# =====================================
@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

# =====================================
# Google Callback Endpoint
# =====================================
@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    return await handle_google_callback(request, db, oauth)

# =====================================
# GitHub Endpoint
# =====================================
@router.get("/github")
async def github_login(request: Request):
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)

# =====================================
# GitHub Endpoint
# =====================================
@router.get("/github/callback")
async def github_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    return await handle_github_callback(request, db, oauth)

