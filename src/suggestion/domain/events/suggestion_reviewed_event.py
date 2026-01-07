"""
Event: SuggestionReviewedEvent

Raised when a suggestion is reviewed (approved or rejected) by an admin.
"""
from dataclasses import dataclass, field

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class SuggestionReviewedEvent(DomainEvent):
    """
    Event raised when a suggestion is reviewed.

    This event captures the review action taken on a suggestion,
    including who reviewed it and what decision was made.

    Attributes:
        suggestion_id: The ID of the suggestion that was reviewed.
        new_status: The status after review ('approved', 'rejected', 'deleted').
        reviewer: Name of the person who reviewed the suggestion.
        notes: Optional review notes.

    Example:
        >>> event = SuggestionReviewedEvent(
        ...     suggestion_id=1,
        ...     new_status="approved",
        ...     reviewer="Admin",
        ...     notes="Good location, approved."
        ... )
    """
    suggestion_id: int = 0
    new_status: str = ""
    reviewer: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        """
        Convert event to dictionary for serialization.

        Returns:
            Dictionary representation of the event.
        """
        base = super().to_dict()
        base.update({
            'suggestion_id': self.suggestion_id,
            'new_status': self.new_status,
            'reviewer': self.reviewer,
            'notes': self.notes,
        })
        return base
