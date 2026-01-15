"""DemandRepository - In-memory cache for demand analysis results."""
from typing import Optional
import pandas as pd


class DemandRepository:
    """Repository for caching demand analysis DataFrames."""

    def __init__(self) -> None:
        self._current_analysis: Optional[pd.DataFrame] = None

    def get_analysis(self) -> Optional[pd.DataFrame]:
        """Retrieve cached analysis results."""
        return self._current_analysis

    def update_analysis(self, df: pd.DataFrame) -> None:
        """Store analysis results."""
        self._current_analysis = df
