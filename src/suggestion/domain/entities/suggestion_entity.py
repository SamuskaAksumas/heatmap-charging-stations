from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.shared.domain.entities.entity import Entity
from src.shared.domain.value_objects.postal_code import PostalCode
from src.suggestion.domain.exceptions.invalid_suggestion_exception import (
    InvalidSuggestionException,
)


@dataclass(eq=False)
class SuggestionEntity(Entity):
    """
    Entity representing a charging station suggestion.

    - Has identity (id)
    - Does NOT contain state machine logic
    - Invariants are validated on creation
    """

    plz: str
    address: str
    reason: str
    id: Optional[int] = None
    status: str = "pending"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reviewed_by: Optional[str] = None
    review_date: Optional[str] = None
    review_notes: Optional[str] = None

    def __post_init__(self) -> None:
        # Initialize Entity identity
        super().__init__(entity_id=str(self.id) if self.id is not None else "new")

        # Invariant checks (NOT workflow logic)
        self._validate()

    def _validate(self) -> None:
        """
        Validate entity invariants.
        """
        # Validate PLZ via Value Object
        try:
            PostalCode(self.plz)
        except ValueError as e:
            raise InvalidSuggestionException(str(e))

        if not self.address or not self.address.strip():
            raise InvalidSuggestionException("Address must not be empty")

        if not self.reason or not self.reason.strip():
            raise InvalidSuggestionException("Reason must not be empty")

        if self.status not in {"pending", "approved", "rejected", "deleted"}:
            raise InvalidSuggestionException(f"Invalid status '{self.status}'")
