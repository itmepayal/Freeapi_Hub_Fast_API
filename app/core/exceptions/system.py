from fastapi import status
from .base import AppException


class InternalServerException(AppException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
        )


class ServiceUnavailableException(AppException):
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
        )