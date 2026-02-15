from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from app.utils.response import APIResponse

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(message=exc.detail, status="fail").dict()
    )

async def validation_exception_handler(request: Request, exc: HTTPException):
    errors = exc.errors()
    message = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in errors])
    return JSONResponse(
        status_code=exe.status_code,
        content=APIResponse(message=message, status="fail").dict()
    )

async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=APIResponse(message=str(exc), status="fail").dict()
    )