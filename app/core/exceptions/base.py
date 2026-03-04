from typing import Optional


class AppException(Exception):
    """
    Base application exception.
    All custom exceptions must inherit from this.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)
        