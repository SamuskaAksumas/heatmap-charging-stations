"""
Application Service: DemandService

Coordinates the demand analysis workflow between domain logic and infrastructure.
"""
from typing import Optional
import pandas as pd

from src.demand.domain.events.demand_calculated import on_demand_calculated
from src.demand.infrastructure.respositories.demand_repository import DemandRepository


class DemandService:
    """
    Application service for demand analysis operations.

    This service coordinates the calculation and retrieval of demand data,
    following the DDD pattern of separating domain logic from infrastructure.
    """

    def __init__(self, repository: DemandRepository) -> None:
        """
        Initialize the DemandService.

        Args:
            repository: The repository for storing demand analysis results
        """
        self._repository = repository

    def calculate_demand(
        self,
        df_stations_count: pd.DataFrame,
        df_residents_geo: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate demand for all postal code areas.

        Coordinates the demand calculation by:
        1. Calling the domain event (on_demand_calculated)
        2. Storing results in the repository

        Args:
            df_stations_count: DataFrame with columns ['PLZ', 'count'/'Number']
            df_residents_geo: DataFrame with columns ['PLZ', 'Einwohner', 'geometry']

        Returns:
            DataFrame with demand analysis results
        """
        # 1. Call domain logic (Process)
        results = on_demand_calculated(df_stations_count, df_residents_geo)

        # 2. Store in repository for later retrieval
        self._repository.update_analysis(results)

        return results

    def get_latest_results(self) -> Optional[pd.DataFrame]:
        """
        Retrieve the latest demand analysis results.

        Returns:
            DataFrame with demand results, or None if no analysis exists
        """
        return self._repository.get_analysis()