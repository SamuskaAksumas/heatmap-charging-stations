import pytest
import pandas as pd
from src.demand.application.services.demand_service import DemandService
from src.demand.infrastructure.respositories.in_memory_demand_repository import InMemoryDemandRepository

@pytest.fixture
def demand_setup():
    """Fixture to initialize the service with a fake repository."""
    repo = InMemoryDemandRepository()
    service = DemandService(repo)
    return service, repo

@pytest.mark.parametrize(
    "people, stations, expected_demand",
    [
        (500, 0, 500.0),   # Rule: If 0 stations, demand = total residents
        (500, 1, 500.0),   # Rule: 500 / 1
        (500, 5, 100.0),   # Rule: 500 / 5
        (0, 10, 0.0),      # Rule: 0 / 10
    ],
)
def test_demand_service_integration(demand_setup, people, stations, expected_demand):
    # 1. ARRANGE
    service, repo = demand_setup
    
    df_stations = pd.DataFrame({
        'PLZ': ['12345'],
        'count': [stations] # The service handles 'count' vs 'Number' internally
    })

    df_residents = pd.DataFrame({
        'PLZ': ['12345'],
        'Einwohner': [people],
        'geometry': [None]
    })

    # 2. ACT
    # We call the SERVICE, which calls the Domain Event, which updates the REPO
    result = service.calculate_demand(df_stations, df_residents)

    # 3. ASSERT - Logic check
    assert result.iloc[0]['PLZ'] == '12345'
    assert pytest.approx(result.iloc[0]['demand']) == expected_demand

    # 4. ASSERT - Repository check (Crucial for TDD)
    # Ensure the repository actually 'holds' the data now
    stored_data = repo.get_analysis()
    assert stored_data is not None
    assert pytest.approx(stored_data.iloc[0]['demand']) == expected_demand

def test_demand_service_get_latest(demand_setup):
    service, repo = demand_setup

    # Create dummy data
    df_stations = pd.DataFrame({'PLZ': ['10115'], 'count': [2]})
    df_residents = pd.DataFrame({'PLZ': ['10115'], 'Einwohner': [1000], 'geometry': [None]})

    # First, calculate it
    service.calculate_demand(df_stations, df_residents)

    # Then, use the Query function (get_latest_results)
    latest = service.get_latest_results()

    assert latest is not None
    assert latest.iloc[0]['PLZ'] == '10115'
    assert 'demand' in latest.columns


# ==================== EDGE CASE TESTS ====================

class TestDemandEdgeCases:
    """Edge Case tests - boundary conditions."""

    def test_multiple_plz_areas(self, demand_setup):
        """Test demand calculation for multiple PLZ areas."""
        service, repo = demand_setup

        df_stations = pd.DataFrame({
            'PLZ': ['10115', '10117', '10119'],
            'count': [5, 0, 10]
        })
        df_residents = pd.DataFrame({
            'PLZ': ['10115', '10117', '10119'],
            'Einwohner': [1000, 500, 2000],
            'geometry': [None, None, None]
        })

        result = service.calculate_demand(df_stations, df_residents)

        assert len(result) == 3
        # 10115: 1000/5 = 200
        assert pytest.approx(result[result['PLZ'] == '10115'].iloc[0]['demand']) == 200.0
        # 10117: 500/0 = 500 (residents only)
        assert pytest.approx(result[result['PLZ'] == '10117'].iloc[0]['demand']) == 500.0
        # 10119: 2000/10 = 200
        assert pytest.approx(result[result['PLZ'] == '10119'].iloc[0]['demand']) == 200.0

    def test_very_high_demand(self, demand_setup):
        """Test with very high population and few stations."""
        service, repo = demand_setup

        df_stations = pd.DataFrame({'PLZ': ['10115'], 'count': [1]})
        df_residents = pd.DataFrame({
            'PLZ': ['10115'],
            'Einwohner': [100000],
            'geometry': [None]
        })

        result = service.calculate_demand(df_stations, df_residents)
        assert pytest.approx(result.iloc[0]['demand']) == 100000.0

    def test_plz_only_in_residents(self, demand_setup):
        """Test PLZ that exists only in residents data (no stations)."""
        service, repo = demand_setup

        df_stations = pd.DataFrame({'PLZ': ['10115'], 'count': [5]})
        df_residents = pd.DataFrame({
            'PLZ': ['10115', '10117'],  # 10117 has no stations
            'Einwohner': [1000, 500],
            'geometry': [None, None]
        })

        result = service.calculate_demand(df_stations, df_residents)

        # 10117 should have demand = residents (no stations = 0)
        plz_10117 = result[result['PLZ'] == '10117']
        assert len(plz_10117) == 1
        assert pytest.approx(plz_10117.iloc[0]['demand']) == 500.0


# ==================== ERROR SCENARIO TESTS ====================

class TestDemandErrorScenarios:
    """Error Scenario tests - handling edge cases gracefully."""

    def test_get_latest_without_calculation(self, demand_setup):
        """Test getting results before any calculation."""
        service, repo = demand_setup

        result = service.get_latest_results()
        assert result is None

    def test_empty_dataframes(self, demand_setup):
        """Test with empty input DataFrames."""
        service, repo = demand_setup

        df_stations = pd.DataFrame({'PLZ': [], 'count': []})
        df_residents = pd.DataFrame({
            'PLZ': [],
            'Einwohner': [],
            'geometry': []
        })

        result = service.calculate_demand(df_stations, df_residents)
        assert len(result) == 0