"""
Domain entities and value objects for community engagement.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class SuggestionStatus(Enum):
    """Enumeration of possible suggestion statuses."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ReviewInfo:
    """Value object representing review information."""
    reviewer: str
    review_date: datetime
    notes: Optional[str] = None


@dataclass
class ChargingSuggestion:
    """Entity representing a community suggestion for a charging location."""
    id: int
    postal_code: str
    address: str
    reason: str
    submitted_at: datetime
    status: SuggestionStatus = SuggestionStatus.PENDING
    review_info: Optional[ReviewInfo] = None

    def __post_init__(self):
        if not self.postal_code:
            raise ValueError("Postal code cannot be empty")
        if not self.address:
            raise ValueError("Address cannot be empty")
        if not self.reason:
            raise ValueError("Reason cannot be empty")

    def approve(self, reviewer: str, notes: Optional[str] = None) -> None:
        """Approve this suggestion."""
        self.status = SuggestionStatus.APPROVED
        self.review_info = ReviewInfo(
            reviewer=reviewer,
            review_date=datetime.now(),
            notes=notes
        )

    def reject(self, reviewer: str, notes: Optional[str] = None) -> None:
        """Reject this suggestion."""
        self.status = SuggestionStatus.REJECTED
        self.review_info = ReviewInfo(
            reviewer=reviewer,
            review_date=datetime.now(),
            notes=notes
        )

    def is_pending(self) -> bool:
        """Check if suggestion is still pending review."""
        return self.status == SuggestionStatus.PENDING

    def is_approved(self) -> bool:
        """Check if suggestion has been approved."""
        return self.status == SuggestionStatus.APPROVED

    def is_rejected(self) -> bool:
        """Check if suggestion has been rejected."""
        return self.status == SuggestionStatus.REJECTED