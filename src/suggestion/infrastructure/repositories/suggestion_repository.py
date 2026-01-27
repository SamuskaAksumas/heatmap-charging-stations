import json
import os
from typing import List, Optional
from src.suggestion.domain.entities.suggestion_entity import SuggestionEntity
from src.suggestion.domain.aggregates.suggestion_aggregate import SuggestionAggregate

class SuggestionRepository:
    def __init__(self, file_path: str = "src/suggestion/infrastructure/data/suggestions.json"):
        self.file_path = file_path
        # Ensure the directory exists so open() doesn't fail
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def _load_json(self) -> List[dict]:
        """Private helper to read the JSON file safely."""
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_json(self, data: List[dict]):
        """Private helper to write data back to the JSON file."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def get_by_id(self, suggestion_id: int) -> Optional[SuggestionAggregate]:
        """
        Fetches a specific suggestion and rehydrates it into an Aggregate.
        This is what the SuggestionService needs to apply reviews.
        """
        all_data = self._load_json()
        for item in all_data:
            if item.get('id') == suggestion_id:
                # Reconstruct the Domain Model from raw Data
                entity = SuggestionEntity(**item)
                return SuggestionAggregate(entity)
        return None

    def get_all_including_deleted(self) -> List[SuggestionAggregate]:
        """Rehydrates all entries into Domain Aggregates."""
        raw_data = self._load_json()
        return [SuggestionAggregate(SuggestionEntity(**item)) for item in raw_data]

    def save(self, aggregate: SuggestionAggregate):
        """Saves a new suggestion or updates an existing one."""
        all_data = self._load_json()
        new_data = aggregate.to_dict()

        # Handle ID assignment for new suggestions if not already set
        if new_data.get('id') is None:
            max_id = max([item.get('id', 0) for item in all_data], default=0)
            new_data['id'] = max_id + 1
            # Update the entity inside the aggregate so the caller knows the ID
            aggregate.entity.id = new_data['id']

        found = False
        for i, item in enumerate(all_data):
            if item.get('id') == new_data['id']:
                all_data[i] = new_data
                found = True
                break
        
        if not found:
            all_data.append(new_data)
            
        self._save_json(all_data)
        return aggregate
