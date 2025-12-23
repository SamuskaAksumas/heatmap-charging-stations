"""
Domain services for community engagement bounded context.
"""
from typing import List, Optional
from domain.community_engagement.entities import ChargingSuggestion, SuggestionStatus
from domain.community_engagement.repository import SuggestionRepository


class CommunityEngagementService:
    """Domain service for community engagement operations."""

    def __init__(self, repository: SuggestionRepository):
        self.repository = repository

    def submit_suggestion(self, suggestion: ChargingSuggestion) -> None:
        """Submit a new suggestion."""
        self.repository.save(suggestion)

    def get_suggestion_by_id(self, suggestion_id: int) -> Optional[ChargingSuggestion]:
        """Get a suggestion by ID."""
        return self.repository.get_by_id(suggestion_id)

    def get_all_suggestions(self) -> List[ChargingSuggestion]:
        """Get all suggestions."""
        return self.repository.get_all()

    def get_pending_suggestions(self) -> List[ChargingSuggestion]:
        """Get all pending suggestions."""
        return self.repository.get_pending_suggestions()

    def get_approved_suggestions(self) -> List[ChargingSuggestion]:
        """Get all approved suggestions."""
        return self.repository.get_approved_suggestions()

    def get_rejected_suggestions(self) -> List[ChargingSuggestion]:
        """Get all rejected suggestions."""
        return self.repository.get_rejected_suggestions()

    def update_suggestion(self, suggestion: ChargingSuggestion) -> None:
        """Update an existing suggestion."""
        self.repository.update(suggestion)

    def get_suggestions_by_postal_code(self, postal_code: str) -> List[ChargingSuggestion]:
        """Get all suggestions for a specific postal code."""
        return self.repository.get_by_postal_code(postal_code)