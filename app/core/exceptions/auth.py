from fastapi import status
from .base import AppException

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )

class InvalidTokenException(AppException):
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_TOKEN",
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )
        