from datetime import datetime

from src.shared.domain.aggregate_root import AggregateRoot
from src.suggestion.domain.entities.suggestion_entity import SuggestionEntity
from src.suggestion.domain.exceptions.invalid_suggestion_exception import (
    InvalidSuggestionException,
)


class SuggestionAggregate(AggregateRoot):
    """
    Aggregate Root for the Suggestion Bounded Context.

    Responsible for:
    - Enforcing invariants
    - Managing the state machine
    - Protecting the SuggestionEntity lifecycle
    """

    def __init__(self, entity: SuggestionEntity):
        super().__init__(aggregate_id=str(entity.id))
        self.entity = entity

    def apply_review(self, status: str, reviewer: str, notes: str | None = None) -> None:
        """
        Domain Logic: Enforce business rules for status transitions.
        This is the single place where the state machine lives.
        """

        current_status = self.entity.status

        # Rule 0: Terminal state protection
        if current_status == "deleted":
            raise InvalidSuggestionException(
                f"Cannot modify suggestion {self.entity.id}; it is already deleted."
            )

        # Rule 1: Approved suggestions are immutable (except delete)
        if current_status == "approved" and status in {"approved", "rejected"}:
            raise InvalidSuggestionException(
                f"Transition from '{current_status}' to '{status}' is not allowed."
            )

        # Rule 2: Rejected suggestions can only be deleted
        if current_status == "rejected" and status != "deleted":
            raise InvalidSuggestionException(
                f"Cannot transition from '{current_status}' to '{status}'."
            )

        # Rule 3: Pending suggestions can only be approved or rejected
        if current_status == "pending" and status not in {"approved", "rejected"}:
            raise InvalidSuggestionException(
                f"Invalid transition from '{current_status}' to '{status}'."
            )

        # Apply transition
        self._apply_state_change(status, reviewer, notes)

    def _apply_state_change(
        self, status: str, reviewer: str, notes: str | None
    ) -> None:
        """
        Internal state mutation after validation.
        """
        self.entity.status = status
        self.entity.reviewed_by = reviewer
        self.entity.review_notes = notes
        self.entity.review_date = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """
        Converts the Aggregate to a primitive structure
        for persistence or presentation layers.
        """
        return {
            "id": self.entity.id,
            "plz": self.entity.plz,
            "address": self.entity.address,
            "reason": self.entity.reason,
            "status": self.entity.status,
            "timestamp": self.entity.timestamp,
            "reviewed_by": self.entity.reviewed_by,
            "review_date": self.entity.review_date,
            "review_notes": self.entity.review_notes,
        }
