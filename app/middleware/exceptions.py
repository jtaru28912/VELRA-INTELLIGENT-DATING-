import logging

from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.exceptions import AppError


logger = logging.getLogger(__name__)


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except RequestValidationError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "error": "validation_error",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                },
            )
        except AppError as exc:
            logger.warning("Application error | code=%s message=%s", exc.code, exc.message)
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            )
        except Exception as exc:
            # Handle FastAPI/Starlette HTTPException explicitly to preserve status code
            from starlette.exceptions import HTTPException as StarletteHTTPException
            if isinstance(exc, StarletteHTTPException):
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"error": "http_error", "message": str(exc.detail)},
                )
            
            logger.exception("Unhandled server error: %s", exc)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                },
            )
