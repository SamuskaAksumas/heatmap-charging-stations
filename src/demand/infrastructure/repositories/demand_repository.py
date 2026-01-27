from typing import Optional
from src.demand.domain.aggregates.demand_aggregate import DemandAggregate

class DemandRepository:
    """Infrastructure implementation for Aggregate persistence."""
    def __init__(self) -> None:
        self._storage: dict = {}

    def save_analysis(self, aggregate: DemandAggregate) -> None:
        self._storage[aggregate.aggregate_id] = aggregate

    def get_analysis(self, aggregate_id: str = "berlin_charging_analysis") -> Optional[DemandAggregate]:
        return self._storage.get(aggregate_id)
