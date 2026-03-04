# =====================================
# FastAPI / SQLAlchemy
# =====================================
from sqlalchemy.orm import Session

# =====================================
# Local Models
# =====================================
from app.api.v1.user.models import User


def issue_tokens(user: User, db: Session) -> dict:
    
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user.refresh_token = refresh_token
    db.add(user)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    