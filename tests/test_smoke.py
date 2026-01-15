"""
Smoke Test - Application Verification

Verifies that all important modules can be imported
and that the application is basically runnable.

Following TDD guidelines: Smoke tests ensure that after refactoring,
the app-level functionality is preserved.
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
        from src.demand.domain.events.demand_calculated import on_demand_calculated
        from src.demand.infrastructure.repositories.demand_repository import DemandRepository
        assert DemandService is not None
        assert callable(on_demand_calculated)

    def test_suggestion_layer_imports(self) -> None:
        """Verifies that the suggestion bounded context can be imported."""
        from src.suggestion.application.services.suggestion_service import SuggestionService
        from src.suggestion.domain.entities.suggestion import ChargingSuggestion
        from src.suggestion.domain.exceptions import InvalidSuggestionException
        from src.suggestion.infrastructure.repositories.suggestion_repository import SuggestionRepository
        assert SuggestionService is not None
        assert ChargingSuggestion is not None

    def test_shared_layer_imports(self) -> None:
        """Verifies that the shared bounded context can be imported."""
        from src.shared.domain.value_objects.postal_code import PostalCode
        from src.shared.domain.exceptions import DomainException
        from src.shared.infrastructure.preprocessing import preprop_resid, preprop_lstat
        from src.shared.infrastructure.utils import timer
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
        from src.shared.infrastructure.preprocessing.residents import preprop_resid
        assert callable(sort_by_plz_add_geometry)
        assert callable(preprop_lstat)


class TestSmokeInstantiation:
    """Verifies that important classes can be instantiated."""

    def test_postal_code_creation(self) -> None:
        """Verifies that a PostalCode value object can be created."""
        from src.shared.domain.value_objects.postal_code import PostalCode
        plz = PostalCode("10115")
        assert plz.value == "10115"

    def test_suggestion_creation(self) -> None:
        """Verifies that a ChargingSuggestion entity can be created."""
        from src.suggestion.domain.entities.suggestion import ChargingSuggestion
        suggestion = ChargingSuggestion.from_dict({
            'id': 1,
            'plz': '10115',
            'address': 'Test Address',
            'reason': 'Test Reason',
            'status': 'pending',
            'created_at': '2024-01-01T00:00:00'
        })
        assert suggestion.plz == "10115"
        assert suggestion.status == "pending"


class TestSmokeExceptions:
    """Verifies that exceptions are thrown correctly."""

    def test_invalid_postal_code_raises(self) -> None:
        """Verifies that an invalid postal code throws an error."""
        from src.shared.domain.value_objects.postal_code import PostalCode
        with pytest.raises(ValueError):
            PostalCode("99999")

    def test_invalid_suggestion_plz_raises(self) -> None:
        """Verifies that an invalid PLZ in suggestion throws an error."""
        from src.suggestion.domain.entities.suggestion import ChargingSuggestion
        from src.suggestion.domain.exceptions import InvalidSuggestionException
        with pytest.raises(InvalidSuggestionException):
            ChargingSuggestion.from_dict({
                'id': 1,
                'plz': '99999',  # Invalid - not a Berlin PLZ
                'address': 'Test',
                'reason': 'Test',
                'status': 'pending',
                'created_at': '2024-01-01T00:00:00'
            })
