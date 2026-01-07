"""
Event: DemandCalculatedEvent

Raised when demand calculation is completed for all postal code areas.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class DemandCalculatedEvent(DomainEvent):
    """
    Event raised when demand calculation is completed.

    This event captures the results of a demand calculation run,
    including summary statistics and top demand areas.

    Attributes:
        total_areas: Number of postal code areas analyzed.
        total_residents: Total number of residents across all areas.
        total_stations: Total number of charging stations.
        average_demand: Average demand score across all areas.
        high_demand_count: Number of areas with high demand.
        top_demand_areas: List of PLZ codes with highest demand.

    Example:
        >>> event = DemandCalculatedEvent(
        ...     total_areas=190,
        ...     total_residents=3900000,
        ...     total_stations=3657,
        ...     average_demand=1066.0,
        ...     high_demand_count=15,
        ...     top_demand_areas=["12309", "10247", "13187"]
        ... )
    """
    total_areas: int = 0
    total_residents: int = 0
    total_stations: int = 0
    average_demand: float = 0.0
    high_demand_count: int = 0
    top_demand_areas: tuple = field(default_factory=tuple)  # Use tuple for immutability

    def to_dict(self) -> dict:
        """
        Convert event to dictionary for serialization.

        Returns:
            Dictionary representation of the event.
        """
        base = super().to_dict()
        base.update({
            'total_areas': self.total_areas,
            'total_residents': self.total_residents,
            'total_stations': self.total_stations,
            'average_demand': self.average_demand,
            'high_demand_count': self.high_demand_count,
            'top_demand_areas': list(self.top_demand_areas),
        })
        return base

    @classmethod
    def from_results(cls, results_df) -> "DemandCalculatedEvent":
        """
        Factory method to create event from calculation results DataFrame.

        Args:
            results_df: DataFrame with demand calculation results.

        Returns:
            DemandCalculatedEvent with computed statistics.
        """
        total_areas = len(results_df)
        total_residents = int(results_df['Einwohner'].sum()) if 'Einwohner' in results_df.columns else 0
        total_stations = int(results_df['count'].sum()) if 'count' in results_df.columns else 0
        average_demand = float(results_df['demand'].mean()) if 'demand' in results_df.columns else 0.0

        # Count high demand areas (demand > 10000)
        high_demand_count = int((results_df['demand'] > 10000).sum()) if 'demand' in results_df.columns else 0

        # Get top 5 demand areas
        if 'demand' in results_df.columns and 'PLZ' in results_df.columns:
            top_areas = results_df.nlargest(5, 'demand')['PLZ'].astype(str).tolist()
        else:
            top_areas = []

        return cls(
            total_areas=total_areas,
            total_residents=total_residents,
            total_stations=total_stations,
            average_demand=average_demand,
            high_demand_count=high_demand_count,
            top_demand_areas=tuple(top_areas),
        )
