from dataclasses import dataclass
from src.suggestion.domain.exceptions import InvalidSuggestionException

@dataclass(frozen=True)
class SuggestionContent:
    """Value Object: Ensures the text content of a suggestion is valid."""
    address: str
    reason: str

    def __post_init__(self):
        if not self.address or not self.address.strip():
            raise InvalidSuggestionException("Address cannot be empty")
        if not self.reason or not self.reason.strip():
            raise InvalidSuggestionException("Reason cannot be empty")