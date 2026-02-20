# =====================================
# SQLAlchemy Core Imports
# =====================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# =====================================
# Database URL
# =====================================
DATABASE_URL =  "postgresql://neondb_owner:npg_5dgTC4RFbLri@ep-green-wind-aih55vuq-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# =====================================
# Engine Creation
# =====================================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# =====================================
# Session Factory
# =====================================
SessionLocal = sessionmaker(bind=engine)

# =====================================
# Base Class for ORM Models
# =====================================
Base = declarative_base()

# =====================================
# Dependency: get_db()
# =====================================
def get_db():
    db = SessionLocal()
    try:
        # Provide session to request
        yield db
    finally:
        # Always close session after request finishes
        db.close()
