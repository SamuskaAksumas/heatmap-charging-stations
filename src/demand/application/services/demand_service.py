"""DemandService - Coordinates demand analysis workflow."""
from typing import Optional
import pandas as pd

from src.demand.domain.events.demand_calculated import on_demand_calculated
from src.demand.infrastructure.repositories.demand_repository import DemandRepository


class DemandService:
    """Application service for demand analysis operations."""

    def __init__(self, repository: DemandRepository) -> None:
        self._repository = repository

    def calculate_demand(
        self,
        df_stations_count: pd.DataFrame,
        df_residents_geo: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate demand for all PLZ areas and cache results."""
        results = on_demand_calculated(df_stations_count, df_residents_geo)
        self._repository.update_analysis(results)
        return results

    def get_latest_results(self) -> Optional[pd.DataFrame]:
        """Retrieve cached demand analysis results."""
        return self._repository.get_analysis()