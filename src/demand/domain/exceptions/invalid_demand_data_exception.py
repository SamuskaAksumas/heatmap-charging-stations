"""Exception for invalid demand calculation data."""
from src.shared.domain.exceptions import DomainException


class InvalidDemandDataException(DomainException):
    """
    Raised when demand calculation data is invalid.

    This exception is thrown when:
    - Required data columns are missing
    - Data values are negative when they shouldn't be
    - Data frames have incompatible shapes for merging

    Attributes:
        message: Human-readable error description.
    """

    def __init__(self, message: str):
        super().__init__(f"Invalid demand data: {message}")
