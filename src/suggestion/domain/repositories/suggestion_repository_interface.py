"""
Repository Interface for Suggestions.

Defines the contract for suggestion persistence operations,
following the Repository Pattern for dependency inversion.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.suggestion.domain.entities.suggestion import ChargingSuggestion


class SuggestionRepositoryInterface(ABC):
    """
    Abstract repository interface for ChargingSuggestion entities.

    This interface defines all operations required for managing suggestions,
    allowing different implementations (JSON file, database, in-memory, etc.)
    to be swapped without changing the domain or application layers.

    Implementing classes must provide concrete implementations for all methods.

    Example:
        >>> class JsonSuggestionRepository(SuggestionRepositoryInterface):
        ...     def get_by_id(self, id: int) -> Optional[ChargingSuggestion]:
        ...         # Load from JSON and find by id
        ...         pass
    """

    @abstractmethod
    def get_by_id(self, suggestion_id: int) -> Optional[ChargingSuggestion]:
        """
        Retrieve a suggestion by its unique identifier.

        Args:
            suggestion_id: The unique identifier of the suggestion.

        Returns:
            The ChargingSuggestion if found, None otherwise.
        """
        pass

    @abstractmethod
    def get_all(self, include_deleted: bool = False) -> List[ChargingSuggestion]:
        """
        Retrieve all suggestions.

        Args:
            include_deleted: If True, include deleted suggestions.

        Returns:
            List of all suggestions (filtered by include_deleted).
        """
        pass

    @abstractmethod
    def get_by_plz(self, plz: str) -> List[ChargingSuggestion]:
        """
        Retrieve all suggestions for a specific postal code.

        Args:
            plz: The postal code to filter by.

        Returns:
            List of suggestions for the given PLZ.
        """
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[ChargingSuggestion]:
        """
        Retrieve all suggestions with a specific status.

        Args:
            status: The status to filter by ('pending', 'approved', 'rejected').

        Returns:
            List of suggestions with the given status.
        """
        pass

    @abstractmethod
    def save(self, suggestion: ChargingSuggestion) -> ChargingSuggestion:
        """
        Persist a suggestion (create or update).

        If the suggestion has no ID, a new ID will be assigned.
        If the suggestion has an ID, it will be updated.

        Args:
            suggestion: The suggestion to persist.

        Returns:
            The persisted suggestion with assigned ID.
        """
        pass

    @abstractmethod
    def delete(self, suggestion_id: int) -> bool:
        """
        Soft-delete a suggestion by marking its status as 'deleted'.

        Args:
            suggestion_id: The ID of the suggestion to delete.

        Returns:
            True if the suggestion was deleted, False if not found.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get the total count of non-deleted suggestions.

        Returns:
            Number of suggestions (excluding deleted).
        """
        pass
