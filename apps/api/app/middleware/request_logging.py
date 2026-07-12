"""Request context and logging middleware."""

from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastforge_common.constants import REQUEST_ID_HEADER
from fastforge_logging import bind_log_context, clear_log_context, get_logger

logger = get_logger("app.requests")


def register_request_logging_middleware(app: FastAPI) -> None:
    """Register request logging middleware."""

    @app.middleware("http")
    async def request_logging_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
        bind_log_context(request_id=request_id, correlation_id=request_id)
        started_at = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            duration_ms = round((perf_counter() - started_at) * 1000, 2)
            logger.info(
                "HTTP request completed",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
                client_ip=request.client.host if request.client is not None else None,
                user_agent=request.headers.get("user-agent"),
            )
            clear_log_context()
