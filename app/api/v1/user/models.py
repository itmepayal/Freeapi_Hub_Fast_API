import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.db.connect import Base
from app.core.security.security import hash_password
from app.models.mixins import TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    auth_provider = Column(String, default="local")
    role = Column(String, default="ADMIN")
    is_email_verified = Column(Boolean, default=False)
    refresh_token = Column(String, nullable=True)
    forgot_password_token = Column(String, nullable=True)
    forgot_password_expiry = Column(DateTime, nullable=True)
    email_verification_token = Column(String, nullable=True)
    email_verification_expiry = Column(DateTime, nullable=True)
    
    def set_password(self, password: str):
        self.password = hash_password(password)

    def verify_password(self, password: str) -> bool:
        from app.core.security.security import verify_password
        return verify_password(password, self.password)
