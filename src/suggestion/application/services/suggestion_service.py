"""
Application Service: SuggestionService

Coordinates suggestion management workflow between domain logic and infrastructure.
"""
from typing import List, Dict, Any

from src.suggestion.domain.entities.suggestion import ChargingSuggestion
from src.suggestion.domain.events.suggestion_handled import save_suggestion
from src.suggestion.infrastructure.repositories.suggestion_repository import SuggestionRepository
from src.suggestion.domain.events.load_suggestion import load_suggestions
from src.suggestion.domain.events.review_suggestion import review_suggestion


class SuggestionService:
    """
    Application service for managing charging station suggestions.

    Coordinates CRUD operations for suggestions, following DDD patterns
    by delegating business logic to domain events.
    """

    def __init__(self, repository: SuggestionRepository) -> None:
        """
        Initialize the SuggestionService.

        Args:
            repository: Repository for persisting suggestions
        """
        self._repository = repository

    def get_all_suggestions(self) -> List[Dict[str, Any]]:
        """
        Retrieve all visible suggestions.

        Filters out deleted suggestions using the domain event.

        Returns:
            List of suggestion dictionaries (excluding deleted ones)
        """
        # 1. Call infrastructure layer
        raw_list = self._repository.fetch_raw_data()

        # 2. Apply domain logic (filter deleted)
        processed_list = load_suggestions(raw_list)

        return processed_list

    def create_suggestion(
        self,
        plz: str,
        address: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Create a new charging station suggestion.

        Args:
            plz: Postal code for the suggestion
            address: Street address for the suggested location
            reason: Reason why a charging station is needed here

        Returns:
            Dictionary containing the created suggestion with id and timestamp
        """
        # 1. Create entity
        suggestion = ChargingSuggestion(plz, address, reason)
        suggestion_dict = suggestion.__dict__

        # 2. Apply domain logic (set id, timestamp, status)
        current_data = self._repository.fetch_raw_data()
        processed_data = save_suggestion(suggestion_dict, len(current_data))

        # 3. Persist via repository
        self._repository.add(processed_data)

        return processed_data

    def review_suggestion(
        self,
        suggestion_id: int,
        status: str,
        reviewer: str = "Admin",
        notes: str = ""
    ) -> None:
        """
        Review (approve/reject) a suggestion.

        Args:
            suggestion_id: ID of the suggestion to review
            status: New status ('approved', 'rejected', 'deleted')
            reviewer: Name of the reviewer
            notes: Optional review notes
        """
        # 1. Fetch current data
        all_suggestions = self._repository.fetch_raw_data()

        # 2. Find and update using domain event
        for suggestion in all_suggestions:
            if suggestion.get('id') == suggestion_id:
                review_suggestion(suggestion, status, reviewer, notes)
                break

        # 3. Persist updated list
        self._repository.save(all_suggestions)
