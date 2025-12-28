import pytest
from src.suggestion.application.services.SuggestionService import SuggestionService
from src.suggestion.infrastructure.repositories.in_memory_suggestion_repository import InMemorySuggestionRepository

@pytest.fixture
def suggestion_setup():
    """Fixture to provide a clean service and in-memory repo for every test."""
    repo = InMemorySuggestionRepository()
    service = SuggestionService(repo)
    return service, repo

def test_create_suggestion_integration(suggestion_setup):
    # 1. ARRANGE
    service, repo = suggestion_setup
    plz = "10117"
    address = "Friedrichstraße"
    reason = "High traffic area"

    # 2. ACT
    # We use the service just like our Streamlit UI does
    service.create_suggestion(plz, address, reason)

    # 3. ASSERT - Verify via Repository
    # Instead of checking a JSON file, we check the In-Memory storage
    all_suggestions = repo.fetch_raw_data()
    
    assert len(all_suggestions) == 1
    assert all_suggestions[0]['plz'] == "10117"
    assert all_suggestions[0]['address'] == "Friedrichstraße"
    assert all_suggestions[0]['status'] == "pending"
    assert "id" in all_suggestions[0]
    assert "timestamp" in all_suggestions[0]

def test_review_suggestion_logic(suggestion_setup):
    # 1. ARRANGE
    service, repo = suggestion_setup
    service.create_suggestion("10115", "Mitte", "Need power")
    suggestion_id = repo.fetch_raw_data()[0]['id']

    # 2. ACT
    # Test the admin review functionality
    service.review_suggestion(suggestion_id, status="approved", reviewer="Admin", notes="Valid point")

    # 3. ASSERT
    updated_suggestion = repo.fetch_raw_data()[0]
    assert updated_suggestion['status'] == "approved"
    assert updated_suggestion['reviewed_by'] == "Admin"
    assert updated_suggestion['review_notes'] == "Valid point"