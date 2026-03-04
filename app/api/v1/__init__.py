from fastapi import APIRouter
from app.api.v1.health.routes import router as health_router
from app.api.v1.user.routes import router as user_router
from app.api.v1.todos import router as todo_router

api_router_v1 = APIRouter()

api_router_v1.include_router(health_router, prefix="/health")
api_router_v1.include_router(user_router, prefix="/users")
api_router_v1.include_router(todo_router, prefix="/todos")
