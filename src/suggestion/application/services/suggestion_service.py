"""SuggestionService - Coordinates suggestion management workflow."""
from typing import List, Dict, Any

from src.suggestion.domain.entities.suggestion import ChargingSuggestion
from src.suggestion.infrastructure.repositories.suggestion_repository import SuggestionRepository


class SuggestionService:
    """Application service for managing charging station suggestions."""

    def __init__(self, repository: SuggestionRepository) -> None:
        self._repository = repository

    def get_all_suggestions(self) -> List[Dict[str, Any]]:
        """Retrieve all visible suggestions (excludes deleted)."""
        return self._repository.get_all()

    def create_suggestion(self, plz: str, address: str, reason: str) -> Dict[str, Any]:
        """Create a new suggestion (validates via Entity, persists via Repository)."""
        suggestion = ChargingSuggestion(plz, address, reason)
        return self._repository.add(suggestion.to_dict())

    def review_suggestion(
        self,
        suggestion_id: int,
        status: str,
        reviewer: str = "Admin",
        notes: str = ""
    ) -> None:
        """Review suggestion using Entity's state machine (approve/reject/delete)."""
        all_suggestions = self._repository.get_all_including_deleted()

        for i, suggestion_data in enumerate(all_suggestions):
            if suggestion_data.get('id') == suggestion_id:
                entity = ChargingSuggestion.from_dict(suggestion_data)

                if status == 'approved':
                    entity.approve(reviewer, notes)
                elif status == 'rejected':
                    entity.reject(reviewer, notes)
                elif status == 'deleted':
                    entity.delete(reviewer, notes)

                all_suggestions[i] = entity.to_dict()
                break

        self._repository.update(all_suggestions)
