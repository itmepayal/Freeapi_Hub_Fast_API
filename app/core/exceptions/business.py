from fastapi import status
from .base import AppException


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
        )


class AlreadyExistsException(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="ALREADY_EXISTS",
        )


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict occurred"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
        )


class InvalidStateException(AppException):
    def __init__(self, message: str = "Invalid state transition"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_STATE",
        )


class BusinessRuleException(AppException):
    def __init__(self, message: str = "Business rule violation"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_RULE_VIOLATION",
        )


class InsufficientBalanceException(AppException):
    def __init__(self, message: str = "Insufficient balance"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INSUFFICIENT_BALANCE",
        )


class DomainValidationException(AppException):
    def __init__(self, message: str = "Invalid domain data"):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="DOMAIN_VALIDATION_ERROR",
        )
        