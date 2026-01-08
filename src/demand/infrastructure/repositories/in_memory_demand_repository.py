"""
Repository: InMemoryDemandRepository

In-memory implementation for testing purposes.
"""
from typing import Optional
import pandas as pd


class InMemoryDemandRepository:
    """
    In-memory repository for demand analysis (used in tests).

    This implementation stores data in RAM without persistence,
    making it ideal for unit testing.
    """

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._data: Optional[pd.DataFrame] = None

    def get_analysis(self) -> Optional[pd.DataFrame]:
        """
        Retrieve stored analysis data.

        Returns:
            DataFrame with demand data, or None if empty
        """
        return self._data

    def update_analysis(self, df: pd.DataFrame) -> None:
        """
        Store analysis data.

        Args:
            df: DataFrame to store
        """
        self._data = df