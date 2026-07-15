"""Root API router."""

from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.billing.router import router as billing_router
from app.health.router import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router)
api_router.include_router(billing_router)
