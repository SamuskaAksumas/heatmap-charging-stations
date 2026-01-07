"""
Repository: InMemorySuggestionRepository

In-memory implementation for testing purposes.
"""
from typing import List, Dict, Any


class InMemorySuggestionRepository:
    """
    In-memory repository for suggestions (used in tests).

    This implementation stores data in RAM without persistence,
    making it ideal for unit testing without file I/O.
    """

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._data: List[Dict[str, Any]] = []

    def fetch_raw_data(self) -> List[Dict[str, Any]]:
        """
        Retrieve all stored suggestions.

        Returns:
            List of suggestion dictionaries
        """
        return self._data

    def add(self, suggestion_dict: Dict[str, Any]) -> None:
        """
        Add a new suggestion to storage.

        Args:
            suggestion_dict: Suggestion data to store
        """
        self._data.append(suggestion_dict)

    def save(self, suggestions_list: List[Dict[str, Any]]) -> None:
        """
        Replace all suggestions with a new list.

        Args:
            suggestions_list: Complete list of suggestions
        """
        self._data = suggestions_list