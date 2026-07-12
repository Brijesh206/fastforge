"""Health check routes."""

from fastapi import APIRouter, Depends

from app.health.schemas import HealthResponse
from app.health.service import HealthService, get_health_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(service: HealthService = Depends(get_health_service)) -> HealthResponse:
    """Return aggregate health status."""
    return await service.health()


@router.get("/live", response_model=HealthResponse)
async def live(service: HealthService = Depends(get_health_service)) -> HealthResponse:
    """Return liveness status."""
    return service.live()


@router.get("/ready", response_model=HealthResponse)
async def ready(service: HealthService = Depends(get_health_service)) -> HealthResponse:
    """Return readiness status."""
    return await service.ready()
