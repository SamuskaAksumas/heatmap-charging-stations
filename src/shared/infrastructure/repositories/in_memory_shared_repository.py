"""InMemorySharedRepository - In-memory storage for testing."""
import pandas as pd


class InMemorySharedRepository:
    """In-memory repository for shared data (used in tests)."""

    def __init__(self):
        self._fake_csv_data = None
        self._fake_geodata = None

    def set_fake_csv_data(self, df: pd.DataFrame):
        """Set fake CSV data for testing."""
        self._fake_csv_data = df

    def set_fake_geodata(self, df: pd.DataFrame):
        """Set fake geodata for testing."""
        self._fake_geodata = df

    def read_csv_with_header_detection(self, path, sep=';'):
        """Return pre-loaded fake CSV."""
        return self._fake_csv_data

    def load_geodata(self, path):
        """Return pre-loaded fake geodata."""
        return self._fake_geodata
