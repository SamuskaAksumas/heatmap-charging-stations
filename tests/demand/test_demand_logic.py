import pytest
import pandas as pd
from src.domain.events.demand_calculated import on_demand_calculated

@pytest.mark.parametrize("people, stations, expected_demand", [
    (500, 0, 500.0),  # Case 1: 0 stations -> Demand is just the population
    (500, 1, 500.0),  # Case 2: 500 / 1 = 500
    (500, 5, 100.0),  # Case 3: 500 / 5 = 100
    (0, 10, 0.0),     # Case 4: No people -> No demand
])
def test_demand_various_scenarios(people, stations, expected_demand):
    df_stations = pd.DataFrame({'PLZ': ['12345'], 'count': [stations]})
    df_residents = pd.DataFrame({'PLZ': ['12345'], 'Einwohner': [people], 'geometry': [None]})
    
    result = on_demand_calculated(df_stations, df_residents)
    
    assert result.iloc[0]['demand'] == expected_demand