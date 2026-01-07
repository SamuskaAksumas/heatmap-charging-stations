"""
Event: SuggestionCreatedEvent

Raised when a new charging station suggestion is created by a user.
"""
from dataclasses import dataclass, field

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class SuggestionCreatedEvent(DomainEvent):
    """
    Event raised when a new suggestion is created.

    This event captures all relevant information about a new suggestion
    for potential subscribers (e.g., notification systems, analytics).

    Attributes:
        suggestion_id: The unique ID assigned to the suggestion.
        plz: The postal code where the suggestion was made.
        address: The suggested address/location.
        reason: Why the user suggested this location.

    Example:
        >>> event = SuggestionCreatedEvent(
        ...     suggestion_id=1,
        ...     plz="10115",
        ...     address="Torstrasse 1",
        ...     reason="High demand area"
        ... )
    """
    suggestion_id: int = 0
    plz: str = ""
    address: str = ""
    reason: str = ""

    def to_dict(self) -> dict:
        """
        Convert event to dictionary for serialization.

        Returns:
            Dictionary representation of the event.
        """
        base = super().to_dict()
        base.update({
            'suggestion_id': self.suggestion_id,
            'plz': self.plz,
            'address': self.address,
            'reason': self.reason,
        })
        return base
