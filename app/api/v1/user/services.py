import hashlib
# =====================================
# FastAPI / SQLAlchemy
# =====================================
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import RedirectResponse

# =====================================
# Standard Library
# =====================================
from datetime import datetime

# =====================================
# Local Models
# =====================================
from app.api.v1.user.models import User

# =====================================
# Security Utilities
# =====================================
from app.core.security.security import (
    create_access_token, 
    create_refresh_token, 
    generate_temp_token, 
    hash_password,
    verify_password
)
from app.core.email.sendgrid_service import send_email

# =====================================
# JWT Handling
# =====================================
from jose import jwt, JWTError

# =====================================
# App Config / DB
# =====================================
from app.core.config.config import settings
from app.core.db.connect import get_db

# =====================================
# OAuth2 Bearer Token Extractor
# =====================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")  

# =====================================
# Create User Service
# =====================================
def create_user(db: Session, email: str, username: str, password: str):

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    user = User(email=email, username=username)
    user.set_password(password)

    raw_token, hashed_token, expiry = generate_temp_token()

    user.email_verification_token = hashed_token
    user.email_verification_expiry = expiry

    db.add(user)
    db.commit()
    db.refresh(user)

    verify_link = f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"

    send_email(
        to_email=user.email,
        template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
        dynamic_data={
            "username": user.username,
            "verify_link": verify_link,
        }
    )

    return user

# =====================================
# Authenticate User Credentials
# =====================================
def authenticate_user(db: Session, username: str, password: str) -> User | None:

    # Fetch user by username
    user = db.query(User).filter(User.username == username).first()

    # Return None if user not found
    if not user:
        return None
    
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email to continue."
        )

    # Verify provided password against stored hash
    if not verify_password(password, user.password):
        return None

    # Authentication successful
    return user

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    if user.is_email_verified:
        return {
            "status": "success",
            "message": "Email already verified"
        }

    user.is_email_verified = True
    user.email_verification_token = None
    user.email_verification_expiry = None

    db.commit()

    return {
        "status": "success",
        "message": "Email verified successfully"
    }

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

    db.commit()

    verify_link = f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"

    send_email(
        to_email=user.email,
        template_id=settings.SENDGRID_EMAIL_VERIFICATION_TEMPLATE_ID,
        dynamic_data={
            "username": user.username,
            "verify_link": verify_link,
        }
    )

# =====================================
# Current User 
# =====================================
def me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:  

    # Standard credential failure response
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT using configured secret + algorithm
        payload = jwt.decode(
            token,
            settings.ACCESS_TOKEN_SECRET,
            algorithms=["HS256"]
        )

        # Extract subject (user id) from token payload
        user_id: str = payload.get("sub")

        # Reject token if subject missing
        if user_id is None:
            raise credentials_exception

    # Catch any decode / signature / expiry errors
    except JWTError:
        raise credentials_exception

    # Load user from database using token subject
    user = db.query(User).filter(User.id == user_id).first()

    # Reject if user no longer exists
    if user is None:
        raise credentials_exception

    # Return authenticated user
    return user


# =====================================
# Refresh Token Service
# =====================================
def refresh_user_token(
    db: Session,
    refresh_token: str,
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid refresh token",
    )
    
    try:
        payload = jwt.decode(
            refresh_token,
            settings.REFRESH_TOKEN_SECRET,
            algorithms=["HS256"],
        )

        user_id = payload.get("sub")
        
        if not user_id:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # check user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or user.refresh_token != refresh_token:
        raise credentials_exception
    
    new_access = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})

    user.refresh_token = new_refresh
    db.add(user)
    db.commit()
    
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }
    
# =====================================
# Change Password Service
# =====================================
def change_password_service(
    db: Session,
    user: User,
    old_password: str,
    new_password: str
):
    if not verify_password(old_password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    if verify_password(new_password, user.password):
        raise HTTPException(
            status_code=400,
            detail="New password cannot be same as old password"
        )
    
    user.set_password(new_password)
    
    user.refresh_token = None

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"status": "success", "message": "Password changed successfully"}

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
    
    db.add(user)
    db.commit()
    
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
    
    send_email(
        to_email=user.email,
        template_id=settings.SENDGRID_PASSWORD_RESET_TEMPLATE_ID,
        dynamic_data={
            "username": user.username,
            "reset_link": reset_link,
        }
    )
    
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
        raise HTTPException(400, "Invalid reset token")

    if user.forgot_password_expiry < datetime.utcnow():
        raise HTTPException(400, "Token expired")

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
    db:Session,
    user_id: str, 
    new_role: str, 
    current_user: User
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to assign roles"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own role"
        )

    user.role = new_role.upper()
    
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": f"Role '{new_role}' assigned to user '{user.username}' successfully."}

# =====================================
# GOOGLE SERVICE
# =====================================
async def handle_google_callback(request, db: Session, oauth):

    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Google user info not found")

    email = user_info["email"]
    username = user_info.get("name") or email.split("@")[0]

    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            email=email,
            username=username,
            password=None,
            auth_provider="google",
            is_email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return _generate_login_response(user, db)


# =====================================
# GITHUB SERVICE
# =====================================
async def handle_github_callback(request, db: Session, oauth):

    token = await oauth.github.authorize_access_token(request)

    profile_resp = await oauth.github.get("user", token=token)
    profile = profile_resp.json()

    email_resp = await oauth.github.get("user/emails", token=token)
    emails = email_resp.json()

    primary_email = None
    for e in emails:
        if e.get("primary") and e.get("verified"):
            primary_email = e.get("email")
            break

    if not primary_email:
        raise HTTPException(status_code=400, detail="GitHub email not available")

    username = profile.get("name") or profile.get("login")

    user = db.query(User).filter(User.email == primary_email).first()

    if not user:
        user = User(
            email=primary_email,
            username=username,
            password=None,
            auth_provider="github",
            is_email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return _generate_login_response(user, db)


# =====================================
# COMMON TOKEN GENERATOR
# =====================================
def _generate_login_response(user: User, db: Session):

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user.refresh_token = refresh_token
    db.commit()

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/social-success?access_token={access_token}"
    )