"""Security response headers and request body-size limit.

The API serves JSON only, so the header set is the small one that matters for
an API: no MIME sniffing, no framing, no referrer leakage, and HSTS in
production (the app is expected to sit behind TLS there).
"""

from collections.abc import Awaitable, Callable
from http import HTTPStatus

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastforge_common.exceptions import ErrorCode
from fastforge_common.schemas import ErrorDetail, ErrorResponse

from app.config import get_settings

# 1 MiB — generous for every JSON endpoint this API exposes (the largest real
# payload is a Stripe webhook, typically a few KiB).
MAX_BODY_BYTES = 1 * 1024 * 1024


def register_security_headers_middleware(app: FastAPI) -> None:
    """Register security headers and body-size enforcement."""
    is_production = get_settings().is_production

    @app.middleware("http")
    async def security_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        content_length = request.headers.get("content-length")
        if (
            content_length is not None
            and content_length.isdigit()
            and int(content_length) > MAX_BODY_BYTES
        ):
            error = ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.VALIDATION_ERROR,
                    message="Request body too large.",
                )
            )
            return JSONResponse(
                status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                content=error.model_dump(mode="json"),
            )

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = response.headers.get("Cache-Control", "no-store")
        if is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains"
            )
        return response
