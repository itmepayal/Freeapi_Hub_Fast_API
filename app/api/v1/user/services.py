# =====================================
# Standard Library
# =====================================
import hashlib
from datetime import datetime

# =====================================
# SQLAlchemy
# =====================================
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import RedirectResponse

# =====================================
# Local Models
# =====================================
from app.api.v1.user.models import User

# =====================================
# Security Utilities
# =====================================
from app.core.security.security import (
    generate_temp_token,
    verify_password,
)
from app.core.security.token import issue_tokens

# =====================================
# Email Service
# =====================================
from app.core.email.sendgrid_service import send_email

# =====================================
# JWT
# =====================================
from jose import jwt, JWTError

# =====================================
# Config
# =====================================
from app.core.config.config import settings

# =====================================
# Shemas
# =====================================
from app.api.v1.user.schemas import UserCreate

# =====================================
# Custom Exceptions
# =====================================
from app.core.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    AlreadyExistsException,
    ConflictException,
    DomainValidationException,
)

# =====================================
# OAuth2 Bearer Token Extractor
# =====================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")  

# =====================================
# Create User Service
# =====================================
def create_user(db: Session, user_data: UserCreate):

    if db.query(User).filter(User.email == user_data.email).first():
        raise AlreadyExistsException("Email already exists")

    if db.query(User).filter(User.username == user_data.username).first():
        raise AlreadyExistsException("Username already exists")

    raw_token, hashed_token, expiry = generate_temp_token()

    user = User(
        email=user_data.email,
        username=user_data.username,
    )

    user.set_password(user_data.password)
    user.email_verification_token = hashed_token
    user.email_verification_expiry = expiry

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except SQLAlchemyError:
        db.rollback()
        raise

    try:
        verify_link = f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"

        send_email(
            to_email=user.email,
            template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
            dynamic_data={
                "username": user.username,
                "verify_link": verify_link,
            }
        )
    except Exception:
        try:
            db.delete(user)
            db.commit()
        except Exception:
            db.rollback()
        raise

    return user

# =====================================
# Authenticate User Credentials
# =====================================
def authenticate_user(db: Session, username: str, password: str) -> User:

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise UnauthorizedException("Incorrect username or password")

    if not user.is_email_verified:
        raise ForbiddenException("Please verify your email to continue.")

    if not verify_password(password, user.password):
        raise UnauthorizedException("Incorrect username or password")

    return user

# =====================================
# Login User
# =====================================
def login_user(db: Session, username: str, password: str):

    user = authenticate_user(db, username, password)

    if user.auth_provider != "LOCAL":
        raise ConflictException("This account is registered via social login.")

    return issue_tokens(user, db)

# =====================================
# LOGOUT SERVICE
# =====================================
def logout_user(db: Session, user: User):

    if not user:
        raise UnauthorizedException("User not authenticated")

    try:
        user.refresh_token = None
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

# =====================================
# Verify Email Service 
# =====================================
def verify_email_service(db: Session, token: str):

    hashed = hashlib.sha256(token.encode()).hexdigest()

    user = db.query(User).filter(
        User.email_verification_token == hashed,
        User.email_verification_expiry > datetime.utcnow()
    ).first()

    if not user:
        raise DomainValidationException("Invalid or expired verification token")

    if user.is_email_verified:
        return {"message": "Email already verified"}

    user.is_email_verified = True
    user.email_verification_token = None
    user.email_verification_expiry = None

    db.commit()

    return {"message": "Email verified successfully"}

# =====================================
# Resend Verify Email Service 
# =====================================
def resend_verification_service(db: Session, email: str):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"message": "If account exists, email sent"}

    if user.is_email_verified:
        return {"message": "Email already verified"}

    raw_token, hashed_token, expiry = generate_temp_token()

    user.email_verification_token = hashed_token
    user.email_verification_expiry = expiry

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    try:
        verify_link = f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"

        send_email(
            to_email=user.email,
            template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
            dynamic_data={
                "username": user.username,
                "verify_link": verify_link,
            }
        )
    except Exception:
        raise

    return {"message": "Verification email sent"}

# =====================================
# Refresh Token Service
# =====================================
def refresh_user_token(db: Session, refresh_token: str):

    try:
        payload = jwt.decode(
            refresh_token,
            settings.REFRESH_TOKEN_SECRET,
            algorithms=["HS256"],
        )

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")

        user_id = payload.get("sub")

        if not user_id:
            raise UnauthorizedException("Invalid refresh token")

    except JWTError:
        raise UnauthorizedException("Invalid refresh token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user or user.refresh_token != refresh_token:
        raise UnauthorizedException("Invalid refresh token")

    return issue_tokens(user, db)

# =====================================
# Change Password Service
# =====================================
def change_password_service(db: Session, user: User, old_password: str, new_password: str):

    if not verify_password(old_password, user.password):
        raise DomainValidationException("Current password is incorrect")

    if verify_password(new_password, user.password):
        raise DomainValidationException("New password cannot be same as old password")

    user.set_password(new_password)
    user.refresh_token = None

    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError:
        db.rollback()
        raise

    return {"message": "Password changed successfully"}


# =====================================
# Forgot Password Service
# =====================================
def forgot_password_service(db: Session, email: str):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"message": "If account exists, reset link sent"}

    raw_token, hashed_token, expiry = generate_temp_token()

    user.forgot_password_token = hashed_token
    user.forgot_password_expiry = expiry

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    try:
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

        send_email(
            to_email=user.email,
            template_id=settings.SENDGRID_PASSWORD_RESET_TEMPLATE_ID,
            dynamic_data={
                "username": user.username,
                "reset_link": reset_link,
            }
        )
    except Exception:
        raise

    return {"message": "If account exists, reset link sent"}

# =====================================
# Reset Password Service
# =====================================
def reset_password_service(db: Session, token: str, new_password: str):

    hashed_input = hashlib.sha256(token.encode()).hexdigest()

    user = db.query(User).filter(
        User.forgot_password_token == hashed_input,
        User.forgot_password_expiry > datetime.utcnow()
    ).first()

    if not user:
        raise DomainValidationException("Invalid or expired reset token")

    user.set_password(new_password)
    user.forgot_password_token = None
    user.forgot_password_expiry = None
    user.refresh_token = None

    db.commit()

    return {"message": "Password reset successful"}

# =====================================
# Assign Role Service
# =====================================
def assign_role_service(
    db: Session,
    user_id: str,
    new_role: str,
    current_user: User,
):

    if current_user.role != "ADMIN":
        raise ForbiddenException("You do not have permission to assign roles")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise NotFoundException("User not found")

    if user.id == current_user.id:
        raise DomainValidationException("You cannot change your own role")

    user.role = new_role.upper()

    db.commit()
    db.refresh(user)

    return {
        "message": f"Role '{new_role}' assigned to user '{user.username}' successfully."
    }
# =====================================
# GOOGLE SERVICE
# =====================================
async def handle_google_callback(request, db: Session, oauth):

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        raise UnauthorizedException("Google authorization failed")

    user_info = token.get("userinfo")
    if not user_info:
        raise NotFoundException("Google user info not found")

    email = user_info.get("email")
    if not email:
        raise DomainValidationException("Google account does not provide email")

    username = user_info.get("name") or email.split("@")[0]

    user = db.query(User).filter(User.email == email).first()

    if user:
        if user.auth_provider != "google":
            raise ConflictException(
                "Account already exists with different authentication provider."
            )
        return _generate_login_response(user, db)

    new_user = User(
        email=email,
        username=username,
        password=None,
        auth_provider="google",
        is_email_verified=True,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError:
        db.rollback()
        raise

    return _generate_login_response(new_user, db)

# =====================================
# GITHUB SERVICE
# =====================================
async def handle_github_callback(request, db: Session, oauth):

    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception:
        raise UnauthorizedException("GitHub authorization failed")

    profile_resp = await oauth.github.get("user", token=token)
    profile = profile_resp.json()

    email_resp = await oauth.github.get("user/emails", token=token)
    emails = email_resp.json()

    primary_email = next(
        (e["email"] for e in emails if e.get("primary") and e.get("verified")),
        None,
    )

    if not primary_email:
        raise DomainValidationException("Verified primary GitHub email not found")

    username = (
        profile.get("name")
        or profile.get("login")
        or primary_email.split("@")[0]
    )

    user = db.query(User).filter(User.email == primary_email).first()

    if user:
        if user.auth_provider != "github":
            raise ConflictException(
                "Account already exists with different authentication provider."
            )
        return _generate_login_response(user, db)

    new_user = User(
        email=primary_email,
        username=username,
        password=None,
        auth_provider="github",
        is_email_verified=True,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError:
        db.rollback()
        raise

    return _generate_login_response(new_user, db)

# =====================================
# COMMON TOKEN GENERATOR
# =====================================
def _generate_login_response(user: User, db: Session):

    tokens = issue_tokens(user, db)

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/social-success?access_token={tokens['access_token']}"
    )
