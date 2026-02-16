# =====================================
# FastAPI Core Imports
# =====================================
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException

# =====================================
# Standard API Response Wrapper
# =====================================
from app.utils.response import APIResponse

# =====================================
# HTTP Exception Handler
# =====================================
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            message=exc.detail,
            status="fail"
        ).dict()
    )

# =====================================
# Request Validation Error Handler
# =====================================
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    # Build readable validation message
    message = "; ".join([
        f"{err['loc'][-1]}: {err['msg']}"
        for err in errors
    ])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse(
            message=message,
            status="fail"
        ).dict()
    )

# =====================================
# Generic Exception Handler
# =====================================
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            message=str(exc),  
            status="fail"
        ).dict()
    )
