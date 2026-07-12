"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.core.errors import register_exception_handlers
from app.lifespan import lifespan
from app.middleware.request_logging import register_request_logging_middleware
from fastforge_common.constants import DEFAULT_API_PREFIX


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    api = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        lifespan=lifespan,
    )
    register_exception_handlers(api)
    register_request_logging_middleware(api)
    api.include_router(api_router, prefix=DEFAULT_API_PREFIX)
    return api


def run() -> None:
    """Run the API server."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


app = create_app()
