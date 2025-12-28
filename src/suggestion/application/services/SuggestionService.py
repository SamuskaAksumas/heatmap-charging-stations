# src/community/application/services/suggestion_service.py

from src.suggestion.domain.entities.suggestion import ChargingSuggestion
from src.suggestion.domain.events.suggestion_handled import save_suggestion
from src.suggestion.infrastructure.repositories.suggestion_repository import SuggestionRepository
from src.suggestion.domain.events.load_suggestion import load_suggestions
from src.suggestion.domain.events.review_suggestion import review_suggestion

class SuggestionService:
    def __init__(self, repository: SuggestionRepository):
        self._repository = repository

    def get_all_suggestions(self):
        # 1. CALL INFRASTRUCTURE (The 'get_all' equivalent)
        raw_list = self._repository.fetch_raw_data()

        # 2. CALL DOMAIN EVENT (The processing logic)
        processed_list = load_suggestions(raw_list)

        return processed_list

    def create_suggestion(self, plz, address, reason):
        # 1. Create the Entity object
        suggestion = ChargingSuggestion(plz, address, reason)
        suggestion_dict = suggestion.__dict__
        # 2. CALL THE EVENT: Run business logic to get the formatted dict
        current_data = self._repository.fetch_raw_data()
        processed_data = save_suggestion(suggestion_dict, len(current_data))
        # 3. CALL THE REPOSITORY: Save the data to the JSON file
        self._repository.add(processed_data)
        
        return processed_data
    
    def review_suggestion(self, suggestion_id, status, reviewer="Admin", notes=""):
        # 1. FETCH: Get the current list from Infrastructure
        all_suggestions = self._repository.fetch_raw_data()
        
        # 2. PROCESS: Find and update using the Domain Event
        for suggestion in all_suggestions:
            if suggestion.get('id') == suggestion_id:
                # Call the event function we just created
                review_suggestion(suggestion, status, reviewer, notes)
                break
        
        # 3. PERSIST: Save the updated list back to Infrastructure
        self._repository.save(all_suggestions)
