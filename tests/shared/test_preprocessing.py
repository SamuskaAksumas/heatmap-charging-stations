"""
Tests for Infrastructure Preprocessing Functions.

Following TDD principles:
- Happy Path (valid data transformations)
- Edge Cases (empty data, missing columns)
- Error Scenarios (invalid inputs)
"""
import pytest
import pandas as pd
from shapely.geometry import Point, Polygon
from config import pdict

from src.shared.infrastructure.preprocessing.geo_utils import (
    sort_by_plz_add_geometry,
    get_plz_centroid,
)
from src.shared.infrastructure.preprocessing.stations import (
    count_plz_occurrences,
    preprop_lstat,
)
from src.shared.infrastructure.preprocessing.residents import preprop_resid


# ==================== FIXTURES ====================

@pytest.fixture
def sample_geodata():
    """Sample geodata with PLZ and geometry."""
    return pd.DataFrame({
        'PLZ': [10115, 10117, 10119],
        'geometry': [
            Polygon([(13.38, 52.52), (13.39, 52.52), (13.39, 52.53), (13.38, 52.53)]),
            Polygon([(13.39, 52.52), (13.40, 52.52), (13.40, 52.53), (13.39, 52.53)]),
            Polygon([(13.40, 52.52), (13.41, 52.52), (13.41, 52.53), (13.40, 52.53)]),
        ]
    })


@pytest.fixture
def sample_stations_raw():
    """Sample raw station data (like Ladesaeulenregister.csv)."""
    return pd.DataFrame({
        'Postleitzahl': [10115, 10115, 10117, 99999],
        'Bundesland': ['Berlin', 'Berlin', 'Berlin', 'Bayern'],
        'Breitengrad': ['52,52', '52,53', '52,52', '48,13'],
        'Längengrad': ['13,38', '13,39', '13,39', '11,58'],
        'Nennleistung Ladeeinrichtung [kW]': [22, 50, 11, 22],
    })


@pytest.fixture
def sample_residents_raw():
    """Sample raw resident data (like plz_einwohner.csv)."""
    return pd.DataFrame({
        'plz': [10115, 10117, 10119, 99999],
        'einwohner': [5000, 8000, 3000, 10000],
        'lat': ['52,52', '52,52', '52,53', '48,13'],
        'lon': ['13,38', '13,39', '13,40', '11,58'],
    })


# ==================== GEO_UTILS TESTS ====================

class TestSortByPlzAddGeometry:
    """Tests for sort_by_plz_add_geometry function."""

    def test_merges_geometry_column(self, sample_geodata):
        """Test that geometry is merged from geodata."""
        df = pd.DataFrame({'PLZ': [10117, 10115]})  # Unsorted
        result = sort_by_plz_add_geometry(df, sample_geodata, pdict)

        assert 'geometry' in result.columns
        assert len(result) == 2

    def test_sorts_by_plz(self, sample_geodata):
        """Test that result is sorted by PLZ."""
        df = pd.DataFrame({'PLZ': [10119, 10115, 10117]})
        result = sort_by_plz_add_geometry(df, sample_geodata, pdict)

        plz_list = result['PLZ'].tolist()
        assert plz_list == sorted(plz_list)

    def test_drops_rows_without_geometry(self, sample_geodata):
        """Test that rows without matching geometry are dropped."""
        df = pd.DataFrame({'PLZ': [10115, 99999]})  # 99999 not in geodata
        result = sort_by_plz_add_geometry(df, sample_geodata, pdict)

        assert len(result) == 1
        assert result.iloc[0]['PLZ'] == 10115


class TestGetPlzCentroid:
    """Tests for get_plz_centroid function."""

    def test_returns_centroid_for_valid_plz(self, sample_geodata):
        """Test centroid calculation for valid PLZ."""
        lat, lon = get_plz_centroid('10115', sample_geodata)

        assert lat is not None
        assert lon is not None
        assert 52.0 < lat < 53.0  # Berlin latitude range
        assert 13.0 < lon < 14.0  # Berlin longitude range

    def test_returns_none_for_invalid_plz(self, sample_geodata):
        """Test that invalid PLZ returns None."""
        lat, lon = get_plz_centroid('99999', sample_geodata)

        assert lat is None
        assert lon is None

    def test_returns_none_for_non_numeric_plz(self, sample_geodata):
        """Test that non-numeric PLZ returns None."""
        lat, lon = get_plz_centroid('abcde', sample_geodata)

        assert lat is None
        assert lon is None


# ==================== STATIONS TESTS ====================

class TestCountPlzOccurrences:
    """Tests for count_plz_occurrences function."""

    def test_counts_stations_per_plz(self):
        """Test correct counting of stations per PLZ."""
        df = pd.DataFrame({
            'PLZ': [10115, 10115, 10115, 10117, 10117],
            'geometry': [None, None, None, None, None]
        })
        result = count_plz_occurrences(df)

        assert len(result) == 2
        assert result[result['PLZ'] == 10115]['Number'].iloc[0] == 3
        assert result[result['PLZ'] == 10117]['Number'].iloc[0] == 2

    def test_preserves_first_geometry(self):
        """Test that first geometry per PLZ is kept."""
        df = pd.DataFrame({
            'PLZ': [10115, 10115],
            'geometry': ['geom_first', 'geom_second']
        })
        result = count_plz_occurrences(df)

        assert result.iloc[0]['geometry'] == 'geom_first'

    def test_single_station_per_plz(self):
        """Test PLZ with single station."""
        df = pd.DataFrame({
            'PLZ': [10115, 10117, 10119],
            'geometry': [None, None, None]
        })
        result = count_plz_occurrences(df)

        assert len(result) == 3
        assert all(result['Number'] == 1)


class TestPrepropLstat:
    """Tests for preprop_lstat function."""

    def test_filters_berlin_only(self, sample_stations_raw, sample_geodata):
        """Test that only Berlin stations are kept."""
        result = preprop_lstat(sample_stations_raw, sample_geodata, pdict)

        # Bayern station (99999) should be filtered out
        assert 99999 not in result['PLZ'].values

    def test_renames_columns(self, sample_stations_raw, sample_geodata):
        """Test that columns are renamed correctly."""
        result = preprop_lstat(sample_stations_raw, sample_geodata, pdict)

        assert 'PLZ' in result.columns
        assert 'KW' in result.columns
        assert 'Postleitzahl' not in result.columns

    def test_converts_comma_decimals(self, sample_stations_raw, sample_geodata):
        """Test that comma decimals are converted to dots."""
        result = preprop_lstat(sample_stations_raw, sample_geodata, pdict)

        # Original had '52,52' - should now be '52.52'
        assert ',' not in str(result['Breitengrad'].iloc[0])

    def test_plz_is_integer_not_float(self, sample_stations_raw, sample_geodata):
        """PLZ should be stored as integer, not float (e.g., 10115 not 10115.0)."""
        result = preprop_lstat(sample_stations_raw, sample_geodata, pdict)

        assert result['PLZ'].dtype in ['int64', 'int32'], \
            f"PLZ should be integer, got {result['PLZ'].dtype}"


# ==================== RESIDENTS TESTS ====================

class TestPrepropResid:
    """Tests for preprop_resid function."""

    def test_filters_berlin_plz_range(self, sample_residents_raw, sample_geodata):
        """Test that only Berlin PLZ range is kept."""
        result = preprop_resid(sample_residents_raw, sample_geodata, pdict)

        # 99999 should be filtered out
        assert 99999 not in result['PLZ'].values

    def test_renames_columns(self, sample_residents_raw, sample_geodata):
        """Test that columns are renamed correctly."""
        result = preprop_resid(sample_residents_raw, sample_geodata, pdict)

        assert 'PLZ' in result.columns
        assert 'Einwohner' in result.columns
        assert 'plz' not in result.columns
        assert 'einwohner' not in result.columns

    def test_adds_geometry(self, sample_residents_raw, sample_geodata):
        """Test that geometry column is added."""
        result = preprop_resid(sample_residents_raw, sample_geodata, pdict)

        assert 'geometry' in result.columns

    def test_plz_is_integer_not_float(self, sample_residents_raw, sample_geodata):
        """PLZ should be stored as integer, not float (e.g., 10115 not 10115.0)."""
        result = preprop_resid(sample_residents_raw, sample_geodata, pdict)

        assert result['PLZ'].dtype in ['int64', 'int32'], \
            f"PLZ should be integer, got {result['PLZ'].dtype}"


# ==================== EDGE CASES ====================

class TestPreprocessingEdgeCases:
    """Edge case tests for preprocessing functions."""

    def test_empty_dataframe_count_plz(self):
        """Test count_plz_occurrences with empty DataFrame."""
        df = pd.DataFrame({'PLZ': [], 'geometry': []})
        result = count_plz_occurrences(df)

        assert len(result) == 0

    def test_geodata_without_matching_plz(self, sample_geodata):
        """Test when no PLZ matches geodata."""
        df = pd.DataFrame({'PLZ': [99999, 88888]})
        result = sort_by_plz_add_geometry(df, sample_geodata, pdict)

        assert len(result) == 0
