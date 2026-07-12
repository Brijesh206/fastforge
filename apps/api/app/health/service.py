"""Health check service."""

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.dependencies.database import get_database_manager
from app.health.schemas import HealthResponse
from fastforge_database import DatabaseManager
from fastforge_logging import get_logger

logger = get_logger("app.health")


class HealthService:
    """Service for application health checks."""

    def __init__(self, database_manager: DatabaseManager) -> None:
        self._database_manager = database_manager

    def live(self) -> HealthResponse:
        """Return liveness status without checking dependencies."""
        return HealthResponse(status="ok", service="api", checks={"app": "ok"})

    async def ready(self) -> HealthResponse:
        """Return readiness status, including critical dependencies."""
        database_status = await self._check_database()
        status = "ok" if database_status == "ok" else "degraded"
        return HealthResponse(
            status=status,
            service="api",
            checks={
                "app": "ok",
                "database": database_status,
            },
        )

    async def health(self) -> HealthResponse:
        """Return aggregate health status."""
        return await self.ready()

    async def _check_database(self) -> str:
        """Check database connectivity."""
        try:
            async with self._database_manager.session() as session:
                await session.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            logger.warning("Database health check failed", exception_type=type(exc).__name__)
            return "unavailable"
        return "ok"


def get_health_service(
    database_manager: DatabaseManager = Depends(get_database_manager),
) -> HealthService:
    """Return the health service."""
    return HealthService(database_manager)
