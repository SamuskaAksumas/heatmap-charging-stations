"""
Repository: DemandRepository

Infrastructure layer component for persisting demand analysis data.
"""
from typing import Optional
import pandas as pd


class DemandRepository:
    """
    Repository for storing and retrieving demand analysis results.

    Uses in-memory storage for simplicity. Can be extended to use
    SQLite or other persistence mechanisms.
    """

    def __init__(self) -> None:
        """Initialize the repository with empty storage."""
        self._current_analysis: Optional[pd.DataFrame] = None

    def get_analysis(self) -> Optional[pd.DataFrame]:
        """
        Retrieve the current demand analysis results.

        Returns:
            DataFrame with demand results, or None if no data stored
        """
        return self._current_analysis

    def update_analysis(self, df: pd.DataFrame) -> None:
        """
        Store new demand analysis results.

        Args:
            df: DataFrame containing demand analysis data
        """
        self._current_analysis = df