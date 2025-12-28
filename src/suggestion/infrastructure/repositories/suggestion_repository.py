# src/suggestion/infrastructure/repositories/suggestion_repository.py
import json
import os
from src.suggestion.domain.entities.suggestion import ChargingSuggestion

class SuggestionRepository:
    def __init__(self):
        # We define the path relative to this file's location
        base_path = os.path.dirname(os.path.dirname(__file__)) # goes to infrastructure/
        self.file_path = os.path.join(base_path, "data", "suggestions.json")
        
        # Ensure the data folder exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def fetch_raw_data(self) -> list: # all suggestions
        """Technical task: Just read the file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def add(self, suggestion_dict: dict): # new suggestion
        suggestions = self.fetch_raw_data()
        suggestions.append(suggestion_dict)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, indent=2, ensure_ascii=False)

    def save(self, suggestions_list): #edit by admin
        """Technical task: Persist the entire list to the JSON file."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(suggestions_list, f, indent=2, ensure_ascii=False)