"""InvalidSuggestionException - Raised for invalid suggestion data or transitions."""
from src.shared.domain.exceptions import DomainException


class InvalidSuggestionException(DomainException):
    """Raised for invalid PLZ, empty fields, or invalid status transitions."""

    def __init__(self, message: str, field: str = None):
        self.field = field
        if field:
            super().__init__(f"Invalid suggestion field '{field}': {message}")
        else:
            super().__init__(f"Invalid suggestion: {message}")
