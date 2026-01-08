import pytest
from src.suggestion.application.services.suggestion_service import SuggestionService
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


# ==================== EDGE CASE TESTS ====================

class TestSuggestionEdgeCases:
    """Edge Case tests - boundary conditions."""

    def test_multiple_suggestions(self, suggestion_setup):
        """Test creating multiple suggestions."""
        service, repo = suggestion_setup

        service.create_suggestion("10115", "Address 1", "Reason 1")
        service.create_suggestion("10117", "Address 2", "Reason 2")
        service.create_suggestion("10119", "Address 3", "Reason 3")

        all_suggestions = repo.fetch_raw_data()
        assert len(all_suggestions) == 3
        assert all_suggestions[0]['id'] == 1
        assert all_suggestions[1]['id'] == 2
        assert all_suggestions[2]['id'] == 3

    def test_reject_suggestion(self, suggestion_setup):
        """Test rejecting a suggestion."""
        service, repo = suggestion_setup

        service.create_suggestion("10115", "Bad Location", "Not good")
        suggestion_id = repo.fetch_raw_data()[0]['id']

        service.review_suggestion(suggestion_id, status="rejected", reviewer="Admin", notes="Invalid location")

        updated = repo.fetch_raw_data()[0]
        assert updated['status'] == "rejected"
        assert updated['review_notes'] == "Invalid location"

    def test_get_all_suggestions_filters_deleted(self, suggestion_setup):
        """Test that get_all_suggestions filters out deleted items."""
        service, repo = suggestion_setup

        service.create_suggestion("10115", "Address 1", "Reason 1")
        service.create_suggestion("10117", "Address 2", "Reason 2")

        # Manually mark one as deleted
        all_data = repo.fetch_raw_data()
        all_data[0]['status'] = 'deleted'
        repo.save(all_data)

        # get_all_suggestions should filter deleted
        visible = service.get_all_suggestions()
        assert len(visible) == 1
        assert visible[0]['plz'] == "10117"


# ==================== ERROR SCENARIO TESTS ====================

class TestSuggestionErrorScenarios:
    """Error Scenario tests - handling invalid inputs."""

    def test_get_all_suggestions_empty(self, suggestion_setup):
        """Test getting suggestions when none exist."""
        service, repo = suggestion_setup

        result = service.get_all_suggestions()
        assert result == []

    def test_review_nonexistent_suggestion(self, suggestion_setup):
        """Test reviewing a suggestion that doesn't exist."""
        service, repo = suggestion_setup

        # Try to review suggestion with ID 999 (doesn't exist)
        service.review_suggestion(999, status="approved", reviewer="Admin", notes="Test")

        # Should not crash, just do nothing
        all_suggestions = repo.fetch_raw_data()
        assert len(all_suggestions) == 0


# ==================== DOMAIN RULE TESTS ====================

class TestSuggestionDomainRules:
    """Domain Rule tests - business constraints."""

    def test_suggestion_starts_with_pending_status(self, suggestion_setup):
        """Test that new suggestions always start with 'pending' status."""
        service, repo = suggestion_setup

        service.create_suggestion("10115", "Test Address", "Test Reason")

        suggestion = repo.fetch_raw_data()[0]
        assert suggestion['status'] == "pending"

    def test_suggestion_gets_timestamp(self, suggestion_setup):
        """Test that suggestions get a timestamp."""
        service, repo = suggestion_setup

        service.create_suggestion("10115", "Test Address", "Test Reason")

        suggestion = repo.fetch_raw_data()[0]
        assert 'timestamp' in suggestion
        assert suggestion['timestamp'] is not None

    def test_suggestion_gets_incremental_id(self, suggestion_setup):
        """Test that suggestions get incremental IDs."""
        service, repo = suggestion_setup

        service.create_suggestion("10115", "Address 1", "Reason 1")
        service.create_suggestion("10117", "Address 2", "Reason 2")

        suggestions = repo.fetch_raw_data()
        assert suggestions[0]['id'] == 1
        assert suggestions[1]['id'] == 2