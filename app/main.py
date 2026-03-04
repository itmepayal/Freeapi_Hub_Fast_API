import os
import uvicorn
from contextlib import asynccontextmanager

# ==============================
# SQL Alchemy Imports
# ==============================
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# ==============================
# FastAPI Core Imports
# ==============================
from fastapi import FastAPI, HTTPException
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
from app.api.v1 import api_router_v1

# ==============================
# Exception Handlers
# ==============================
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# ==============================
# Core Utilities
# ==============================
from app.core.config.config import settings


# ==============================
# Lifespan Handler
# ==============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("Database connected successfully")

        if os.getenv("ENV", "dev") == "dev":
            Base.metadata.create_all(bind=engine)
            logger.info("Tables created successfully")

    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        raise e

    yield

    logger.info("Application shutting down...")


# ==============================
# App
# ==============================
app = FastAPI(
    title="API Hub",
    version="1.0.0",
    docs_url="/",
    redoc_url="/redoc",
    lifespan=lifespan, 
)

# ==============================
# Middleware
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
# Routers
# ==============================
app.include_router(api_router_v1, prefix="/api/v1")

# ==============================
# Exception Handlers
# ==============================
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# ==============================
# Run
# ==============================
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_config=None,
    )