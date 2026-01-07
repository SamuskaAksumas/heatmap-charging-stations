"""
Smoke Test - App-Verifikation

Prüft ob alle wichtigen Module importiert werden können
und die Anwendung grundsätzlich lauffähig ist.

Per TDD-Vorgabe aus der Vorlesung: Smoke Tests stellen sicher,
dass nach Refactoring die App-Level Funktionalität erhalten bleibt.
"""
import pytest


class TestSmokeImports:
    """Prüft ob alle Module importiert werden können."""

    def test_main_module_imports(self) -> None:
        """Prüft ob main.py und config importiert werden können."""
        from config import pdict
        assert 'geocode' in pdict

    def test_presentation_layer_imports(self) -> None:
        """Prüft ob der Presentation Layer importiert werden kann."""
        from src.presentation.streamlit_app import make_streamlit_electric_charging_resid
        from src.presentation.components.map_view import render_map_layer
        from src.presentation.components.suggestion_form import render_suggestion_form
        from src.presentation.components.suggestion_list import render_suggestion_list
        assert callable(make_streamlit_electric_charging_resid)
        assert callable(render_map_layer)

    def test_demand_layer_imports(self) -> None:
        """Prüft ob der Demand Bounded Context importiert werden kann."""
        from src.demand.application.services.demand_service import DemandService
        from src.demand.domain.entities.demand_result import DemandResult
        from src.demand.domain.events.demand_calculated import on_demand_calculated
        from src.demand.domain.exceptions import InvalidDemandDataException
        from src.demand.domain.value_objects.demand_score import DemandScore
        from src.demand.infrastructure.respositories.demand_repository import DemandRepository
        assert DemandService is not None
        assert DemandResult is not None

    def test_suggestion_layer_imports(self) -> None:
        """Prüft ob der Suggestion Bounded Context importiert werden kann."""
        from src.suggestion.application.services.suggestion_service import SuggestionService
        from src.suggestion.domain.entities.suggestion import ChargingSuggestion
        from src.suggestion.domain.exceptions import InvalidSuggestionException
        from src.suggestion.domain.events import SuggestionCreatedEvent, SuggestionReviewedEvent
        from src.suggestion.infrastructure.repositories.suggestion_repository import SuggestionRepository
        assert SuggestionService is not None
        assert ChargingSuggestion is not None

    def test_shared_layer_imports(self) -> None:
        """Prüft ob der Shared Bounded Context importiert werden kann."""
        from src.shared.domain.value_objects.postal_code import PostalCode
        from src.shared.domain.events.domain_event import DomainEvent
        from src.shared.domain.exceptions import DomainException, InvalidPostalCodeException
        from src.shared.domain.repositories.base_repository import BaseRepository
        from src.shared.infrastructure.preprocessing import preprop_resid, preprop_lstat
        from src.shared.infrastructure.utils import timer
        assert PostalCode is not None
        assert DomainEvent is not None

    def test_infrastructure_preprocessing_imports(self) -> None:
        """Prüft ob die Preprocessing-Module importiert werden können."""
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
    """Prüft ob wichtige Klassen instanziiert werden können."""

    def test_postal_code_creation(self) -> None:
        """Prüft ob ein PostalCode Value Object erstellt werden kann."""
        from src.shared.domain.value_objects.postal_code import PostalCode
        plz = PostalCode("10115")
        assert plz.value == "10115"

    def test_demand_score_creation(self) -> None:
        """Prüft ob ein DemandScore Value Object erstellt werden kann."""
        from src.demand.domain.value_objects.demand_score import DemandScore
        score = DemandScore(500.0)
        assert score.value == 500.0

    def test_domain_event_creation(self) -> None:
        """Prüft ob Domain Events erstellt werden können."""
        from src.shared.domain.events.domain_event import DomainEvent
        event = DomainEvent()
        assert event.event_id is not None
        assert event.timestamp is not None

    def test_suggestion_event_creation(self) -> None:
        """Prüft ob Suggestion Events erstellt werden können."""
        from src.suggestion.domain.events import SuggestionCreatedEvent
        event = SuggestionCreatedEvent(
            suggestion_id=1,
            plz="10115",
            address="Test",
            reason="Test"
        )
        assert event.suggestion_id == 1
        assert event.event_type == "SuggestionCreatedEvent"

    def test_demand_result_creation(self) -> None:
        """Prüft ob DemandResult Entity erstellt werden kann."""
        from src.demand.domain.entities.demand_result import DemandResult
        result = DemandResult(plz="10115", demand=7500.0, einwohner=15000, count=2)
        assert result.plz == "10115"
        assert result.get_demand_category() == "medium"  # 5000 < 7500 <= 10000


class TestSmokeExceptions:
    """Prüft ob Exceptions korrekt geworfen werden."""

    def test_invalid_postal_code_raises(self) -> None:
        """Prüft ob ungültige PLZ einen Fehler wirft."""
        from src.shared.domain.value_objects.postal_code import PostalCode
        with pytest.raises(ValueError):
            PostalCode("99999")

    def test_invalid_demand_score_raises(self) -> None:
        """Prüft ob negativer DemandScore einen Fehler wirft."""
        from src.demand.domain.value_objects.demand_score import DemandScore
        from src.demand.domain.exceptions import InvalidDemandDataException
        with pytest.raises(InvalidDemandDataException):
            DemandScore(-100.0)
