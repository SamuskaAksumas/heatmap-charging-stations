"""Exception for invalid postal code values."""
from .domain_exception import DomainException


class InvalidPostalCodeException(DomainException):
    """
    Raised when a postal code value is invalid.

    This exception is thrown when:
    - The PLZ format is incorrect (not 5 digits)
    - The PLZ is outside the valid Berlin range (10000-14199)
    - The PLZ contains non-numeric characters

    Attributes:
        value: The invalid postal code value that caused the exception.
        message: Human-readable error description.
    """

    def __init__(self, value: str, reason: str = None):
        self.value = value
        if reason:
            message = f"Invalid postal code '{value}': {reason}"
        else:
            message = f"Invalid postal code: '{value}'"
        super().__init__(message)
