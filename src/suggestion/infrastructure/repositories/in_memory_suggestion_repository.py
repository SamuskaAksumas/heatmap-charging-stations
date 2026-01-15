"""InMemorySuggestionRepository - In-memory storage for testing."""
from datetime import datetime
from typing import List, Dict, Any


class InMemorySuggestionRepository:
    """In-memory repository for suggestions (no file I/O, used in tests)."""

    def __init__(self) -> None:
        self._data: List[Dict[str, Any]] = []

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all visible suggestions (excludes deleted) - for admin view."""
        return [s for s in self._data if s.get('status') != 'deleted']

    def get_visible_for_users(self) -> List[Dict[str, Any]]:
        """Get suggestions visible to users (pending + approved only)."""
        return [s for s in self._data if s.get('status') in ['pending', 'approved']]

    def get_all_including_deleted(self) -> List[Dict[str, Any]]:
        """Get all suggestions including deleted."""
        return self._data

    def add(self, suggestion_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Add new suggestion with ID, timestamp, and initial status."""
        suggestion_dict['id'] = len(self._data) + 1
        suggestion_dict['timestamp'] = datetime.now().isoformat()
        suggestion_dict['status'] = 'pending'
        suggestion_dict['reviewed_by'] = None
        suggestion_dict['review_date'] = None
        suggestion_dict['review_notes'] = None
        self._data.append(suggestion_dict)
        return suggestion_dict

    def update(self, suggestions_list: List[Dict[str, Any]]) -> None:
        """Replace all data with new list."""
        self._data = suggestions_list
