import logging
from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid4())
        request.state.request_id = request_id
        started_at = perf_counter()

        logger.info(
            "Request started | request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)
        except Exception as e:
            logger.error("Request failed | request_id=%s error=%s", request_id, str(e))
            raise e

        duration_ms = (perf_counter() - started_at) * 1000
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Request completed | request_id=%s method=%s path=%s status_code=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
