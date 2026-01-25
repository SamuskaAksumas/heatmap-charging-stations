from typing import List, Dict, Any

from src.suggestion.domain.entities.suggestion_entity import SuggestionEntity
from src.suggestion.domain.aggregates.suggestion_aggregate import SuggestionAggregate
from src.suggestion.domain.events.review_suggestion import ReviewSuggestion
from src.suggestion.infrastructure.repositories.suggestion_repository import SuggestionRepository


class SuggestionService:
    """
    Application Service.
    Coordinates use cases, delegates business rules to the Aggregate Root.
    """

    def __init__(self, repository: SuggestionRepository):
        self._repository = repository

    def create_suggestion(self, plz: str, address: str, reason: str) -> int:
        """
        Use case: User creates a new suggestion.
        """
        # 1. Create Entity (no business rules here)
        entity = SuggestionEntity(
            plz=plz,
            address=address,
            reason=reason
        )

        # 2. Create Aggregate Root
        aggregate = SuggestionAggregate(entity)

        # 3. Persist Aggregate
        saved_aggregate = self._repository.save(aggregate)

        return saved_aggregate.id

    def review_suggestion(
        self,
        suggestion_id: int,
        status: str,
        reviewer: str,
        notes: str | None = None
    ) -> bool:
        """
        Use case: Admin reviews a suggestion.
        """
        # 1. Load Aggregate Root
        aggregate = self._repository.get_by_id(suggestion_id)
        if aggregate is None:
            return False

        # 2. Domain Logic (inside Aggregate!)
        aggregate.apply_review(status, reviewer, notes)

        # 3. Persist updated Aggregate
        self._repository.save(aggregate)

        # 4. Domain Event (side effect)
        ReviewSuggestion(
            suggestion_id=suggestion_id,
            status=status,
            reviewer=reviewer
        )

        return True

    def get_all_suggestions(self) -> List[Dict[str, Any]]:
        """
        Admin view: returns all non-deleted suggestions.
        """
        aggregates = self._repository.get_all_including_deleted()

        return [
            aggregate.to_dict()
            for aggregate in aggregates
            if aggregate.entity.status != "deleted"
        ]

    def get_suggestions_for_users(self) -> List[Dict[str, Any]]:
        """
        User view: returns only pending and approved suggestions.
        """
        aggregates = self._repository.get_all_including_deleted()
        allowed_statuses = {"pending", "approved"}

        return [
            aggregate.to_dict()
            for aggregate in aggregates
            if aggregate.entity.status in allowed_statuses
        ]
