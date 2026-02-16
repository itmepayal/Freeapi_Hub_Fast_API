# =====================================
# Standard Library
# =====================================
import uuid

# =====================================
# SQLAlchemy
# =====================================
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# =====================================
# Local Imports
# =====================================
from app.core.db.connect import Base
from app.models.mixins import TimestampMixin
from app.api.v1.auth.enums import UserRole, LoginType


# =====================================
# User Model
# =====================================
class User(Base, TimestampMixin):
    __tablename__ = "users"

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_username", "username"),
        Index("idx_user_role", "role"),
        Index("idx_user_verified", "is_email_verified"),
    )

    # ---------------------------------
    # Primary Key
    # ---------------------------------
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # ---------------------------------
    # Identity Fields
    # ---------------------------------
    username = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    email = Column(
        String(120),
        nullable=False,
        unique=True,
        index=True
    )

    password = Column(
        String,
        nullable=False
    )

    # ---------------------------------
    # Profile Fields
    # ---------------------------------
    avatar_url = Column(
        String,
        default="https://via.placeholder.com/200x200.png"
    )

    avatar_local_path = Column(String)

    bio = Column(String(300))
    full_name = Column(String(120))

    # ---------------------------------
    # Role & Login
    # ---------------------------------
    role = Column(
        Enum(UserRole, name="user_role_enum"),
        default=UserRole.USER,
        nullable=False
    )

    login_type = Column(
        Enum(LoginType, name="login_type_enum"),
        default=LoginType.EMAIL_PASSWORD,
        nullable=False
    )

    # ---------------------------------
    # Account Status
    # ---------------------------------
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # ---------------------------------
    # Auth Tokens
    # ---------------------------------
    refresh_token = Column(String)

    # Password reset
    forgot_password_token = Column(String)
    forgot_password_expiry = Column(DateTime)

    # Email verification
    email_verification_token = Column(String)
    email_verification_expiry = Column(DateTime)

    # ---------------------------------
    # Security Tracking
    # ---------------------------------
    last_login_at = Column(DateTime)
    last_login_ip = Column(String)

    failed_login_attempts = Column(String, default="0")
    locked_until = Column(DateTime)

    # ---------------------------------
    # Relationships
    # ---------------------------------
    todos = relationship(
        "Todo",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

