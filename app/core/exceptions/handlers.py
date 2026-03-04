from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException

from app.utils.response import APIResponse
from .base import AppException


# =====================================
# AppException Handler
# =====================================
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            message=exc.message,
            status="fail"
        ).model_dump(),
    )


# =====================================
# HTTP Exception Handler
# =====================================
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            message=exc.detail,
            status="fail"
        ).model_dump(),
    )


# =====================================
# Validation Error Handler
# =====================================
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    message = "; ".join([
        f"{err['loc'][-1]}: {err['msg']}"
        for err in errors
    ])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse(
            message=message,
            status="fail"
        ).model_dump(),
    )


# =====================================
# Generic Exception Handler
# =====================================
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            message="Internal server error",
            status="error"
        ).model_dump(),
    )