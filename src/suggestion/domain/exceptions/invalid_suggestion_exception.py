"""Exception for invalid suggestion data."""
from src.shared.domain.exceptions import DomainException


class InvalidSuggestionException(DomainException):
    """
    Raised when a suggestion contains invalid data.

    This exception is thrown when:
    - Required fields (PLZ, address, reason) are missing or empty
    - The PLZ format is invalid
    - The status transition is not allowed

    Attributes:
        field: The name of the invalid field (optional).
        message: Human-readable error description.
    """

    def __init__(self, message: str, field: str = None):
        self.field = field
        if field:
            super().__init__(f"Invalid suggestion field '{field}': {message}")
        else:
            super().__init__(f"Invalid suggestion: {message}")
