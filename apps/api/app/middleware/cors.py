"""CORS middleware."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings


def register_cors_middleware(app: FastAPI) -> None:
    """Allow the browser frontend to call the API cross-origin.

    Scoped to the single frontend origin (``FRONTEND_BASE_URL``). ponytail:
    one origin is all the v1 web app needs — widen to a configurable list only
    when a second origin (e.g. a separate marketing site) actually appears.
    """
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_base_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
