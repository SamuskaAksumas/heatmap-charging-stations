from typing import Optional
import pandas as pd

from src.demand.domain.aggregates.demand_aggregate import DemandAggregate
from src.demand.infrastructure.repositories.demand_repository import DemandRepository


class DemandService:
    """
    Application Service for the Demand bounded context.

    Coordinates use cases and delegates business logic
    to the DemandAggregate.
    """

    AGGREGATE_ID = "berlin_current_analysis"

    def __init__(self, repository: DemandRepository) -> None:
        self._repository = repository

    def calculate_demand(
        self,
        df_stations: pd.DataFrame,
        df_residents: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Use case: Calculate demand heatmap for Berlin.
        """
        # Create Aggregate Root
        aggregate = DemandAggregate(aggregate_id=self.AGGREGATE_ID)

        # Delegate domain logic to the aggregate
        results_df = aggregate.calculate_demand_map(
            df_stations=df_stations,
            df_residents=df_residents
        )

        # Persist aggregate state
        self._repository.save_analysis(aggregate)

        return results_df

    def get_latest_results(self) -> Optional[pd.DataFrame]:
        """
        Use case: Retrieve the latest calculated demand map.
        """
        aggregate = self._repository.get_analysis(self.AGGREGATE_ID)

        if aggregate is None:
            return None

        return aggregate.raw_results
