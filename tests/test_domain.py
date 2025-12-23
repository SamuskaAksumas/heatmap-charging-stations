"""
Unit tests for the domain layer.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock
import shapely.geometry

from domain.charging_infrastructure.entities import ChargingStation, Location, Capacity
from domain.charging_infrastructure.services import ChargingStationService
from domain.geography.entities import PostalArea, Coordinate
from domain.community_engagement.entities import ChargingSuggestion, SuggestionStatus


class TestChargingStation:
    """Test cases for ChargingStation entity."""

    def test_charging_station_creation(self):
        """Test creating a charging station."""
        location = Location(latitude=52.5200, longitude=13.4050)
        capacity = Capacity(power_kw=150, connector_type="CCS")

        station = ChargingStation(
            station_id="ST001",
            location=location,
            capacity=capacity,
            postal_code="10115",
            address="Test Address",
            operator="Test Operator"
        )

        assert station.station_id == "ST001"
        assert station.operator == "Test Operator"
        assert station.location.latitude == 52.5200
        assert station.capacity.power_kw == 150
        assert station.postal_code == "10115"

    def test_capacity_creation(self):
        """Test capacity creation."""
        capacity = Capacity(power_kw=150, connector_type="CCS")

        assert capacity.power_kw == 150
        assert capacity.connector_type == "CCS"


class TestChargingStationService:
    """Test cases for ChargingStationService."""

    def test_get_stations_summary_by_postal_code(self):
        """Test getting station summary by postal code."""
        # Mock repository
        mock_repo = Mock()
        mock_stations = [
            ChargingStation(
                station_id="ST001",
                location=Location(52.5200, 13.4050),
                capacity=Capacity(100, "Type2"),
                postal_code="10115",
                address="Addr1",
                operator="Op1"
            ),
            ChargingStation(
                station_id="ST002",
                location=Location(52.5200, 13.4050),
                capacity=Capacity(200, "CCS"),
                postal_code="10115",
                address="Addr2",
                operator="Op2"
            ),
            ChargingStation(
                station_id="ST003",
                location=Location(52.5200, 13.4050),
                capacity=Capacity(50, "Type2"),
                postal_code="10117",
                address="Addr3",
                operator="Op3"
            )
        ]
        mock_repo.get_all.return_value = mock_stations

        service = ChargingStationService(mock_repo)
        summary = service.get_stations_summary_by_postal_code()

        assert summary["10115"] == 2
        assert summary["10117"] == 1
        assert len(summary) == 2


class TestPostalArea:
    """Test cases for PostalArea entity."""

    def test_postal_area_creation(self):
        """Test creating a postal area."""
        # Create a simple polygon geometry
        coords = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        polygon = shapely.geometry.Polygon(coords)

        area = PostalArea(
            postal_code="10115",
            geometry=polygon
        )

        assert area.postal_code == "10115"
        assert area.geometry is not None

    def test_centroid_calculation(self):
        """Test centroid calculation."""
        # Create a simple square polygon
        coords = [(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]
        polygon = shapely.geometry.Polygon(coords)

        area = PostalArea("10115", polygon)
        centroid = area.calculate_centroid()

        # For a square from (0,0) to (2,2), centroid should be at (1,1)
        assert abs(centroid.latitude - 1.0) < 0.01
        assert abs(centroid.longitude - 1.0) < 0.01


class TestChargingSuggestion:
    """Test cases for ChargingSuggestion entity."""

    def test_suggestion_creation(self):
        """Test creating a suggestion."""
        submitted_at = datetime(2024, 1, 1, 12, 0, 0)

        suggestion = ChargingSuggestion(
            id=1,
            postal_code="10115",
            address="Test Address",
            reason="Need more charging",
            submitted_at=submitted_at
        )

        assert suggestion.id == 1
        assert suggestion.postal_code == "10115"
        assert suggestion.status == SuggestionStatus.PENDING
        assert suggestion.submitted_at == submitted_at

    def test_suggestion_approval(self):
        """Test approving a suggestion."""
        suggestion = ChargingSuggestion(
            id=1,
            postal_code="10115",
            address="Test Address",
            reason="Need more charging",
            submitted_at=datetime.now()
        )

        suggestion.approve("Admin", "Good location")

        assert suggestion.status == SuggestionStatus.APPROVED
        assert suggestion.review_info.reviewer == "Admin"
        assert suggestion.review_info.notes == "Good location"
        assert suggestion.review_info.review_date is not None

    def test_suggestion_rejection(self):
        """Test rejecting a suggestion."""
        suggestion = ChargingSuggestion(
            id=1,
            postal_code="10115",
            address="Test Address",
            reason="Need more charging",
            submitted_at=datetime.now()
        )

        suggestion.reject("Admin", "Already has stations")

        assert suggestion.status == SuggestionStatus.REJECTED
        assert suggestion.review_info.reviewer == "Admin"
        assert suggestion.review_info.notes == "Already has stations"