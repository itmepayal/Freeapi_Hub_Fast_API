# ==============================
# FastAPI Core Imports
# ==============================
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

# ==============================
# Database Setup
# ==============================
from app.core.db.connect import Base, engine

# ==============================
# API Routers
# ==============================
# Versioned route modules
from app.api.v1.health.routes import router as health_router
from app.api.v1.todo.routes import router as todo_router
from app.api.v1.auth.routes import router as auth_router

# ==============================
# Global Exception Handlers
# ==============================
from app.utils.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)


# ==============================
# Create FastAPI Application
# ==============================
app = FastAPI(
    title="API Hub",            
    version="1.0.0",            
    docs_url="/docs",           
    redoc_url="/redoc",        
)

# ==============================
# Enable CORS Middleware
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        
    allow_credentials=True,  
    allow_methods=["*"],       
    allow_headers=["*"],  
)

# ==============================
# Database Initialization
# ==============================
@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)

# ==============================
# Register API Routers
# ==============================

app.include_router(health_router, prefix="/api/v1/health")
app.include_router(auth_router, prefix="/api/v1/accounts")
app.include_router(todo_router, prefix="/api/v1/todos")

# ==============================
# Register Global Exception Handlers
# ==============================
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
