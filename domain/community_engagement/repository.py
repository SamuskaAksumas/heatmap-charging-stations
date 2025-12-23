"""
Repository interfaces for community engagement domain.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import ChargingSuggestion, SuggestionStatus


class SuggestionRepository(ABC):
    """Abstract repository for suggestion data access."""

    @abstractmethod
    def save(self, suggestion: ChargingSuggestion) -> None:
        """Save a suggestion."""
        pass

    @abstractmethod
    def get_all(self) -> List[ChargingSuggestion]:
        """Get all suggestions."""
        pass

    @abstractmethod
    def get_by_id(self, suggestion_id: int) -> Optional[ChargingSuggestion]:
        """Get a suggestion by ID."""
        pass

    @abstractmethod
    def get_by_postal_code(self, postal_code: str) -> List[ChargingSuggestion]:
        """Get suggestions by postal code."""
        pass

    @abstractmethod
    def get_by_status(self, status: SuggestionStatus) -> List[ChargingSuggestion]:
        """Get suggestions by status."""
        pass

    @abstractmethod
    def update(self, suggestion: ChargingSuggestion) -> None:
        """Update an existing suggestion."""
        pass

    @abstractmethod
    def get_pending_suggestions(self) -> List[ChargingSuggestion]:
        """Get all pending suggestions."""
        pass

    @abstractmethod
    def get_approved_suggestions(self) -> List[ChargingSuggestion]:
        """Get all approved suggestions."""
        pass