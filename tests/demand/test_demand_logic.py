import pytest
import pandas as pd
from src.demand.application.services.demandServices import DemandService
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