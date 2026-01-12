"""ChargingSuggestion Entity - Rich domain model with State Machine."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.suggestion.domain.exceptions import InvalidSuggestionException
from src.shared.domain.value_objects.postal_code import PostalCode


VALID_STATUS_TRANSITIONS = {
    'pending': ['approved', 'rejected', 'deleted'],
    'approved': ['deleted'],
    'rejected': ['deleted'],
    'deleted': [],
}


@dataclass
class ChargingSuggestion:
    """
    Suggestion for a new charging station location.

    State Machine: pending → approved/rejected → deleted
    Validates PLZ via PostalCode Value Object.
    """
    plz: str
    address: str
    reason: str
    id: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = 'pending'
    reviewed_by: Optional[str] = None
    review_date: Optional[str] = None
    review_notes: Optional[str] = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate all fields according to domain rules."""
        # Validate PLZ using PostalCode Value Object
        try:
            PostalCode(self.plz.strip() if self.plz else "")
        except ValueError as e:
            raise InvalidSuggestionException(str(e), field="plz")

        # Validate address
        if not self.address or not self.address.strip():
            raise InvalidSuggestionException("Address cannot be empty", field="address")

        # Validate reason
        if not self.reason or not self.reason.strip():
            raise InvalidSuggestionException("Reason cannot be empty", field="reason")

        # Validate status
        valid_statuses = ['pending', 'approved', 'rejected', 'deleted']
        if self.status not in valid_statuses:
            raise InvalidSuggestionException(
                f"Invalid status '{self.status}'. Must be one of: {valid_statuses}",
                field="status"
            )

    def is_pending(self) -> bool:
        return self.status == 'pending'

    def is_approved(self) -> bool:
        return self.status == 'approved'

    def is_rejected(self) -> bool:
        return self.status == 'rejected'

    def is_deleted(self) -> bool:
        return self.status == 'deleted'

    def can_transition_to(self, new_status: str) -> bool:
        """Check if status transition is valid per State Machine rules."""
        return new_status in VALID_STATUS_TRANSITIONS.get(self.status, [])

    def _transition_status(self, new_status: str, reviewer: str, notes: str = None) -> None:
        """Execute status transition with validation."""
        if not self.can_transition_to(new_status):
            raise InvalidSuggestionException(
                f"Cannot transition from '{self.status}' to '{new_status}'"
            )

        self.status = new_status
        self.reviewed_by = reviewer
        self.review_date = datetime.now().isoformat()
        if notes:
            self.review_notes = notes

    def approve(self, reviewer: str, notes: str = None) -> None:
        """Approve this suggestion (pending → approved)."""
        self._transition_status('approved', reviewer, notes)

    def reject(self, reviewer: str, notes: str = None) -> None:
        """Reject this suggestion (pending → rejected)."""
        self._transition_status('rejected', reviewer, notes)

    def delete(self, reviewer: str = None, notes: str = None) -> None:
        """Mark as deleted (terminal state)."""
        self._transition_status('deleted', reviewer or 'System', notes)

    def to_dict(self) -> dict:
        """Convert to dictionary for persistence."""
        return {
            'id': self.id,
            'plz': self.plz,
            'address': self.address,
            'reason': self.reason,
            'timestamp': self.timestamp,
            'status': self.status,
            'reviewed_by': self.reviewed_by,
            'review_date': self.review_date,
            'review_notes': self.review_notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChargingSuggestion":
        """Create entity from dictionary (e.g., from JSON storage)."""
        return cls(
            plz=data.get('plz', ''),
            address=data.get('address', ''),
            reason=data.get('reason', ''),
            id=data.get('id'),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            status=data.get('status', 'pending'),
            reviewed_by=data.get('reviewed_by'),
            review_date=data.get('review_date'),
            review_notes=data.get('review_notes'),
        )
