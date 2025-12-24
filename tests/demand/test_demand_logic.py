import pytest
import pandas as pd
from src.domain.events.demand_calculated import on_demand_calculated


@pytest.mark.parametrize(
    "people, stations, expected_demand",
    [
        (500, 0, 500.0),
        (500, 1, 500.0),
        (500, 5, 100.0),
        (0, 10, 0.0),
    ],
)
def test_demand_various_scenarios(people, stations, expected_demand):
    # ARRANGE
    df_stations = pd.DataFrame({
        'PLZ': ['12345'],
        'count': [stations]
    })

    df_residents = pd.DataFrame({
        'PLZ': ['12345'],
        'Einwohner': [people],
        'geometry': [None]
    })

    # ACT
    result = on_demand_calculated(df_stations, df_residents)

    # ASSERT — structure
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert 'PLZ' in result.columns
    assert 'demand' in result.columns

    # ASSERT — content
    assert result.iloc[0]['PLZ'] == '12345'
    assert pytest.approx(result.iloc[0]['demand'], rel=1e-6) == expected_demand

def test_demand_multiple_plz():
    df_stations = pd.DataFrame({
        'PLZ': ['12345', '54321'],
        'count': [5, 10]
    })

    df_residents = pd.DataFrame({
        'PLZ': ['12345', '54321'],
        'Einwohner': [500, 1000],
        'geometry': [None, None]
    })

    result = on_demand_calculated(df_stations, df_residents)

    assert len(result) == 2
    assert set(result['PLZ']) == {'12345', '54321'}