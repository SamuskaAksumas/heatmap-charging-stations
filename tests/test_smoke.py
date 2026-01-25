"""
Smoke Test - Application Verification

Verifies that all important modules can be imported
and that the application is basically runnable after refactoring 
to DDD Aggregates, Entities, and Value Objects.
"""
import pytest


class TestSmokeImports:
    """Verifies that all modules can be imported."""

    def test_main_module_imports(self) -> None:
        """Verifies that main.py and config can be imported."""
        from config import pdict
        assert 'geocode' in pdict

    def test_presentation_layer_imports(self) -> None:
        """Verifies that the presentation layer can be imported."""
        from src.presentation.streamlit_app import make_streamlit_electric_charging_resid
        from src.presentation.components.map_view import render_map_layer
        from src.presentation.components.suggestion_form import render_suggestion_form
        from src.presentation.components.suggestion_list import render_suggestion_list
        assert callable(make_streamlit_electric_charging_resid)
        assert callable(render_map_layer)

    def test_demand_layer_imports(self) -> None:
        """Verifies that the demand bounded context can be imported."""
        from src.demand.application.services.demand_service import DemandService
        from src.demand.domain.aggregates.demand_aggregate import DemandAggregate
        from src.demand.domain.entities.demand_entity import DemandEntity
        from src.demand.domain.events.demand_calculated import DemandCalculatedEvent
        assert DemandService is not None
        assert DemandAggregate is not None

    def test_suggestion_layer_imports(self) -> None:
        """Verifies that the suggestion bounded context can be imported."""
        from src.suggestion.application.services.suggestion_service import SuggestionService
        from src.suggestion.domain.aggregates.suggestion_aggregate import SuggestionAggregate
        from src.suggestion.domain.entities.suggestion_entity import SuggestionEntity
        from src.suggestion.domain.exceptions.invalid_suggestion_exception import InvalidSuggestionException
        from src.suggestion.infrastructure.repositories.suggestion_repository import SuggestionRepository
        assert SuggestionService is not None
        assert SuggestionAggregate is not None
        assert SuggestionEntity is not None

    def test_shared_layer_imports(self) -> None:
        """Verifies that the shared bounded context can be imported."""
        from src.shared.domain.value_objects.postal_code import PostalCode
        from src.shared.domain.exceptions.domain_exception import DomainException
        from src.shared.infrastructure.preprocessing.residents import preprop_resid
        from src.shared.infrastructure.utils.helper_tools import timer
        assert PostalCode is not None
        assert DomainException is not None

    def test_infrastructure_preprocessing_imports(self) -> None:
        """Verifies that preprocessing modules can be imported."""
        from src.shared.infrastructure.preprocessing.geo_utils import (
            sort_by_plz_add_geometry,
            get_plz_centroid,
        )
        from src.shared.infrastructure.preprocessing.stations import (
            preprop_lstat,
            count_plz_occurrences,
        )
        assert callable(sort_by_plz_add_geometry)
        assert callable(preprop_lstat)


class TestSmokeInstantiation:
    """Verifies that important classes can be instantiated."""

    def test_postal_code_creation(self) -> None:
        """Verifies that a PostalCode value object can be created."""
        from src.shared.domain.value_objects.postal_code import PostalCode
        plz = PostalCode("10115")
        assert plz.value == "10115"

    def test_suggestion_aggregate_creation(self) -> None:
        """Verifies that a SuggestionAggregate (with Entity) can be created."""
        from src.suggestion.domain.entities.suggestion_entity import SuggestionEntity
        from src.suggestion.domain.aggregates.suggestion_aggregate import SuggestionAggregate
        
        entity = SuggestionEntity(
            id=1,
            plz="10115",
            address="Test Address",
            reason="Test Reason",
            status="pending",
            timestamp="2024-01-01T00:00:00"
        )
        aggregate = SuggestionAggregate(entity)
        assert aggregate.entity.plz == "10115"
        assert aggregate.entity.status == "pending"

    def test_demand_aggregate_creation(self) -> None:
        """Verifies that a DemandAggregate can be created."""
        from src.demand.domain.aggregates.demand_aggregate import DemandAggregate
        
        # Based on your definition: DemandAggregate(aggregate_id: str)
        plz_id = "10117"
        aggregate = DemandAggregate(plz_id)
        
        # Verify the ID is stored correctly
        # Depending on your implementation, this is likely .aggregate_id or .id
        try:
            assert aggregate.aggregate_id == plz_id
        except AttributeError:
            assert aggregate.id == plz_id


class TestSmokeExceptions:
    """Verifies that exceptions are thrown correctly."""

    def test_invalid_postal_code_raises(self) -> None:
        """Verifies that an invalid postal code throws an error."""
        from src.shared.domain.value_objects.postal_code import PostalCode
        # Assuming PostalCode value object does the validation
        with pytest.raises(ValueError):
            PostalCode("99999")

    def test_invalid_suggestion_status_transition_raises(self) -> None:
        """Verifies that the Aggregate state machine enforces rules."""
        from src.suggestion.domain.entities.suggestion_entity import SuggestionEntity
        from src.suggestion.domain.aggregates.suggestion_aggregate import SuggestionAggregate
        from src.suggestion.domain.exceptions.invalid_suggestion_exception import InvalidSuggestionException
        
        entity = SuggestionEntity(id=1, plz="10115", address="A", reason="R", status="approved")
        aggregate = SuggestionAggregate(entity)
        
        # Approved -> Rejected is an invalid transition in our domain rules
        with pytest.raises(InvalidSuggestionException):
            aggregate.apply_review(status="rejected", reviewer="Admin", notes="Wrong")
