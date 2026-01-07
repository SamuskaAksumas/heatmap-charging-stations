"""
Entity: ChargingSuggestion

Rich domain entity representing a user suggestion for a new charging station location.
Contains validation and business logic following DDD principles.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.suggestion.domain.exceptions import InvalidSuggestionException


# Valid status transitions
VALID_STATUS_TRANSITIONS = {
    'pending': ['approved', 'rejected', 'deleted'],
    'approved': ['deleted'],
    'rejected': ['deleted'],
    'deleted': [],  # Terminal state
}


@dataclass
class ChargingSuggestion:
    """
    Rich Entity representing a charging station location suggestion.

    This entity includes validation and business logic, following DDD principles
    where entities are not just data containers but encapsulate domain rules.

    Attributes:
        plz: Postal code (PLZ) for the suggested location (Berlin range)
        address: Street address for the suggestion (non-empty)
        reason: User's reason for suggesting this location (non-empty)
        id: Unique identifier (assigned by domain event)
        timestamp: Creation timestamp (ISO format)
        status: Current status ('pending', 'approved', 'rejected', 'deleted')

    Domain Rules:
        - PLZ must be a valid Berlin postal code (10000-14200)
        - Address and reason cannot be empty
        - Status can only transition through valid paths
        - New suggestions always start as 'pending'

    Example:
        >>> suggestion = ChargingSuggestion("10115", "Torstrasse 1", "High foot traffic")
        >>> suggestion.approve("Admin")
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
        """Validate the suggestion upon creation."""
        self._validate()

    def _validate(self) -> None:
        """
        Validate all fields according to domain rules.

        Raises:
            InvalidSuggestionException: If any validation fails.
        """
        # Validate PLZ
        if not self.plz or not self.plz.strip():
            raise InvalidSuggestionException("PLZ cannot be empty", field="plz")

        try:
            plz_int = int(self.plz.strip())
            if not (10000 <= plz_int <= 14200):
                raise InvalidSuggestionException(
                    f"PLZ must be in Berlin range (10000-14200), got {plz_int}",
                    field="plz"
                )
        except ValueError:
            raise InvalidSuggestionException(
                f"PLZ must be numeric, got '{self.plz}'",
                field="plz"
            )

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
        """Check if the suggestion is pending review."""
        return self.status == 'pending'

    def is_approved(self) -> bool:
        """Check if the suggestion has been approved."""
        return self.status == 'approved'

    def is_rejected(self) -> bool:
        """Check if the suggestion has been rejected."""
        return self.status == 'rejected'

    def is_deleted(self) -> bool:
        """Check if the suggestion has been deleted."""
        return self.status == 'deleted'

    def can_transition_to(self, new_status: str) -> bool:
        """
        Check if a status transition is valid.

        Args:
            new_status: The target status.

        Returns:
            True if the transition is allowed.
        """
        return new_status in VALID_STATUS_TRANSITIONS.get(self.status, [])

    def _transition_status(self, new_status: str, reviewer: str, notes: str = None) -> None:
        """
        Internal method to transition status with validation.

        Args:
            new_status: The target status.
            reviewer: Name of the reviewer.
            notes: Optional review notes.

        Raises:
            InvalidSuggestionException: If the transition is not allowed.
        """
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
        """
        Approve this suggestion.

        Args:
            reviewer: Name of the admin approving.
            notes: Optional approval notes.

        Raises:
            InvalidSuggestionException: If suggestion cannot be approved.
        """
        self._transition_status('approved', reviewer, notes)

    def reject(self, reviewer: str, notes: str = None) -> None:
        """
        Reject this suggestion.

        Args:
            reviewer: Name of the admin rejecting.
            notes: Optional rejection notes.

        Raises:
            InvalidSuggestionException: If suggestion cannot be rejected.
        """
        self._transition_status('rejected', reviewer, notes)

    def delete(self, reviewer: str = None, notes: str = None) -> None:
        """
        Mark this suggestion as deleted.

        Args:
            reviewer: Name of the admin deleting (optional).
            notes: Optional deletion notes.

        Raises:
            InvalidSuggestionException: If suggestion cannot be deleted.
        """
        self._transition_status('deleted', reviewer or 'System', notes)

    def to_dict(self) -> dict:
        """
        Convert entity to dictionary for persistence.

        Returns:
            Dictionary representation of the suggestion.
        """
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
        """
        Create entity from dictionary.

        Args:
            data: Dictionary with suggestion data.

        Returns:
            ChargingSuggestion instance.
        """
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
