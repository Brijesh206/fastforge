"""FastAPI application entry point."""

from fastapi import FastAPI
from fastforge_common.constants import DEFAULT_API_PREFIX

from app.api.router import api_router
from app.config import get_settings
from app.core.errors import register_exception_handlers
from app.lifespan import lifespan
from app.middleware.cors import register_cors_middleware
from app.middleware.request_logging import register_request_logging_middleware
from app.middleware.security import register_security_headers_middleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    api = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        lifespan=lifespan,
        # Interactive docs are a dev/staging tool; production exposes only the API.
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
    )
    register_exception_handlers(api)
    register_request_logging_middleware(api)
    register_security_headers_middleware(api)
    register_cors_middleware(api)
    api.include_router(api_router, prefix=DEFAULT_API_PREFIX)
    return api


def run() -> None:
    """Run the API server."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload and not settings.is_production,
    )


app = create_app()
