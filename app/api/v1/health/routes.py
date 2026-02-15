from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(tags=["Health"])

class HealthResponse(BaseModel):
    status:str
    timestamp: str

@router.get("/live", response_model=HealthResponse)
def live():
    return HealthResponse(
        status="alive",
        timestamp=datetime.utcnow().isoformat()
    )
