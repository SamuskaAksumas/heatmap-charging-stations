import pytest
from src.suggestion.application.services.suggestion_service import SuggestionService
from src.suggestion.infrastructure.repositories.in_memory_suggestion_repository import InMemorySuggestionRepository
from src.suggestion.domain.exceptions import InvalidSuggestionException

@pytest.fixture
def suggestion_setup():
    """Fixture to provide a clean service and in-memory repo for every test."""
    repo = InMemorySuggestionRepository()
    service = SuggestionService(repo)
    return service, repo

def test_create_suggestion_integration(suggestion_setup):
    service, repo = suggestion_setup
    plz, address, reason = "10117", "Friedrichstraße", "High traffic area"

    service.create_suggestion(plz, address, reason)

    all_suggestions = repo.get_all_including_deleted()
    assert len(all_suggestions) == 1
    # Check the Aggregate's internal entity
    suggestion = all_suggestions[0].entity
    assert suggestion.plz == "10117"
    assert suggestion.address == "Friedrichstraße"
    assert suggestion.status == "pending"
    assert suggestion.id is not None
    assert suggestion.timestamp is not None

def test_review_suggestion_logic(suggestion_setup):
    service, repo = suggestion_setup
    service.create_suggestion("10115", "Mitte", "Need power")
    suggestion_id = repo.get_all_including_deleted()[0].entity.id

    service.review_suggestion(suggestion_id, status="approved", reviewer="Admin", notes="Valid point")

    updated = repo.get_all_including_deleted()[0].entity
    assert updated.status == "approved"
    assert updated.reviewed_by == "Admin"
    assert updated.review_notes == "Valid point"

# ==================== EDGE CASE TESTS ====================

class TestSuggestionEdgeCases:
    def test_multiple_suggestions(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Address 1", "Reason 1")
        service.create_suggestion("10117", "Address 2", "Reason 2")
        service.create_suggestion("10119", "Address 3", "Reason 3")

        all_suggestions = repo.get_all_including_deleted()
        assert len(all_suggestions) == 3
        assert all_suggestions[0].entity.id == 1
        assert all_suggestions[1].entity.id == 2
        assert all_suggestions[2].entity.id == 3

    def test_reject_suggestion(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Bad Location", "Not good")
        suggestion_id = repo.get_all_including_deleted()[0].entity.id

        service.review_suggestion(suggestion_id, status="rejected", reviewer="Admin", notes="Invalid location")

        updated = repo.get_all_including_deleted()[0].entity
        assert updated.status == "rejected"
        assert updated.review_notes == "Invalid location"

    def test_get_all_suggestions_filters_deleted(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Address 1", "Reason 1")
        service.create_suggestion("10117", "Address 2", "Reason 2")

        # Admin deletes the first one
        all_data = repo.get_all_including_deleted()
        service.review_suggestion(all_data[0].entity.id, status="deleted", reviewer="Admin", notes="Delete")

        # get_all_suggestions (Admin View) should filter out deleted
        visible = service.get_all_suggestions()
        assert len(visible) == 1
        assert visible[0]['plz'] == "10117"

# ==================== ERROR SCENARIO TESTS ====================

class TestSuggestionErrorScenarios:
    def test_get_all_suggestions_empty(self, suggestion_setup):
        service, _ = suggestion_setup
        assert service.get_all_suggestions() == []

    def test_review_nonexistent_suggestion(self, suggestion_setup):
        service, repo = suggestion_setup
        # Should return False or handle gracefully
        result = service.review_suggestion(999, status="approved", reviewer="Admin", notes="Test")
        assert result is False
        assert len(repo.get_all_including_deleted()) == 0

# ==================== DOMAIN RULE TESTS ====================

class TestSuggestionDomainRules:
    def test_suggestion_starts_with_pending_status(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Test Address", "Test Reason")
        assert repo.get_all_including_deleted()[0].entity.status == "pending"

    def test_suggestion_gets_timestamp(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Test Address", "Test Reason")
        assert repo.get_all_including_deleted()[0].entity.timestamp is not None

    def test_suggestion_gets_incremental_id(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "A1", "R1")
        service.create_suggestion("10117", "A2", "R2")
        all_aggs = repo.get_all_including_deleted()
        assert all_aggs[0].entity.id == 1
        assert all_aggs[1].entity.id == 2

# ==================== STATE MACHINE TESTS ====================

class TestSuggestionStateMachine:
    def test_cannot_approve_already_approved(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Test", "Reason")
        suggestion_id = repo.get_all_including_deleted()[0].entity.id

        service.review_suggestion(suggestion_id, status="approved", reviewer="Admin", notes="Ok")
        with pytest.raises(InvalidSuggestionException):
            service.review_suggestion(suggestion_id, status="approved", reviewer="Admin2", notes="No")

    def test_cannot_reject_already_approved(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Test", "Reason")
        suggestion_id = repo.get_all_including_deleted()[0].entity.id

        service.review_suggestion(suggestion_id, status="approved", reviewer="Admin", notes="Ok")
        with pytest.raises(InvalidSuggestionException):
            service.review_suggestion(suggestion_id, status="rejected", reviewer="Admin", notes="No")

    def test_can_delete_approved_suggestion(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Test", "Reason")
        suggestion_id = repo.get_all_including_deleted()[0].entity.id

        service.review_suggestion(suggestion_id, status="approved", reviewer="Admin", notes="Ok")
        service.review_suggestion(suggestion_id, status="deleted", reviewer="Admin", notes="Bye")
        assert repo.get_all_including_deleted()[0].entity.status == "deleted"

# ==================== USER VISIBILITY TESTS ====================

class TestUserVisibility:
    def test_get_suggestions_for_users_excludes_rejected(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "P", "R1")
        service.create_suggestion("10117", "A", "R2")
        service.create_suggestion("10119", "R", "R3")

        all_aggs = repo.get_all_including_deleted()
        service.review_suggestion(all_aggs[1].entity.id, status="approved", reviewer="Admin", notes="Ok")
        service.review_suggestion(all_aggs[2].entity.id, status="rejected", reviewer="Admin", notes="No")

        user_visible = service.get_suggestions_for_users()
        assert len(user_visible) == 2
        statuses = [s['status'] for s in user_visible]
        assert 'pending' in statuses and 'approved' in statuses and 'rejected' not in statuses

    def test_get_suggestions_for_users_excludes_deleted(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "A1", "R1")
        service.create_suggestion("10117", "A2", "R2")

        service.review_suggestion(1, status="deleted", reviewer="Admin", notes="Del")
        user_visible = service.get_suggestions_for_users()
        assert len(user_visible) == 1
        assert user_visible[0]['plz'] == "10117"

# ==================== DELETE FUNCTIONALITY TESTS ====================

class TestDeleteFunctionality:
    def test_delete_pending_suggestion(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Test", "Reason")
        service.review_suggestion(1, status="deleted", reviewer="Admin", notes="X")
        assert repo.get_all_including_deleted()[0].entity.status == "deleted"

    def test_cannot_delete_already_deleted(self, suggestion_setup):
        service, repo = suggestion_setup
        service.create_suggestion("10115", "Test", "Reason")
        service.review_suggestion(1, status="deleted", reviewer="Admin", notes="X")
        
        # This will fail because the Aggregate's apply_review logic should 
        # prevent transitions from 'deleted' to 'deleted' if defined.
        with pytest.raises(InvalidSuggestionException):
            service.review_suggestion(1, status="deleted", reviewer="Admin", notes="X")
