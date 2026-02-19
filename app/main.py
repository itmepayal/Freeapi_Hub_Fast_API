import time
import uuid
import uvicorn
import os

# ==============================
# FastAPI Core Imports
# ==============================
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# ==============================
# Logger 
# ==============================
from app.core.logger.logging import logger

# ==============================
# Database Setup
# ==============================
from app.core.db.connect import Base, engine

# ==============================
# Middleware
# ==============================
from app.middleware.loggin import loggin_middleware

# ==============================
# API Routers
# ==============================
from app.api.v1.health.routes import router as health_router
from app.api.v1.todo.routes import router as todo_router
from app.api.v1.user.routes import router as auth_router

# ==============================
# Exception Handlers
# ==============================
from app.utils.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# ==============================
# Core Utilities
# ==============================
from app.core.config.config import settings

# ==============================
# App
# ==============================
app = FastAPI(
    title="API Hub",
    version="1.0.0",
    docs_url="/",
    redoc_url="/redoc",
)

# ==============================
# Logging Middleware
# ==============================
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_SESSION_KEY
)
app.middleware("http")(loggin_middleware)

# ==============================
# CORS
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# DB Init (dev only)
# ==============================
@app.on_event("startup")
async def on_startup():
    if os.getenv("ENV", "dev") == "dev":
        Base.metadata.create_all(bind=engine)

# ==============================
# Routers
# ==============================
app.include_router(health_router, prefix="/api/v1/health")
app.include_router(todo_router, prefix="/api/v1/todos")
app.include_router(auth_router, prefix="/api/v1/users")

# ==============================
# Exception Handlers
# ==============================
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ==============================
# Run
# ==============================
if __name__ == "__main__":
    uvicorn.run(
        "app:main",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_config=None,
    )
