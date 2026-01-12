"""InMemoryDemandRepository - In-memory storage for testing."""
from typing import Optional
import pandas as pd


class InMemoryDemandRepository:
    """In-memory repository for demand analysis (used in tests)."""

    def __init__(self) -> None:
        self._data: Optional[pd.DataFrame] = None

    def get_analysis(self) -> Optional[pd.DataFrame]:
        """Retrieve stored analysis."""
        return self._data

    def update_analysis(self, df: pd.DataFrame) -> None:
        """Store analysis data."""
        self._data = df