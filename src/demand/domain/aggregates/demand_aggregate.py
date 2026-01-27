from typing import List
import pandas as pd

from src.shared.domain.aggregates.aggregate_root import AggregateRoot
from src.demand.domain.entities.demand_entity import DemandEntity
from src.demand.domain.value_objects.demand_score import DemandScore
from src.demand.domain.value_objects.plz import PLZ


class DemandAggregate(AggregateRoot):
    """
    Aggregate Root for the Demand bounded context.

    Responsible for:
    - Enforcing demand calculation invariants
    - Creating and managing DemandEntity instances
    - Producing a demand map result
    """

    def __init__(self, aggregate_id: str):
        super().__init__(aggregate_id)
        self._demands: List[DemandEntity] = []
        self._raw_results: pd.DataFrame | None = None

    def calculate_demand_map(
        self,
        df_stations: pd.DataFrame,
        df_residents: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Core domain logic:
        Calculates demand per PLZ based on residents and stations.
        """
        merged = df_residents.merge(
            df_stations[['PLZ', 'Number']],
            on='PLZ',
            how='left'
        )

        merged['Number'] = merged['Number'].fillna(0).astype(int)

        result_rows = []

        for _, row in merged.iterrows():
            # Create Value Objects (validation happens here)
            plz = PLZ(row['PLZ'])
            score = DemandScore.from_raw(
                residents=row['Einwohner'],
                stations=row['Number']
            )

            # Create Entity
            demand = DemandEntity(plz=plz, score=score)
            self._demands.append(demand)

            # Prepare output row
            row_dict = row.to_dict()
            row_dict['demand'] = score.value
            result_rows.append(row_dict)

        self._raw_results = pd.DataFrame(result_rows)
        return self._raw_results

    def get_demands(self) -> List[DemandEntity]:
        """
        Exposes demand entities in a controlled way.
        """
        return list(self._demands)

    @property
    def raw_results(self) -> pd.DataFrame | None:
        """
        Read-only access to calculation results.
        """
        return self._raw_results
