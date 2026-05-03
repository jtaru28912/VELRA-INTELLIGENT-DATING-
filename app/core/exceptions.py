class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 400,
        code: str = "app_error",
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class ExternalServiceError(AppError):
    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(
            message,
            status_code=502,
            code="external_service_error",
            details=details,
        )
