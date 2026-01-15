"""InvalidSuggestionException - Raised for invalid suggestion data or transitions."""
from src.shared.domain.exceptions import DomainException


class InvalidSuggestionException(DomainException):
    """Raised for invalid PLZ, empty fields, or invalid status transitions."""

    def __init__(self, message: str):
        super().__init__(message)
