# =====================================
# FastAPI / Router Imports
# =====================================
from fastapi import APIRouter, status
from app.utils.response import APIResponse
import structlog

# =====================================
# Router
# =====================================
router = APIRouter(tags=["Health"])

# =====================================
# Health Check Endpoint
# =====================================
@router.get("", status_code=status.HTTP_200_OK, summary="Health Check")
def health_check():
    """
    Simple health check endpoint to verify API is running.
    """
    return APIResponse(
        status="success",
        message="Health check passed",
        data={"api": "ok"},
    )
