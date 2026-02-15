# ==============================
# FastAPI Core Imports
# ==============================
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

# ==============================
# Database
# ==============================
from app.core.database import Base, engine

# ==============================
# Routers
# ==============================
from app.api.v1.todo.routes import router as todo_router

# ==============================
# Exception Handlers
# ==============================
from app.utils.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# ==============================
# Create FastAPI App
# ==============================
app = FastAPI(
    title="API Hub",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ==============================
# Database Initialization
# ==============================
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# ==============================
# Register Routers
# ==============================
app.include_router(todo_router)

# ==============================
# Register Global Exception Handlers
# ==============================
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
