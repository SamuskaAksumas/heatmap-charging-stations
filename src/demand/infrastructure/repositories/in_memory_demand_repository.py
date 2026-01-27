import pandas as pd
from typing import Optional

class InMemoryDemandRepository:
    """Mock repository for testing the Demand Bounded Context."""
    
    def __init__(self):
        # We use a dictionary to simulate a database table
        self._storage = {}

    def save_analysis(self, df: pd.DataFrame, aggregate_id: str = "berlin_current_analysis"):
        """Saves the calculated dataframe to memory."""
        self._storage[aggregate_id] = df

    def get_analysis(self, aggregate_id: str = "berlin_current_analysis") -> Optional[pd.DataFrame]:
        """Retrieves the dataframe from memory."""
        return self._storage.get(aggregate_id)
