"""
Configuration settings for the charging map application.
"""
from pathlib import Path


class Config:
    """Application configuration."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    DATASETS_DIR = PROJECT_ROOT / "datasets"
    DOMAIN_DIR = PROJECT_ROOT / "domain"
    APPLICATION_DIR = PROJECT_ROOT / "application"
    INFRASTRUCTURE_DIR = PROJECT_ROOT / "infrastructure"
    PRESENTATION_DIR = PROJECT_ROOT / "presentation"
    TESTS_DIR = PROJECT_ROOT / "tests"

    # Data file paths
    CHARGING_STATIONS_CSV = DATASETS_DIR / "Ladesaeulenregister.csv"
    POSTAL_AREAS_SHAPEFILE = DATASETS_DIR / "berlin_postleitzahlen" / "berlin_postleitzahlen.shp"
    DEMOGRAPHICS_EXCEL = DATASETS_DIR / "plz_einwohner.xlsx"  # Population data
    SUGGESTIONS_JSON = DATASETS_DIR / "suggestions.json"

    # Berlin boundaries (approximate)
    BERLIN_BOUNDS = {
        'north': 52.6755,
        'south': 52.3382,
        'east': 13.7607,
        'west': 13.0883
    }

    # Valid Berlin postal code range
    BERLIN_PLZ_RANGE = (10000, 14200)

    # Analytics settings
    DEMAND_THRESHOLD_HIGH = 50  # Score threshold for high demand
    DEMAND_THRESHOLD_LOW = 20   # Score threshold for low demand

    # UI settings
    MAP_DEFAULT_ZOOM = 10
    MAP_DEFAULT_LOCATION = [52.5200, 13.4050]  # Berlin center

    # Cache settings
    CACHE_ENABLED = True
    CACHE_TTL_SECONDS = 3600  # 1 hour

    @classmethod
    def validate_paths(cls):
        """Validate that all required data paths exist."""
        required_paths = [
            cls.CHARGING_STATIONS_CSV,
            cls.POSTAL_AREAS_SHAPEFILE,
        ]

        missing_paths = []
        for path in required_paths:
            if not path.exists():
                missing_paths.append(str(path))

        if missing_paths:
            raise FileNotFoundError(f"Missing required data files: {missing_paths}")

        return True