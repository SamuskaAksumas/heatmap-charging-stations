"""SuggestionRepository - JSON file persistence for suggestions."""
import json
import os
from datetime import datetime


class SuggestionRepository:
    """Repository for suggestions using JSON file storage."""

    def __init__(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        self.file_path = os.path.join(base_path, "data", "suggestions.json")
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def get_all(self) -> list:
        """Get all visible suggestions (excludes deleted) - for admin view."""
        return [s for s in self._fetch_raw_data() if s.get('status') != 'deleted']

    def get_visible_for_users(self) -> list:
        """Get suggestions visible to users (pending + approved only)."""
        return [s for s in self._fetch_raw_data() if s.get('status') in ['pending', 'approved']]

    def get_all_including_deleted(self) -> list:
        """Get all suggestions including deleted (for admin/review)."""
        return self._fetch_raw_data()

    def add(self, suggestion_dict: dict) -> dict:
        """Add new suggestion with ID, timestamp, and initial status."""
        suggestions = self._fetch_raw_data()

        # Assign persistence metadata
        suggestion_dict['id'] = len(suggestions) + 1
        suggestion_dict['timestamp'] = datetime.now().isoformat()
        suggestion_dict['status'] = 'pending'
        suggestion_dict['reviewed_by'] = None
        suggestion_dict['review_date'] = None
        suggestion_dict['review_notes'] = None

        suggestions.append(suggestion_dict)
        self._save(suggestions)
        return suggestion_dict

    def update(self, suggestions_list: list):
        """Overwrite all suggestions (after review updates)."""
        self._save(suggestions_list)

    def _fetch_raw_data(self) -> list:
        """Internal: Read all suggestions from file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save(self, suggestions_list: list):
        """Internal: Write suggestions to file."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(suggestions_list, f, indent=2, ensure_ascii=False)