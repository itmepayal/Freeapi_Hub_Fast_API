# =====================================
# FastAPI / SQLAlchemy
# =====================================
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# =====================================
# Schemas
# =====================================
from app.api.v1.user.schemas import (
    UserOut,
    TokenSchema,
    UserCreate,
    LoginRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    EmailSchema,
    AssignRoleSchema,
)

# =====================================
# Services
# =====================================
from app.api.v1.user.services import (
    login_user,
    create_user,
    logout_user,
    refresh_user_token,
    assign_role_service,
    change_password_service,
    forgot_password_service,
    reset_password_service,
    verify_email_service,
    resend_verification_service,
    handle_google_callback,
    handle_github_callback,
)

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
# Dependencies
# =====================================
from app.api.dependencies.auth import get_current_user

# =====================================
# Response Wrapper
# =====================================
from app.utils.response import APIResponse

# =====================================
# Router Configuration
# =====================================
router = APIRouter(
    tags=["Authentication"],
)

# =====================================
# Register
# =====================================
@router.post("/register", response_model=APIResponse[UserOut])
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    user = create_user(db, user_data)

    return APIResponse(
        data=user,
        message="User created successfully",
    )


# =====================================
# Login
# =====================================
@router.post("/login", response_model=APIResponse[TokenSchema])
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    token_data = login_user(
        db=db,
        username=payload.username,
        password=payload.password,
    )

    return APIResponse(
        data=token_data,
        message="Login successful",
    )

# =====================================
# Current User
# =====================================
@router.get("/me", response_model=APIResponse[UserOut])
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return APIResponse(
        data=current_user,
        message="User profile retrieved successfully",
    )


# =====================================
# Logout
# =====================================
@router.post("/logout", response_model=APIResponse[None])
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logout_user(db, current_user)

    return APIResponse(
        data=None,
        message="Logged out successfully",
    )


# =====================================
# Refresh Token
# =====================================
@router.post("/refresh", response_model=APIResponse[TokenSchema])
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    token_data = refresh_user_token(
        db=db,
        refresh_token=payload.refresh_token,
    )

    return APIResponse(
        data=token_data,
        message="Token refreshed successfully",
    )


# =====================================
# Change Password
# =====================================
@router.post("/change-password", response_model=APIResponse[None])
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    change_password_service(
        db=db,
        user=current_user,
        old_password=payload.old_password,
        new_password=payload.new_password,
    )

    return APIResponse(
        data=None,
        message="Password changed successfully",
    )


# =====================================
# Forgot Password
# =====================================
@router.post("/forgot-password", response_model=APIResponse[None])
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    forgot_password_service(
        db=db,
        email=payload.email,
    )

    return APIResponse(
        data=None,
        message="If the email is registered, a reset link has been sent",
    )


# =====================================
# Reset Password
# =====================================
@router.post("/reset-password", response_model=APIResponse[None])
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    reset_password_service(
        db=db,
        token=payload.token,
        new_password=payload.new_password,
    )

    return APIResponse(
        data=None,
        message="Password has been reset successfully",
    )


# =====================================
# Verify Email
# =====================================
@router.get("/verify-email/{token}", response_model=APIResponse[None])
def verify_email(
    token: str,
    db: Session = Depends(get_db),
):
    verify_email_service(db, token)

    return APIResponse(
        data=None,
        message="Email verified successfully",
    )


# =====================================
# Resend Email Verification
# =====================================
@router.post("/resend-email-verification", response_model=APIResponse[None])
def resend_verification(
    body: EmailSchema,
    db: Session = Depends(get_db),
):
    resend_verification_service(db, body.email)

    return APIResponse(
        data=None,
        message="If the email is registered, a verification link has been sent",
    )


# =====================================
# Assign Role
# =====================================
@router.post("/assign-role/{user_id}", response_model=APIResponse[None])
def assign_role(
    user_id: str,
    body: AssignRoleSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assign_role_service(
        db=db,
        user_id=user_id,
        role=body.role,
        current_user=current_user,
    )

    return APIResponse(
        data=None,
        message="Role assigned successfully",
    )


# =====================================
# Google Login
# =====================================
@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


# =====================================
# Google Callback
# =====================================
@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    return await handle_google_callback(request, db, oauth)


# =====================================
# GitHub Login
# =====================================
@router.get("/github")
async def github_login(request: Request):
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)


# =====================================
# GitHub Callback
# =====================================
@router.get("/github/callback")
async def github_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    return await handle_github_callback(request, db, oauth)
