"""
Entity: DemandResult

Rich domain entity representing the demand analysis result for a postal code area.
Contains validation and business logic following DDD principles.
"""
from dataclasses import dataclass
from typing import Optional, Any

from src.demand.domain.exceptions import InvalidDemandDataException


# Demand thresholds for categorization
DEMAND_THRESHOLD_HIGH = 10000.0
DEMAND_THRESHOLD_MEDIUM = 5000.0
DEMAND_THRESHOLD_LOW = 1000.0


@dataclass
class DemandResult:
    """
    Rich Entity representing demand analysis for a postal code area.

    This entity encapsulates the demand calculation logic and provides
    methods for categorizing demand levels according to business rules.

    Attributes:
        plz: The postal code (PLZ)
        demand: The calculated demand score (residents per station)
        einwohner: Number of residents in the area
        count: Number of charging stations in the area
        geometry: Geographic boundary of the area (optional)

    Domain Rules:
        - Demand = residents / stations (or full population if no stations)
        - Higher demand = more need for new charging stations
        - Zero stations indicates critical demand

    Example:
        >>> result = DemandResult(plz="10115", demand=5000.0, einwohner=10000, count=2)
        >>> result.is_high_demand()  # False
        >>> result.get_demand_category()  # "medium"
    """
    plz: str
    demand: float
    einwohner: int = 0
    count: int = 0
    geometry: Optional[Any] = None

    def __post_init__(self) -> None:
        """Validate the demand result upon creation."""
        self._validate()

    def _validate(self) -> None:
        """
        Validate all fields according to domain rules.

        Raises:
            InvalidDemandDataException: If any validation fails.
        """
        # Validate PLZ
        if not self.plz:
            raise InvalidDemandDataException("PLZ cannot be empty")

        # Validate einwohner (residents)
        if self.einwohner < 0:
            raise InvalidDemandDataException(
                f"Residents count cannot be negative: {self.einwohner}"
            )

        # Validate count (stations)
        if self.count < 0:
            raise InvalidDemandDataException(
                f"Station count cannot be negative: {self.count}"
            )

        # Validate demand score
        if self.demand < 0:
            raise InvalidDemandDataException(
                f"Demand score cannot be negative: {self.demand}"
            )

    @property
    def demand_score(self) -> float:
        """
        Calculate the demand score.

        Formula: residents / stations (or residents if no stations)

        Returns:
            float: The demand score
        """
        if self.count > 0:
            return self.einwohner / self.count
        return float(self.einwohner)

    def recalculate_demand(self) -> float:
        """
        Recalculate and update the demand score based on current values.

        Returns:
            float: The updated demand score.
        """
        self.demand = self.demand_score
        return self.demand

    def is_high_demand(self) -> bool:
        """
        Check if this area has high demand for charging stations.

        High demand is defined as more than 10,000 residents per station.

        Returns:
            True if demand is high (> 10,000).
        """
        return self.demand > DEMAND_THRESHOLD_HIGH

    def is_medium_demand(self) -> bool:
        """
        Check if this area has medium demand for charging stations.

        Medium demand is defined as 5,000-10,000 residents per station.

        Returns:
            True if demand is medium (5,000-10,000).
        """
        return DEMAND_THRESHOLD_MEDIUM < self.demand <= DEMAND_THRESHOLD_HIGH

    def is_low_demand(self) -> bool:
        """
        Check if this area has low demand for charging stations.

        Low demand is defined as 1,000-5,000 residents per station.

        Returns:
            True if demand is low (1,000-5,000).
        """
        return DEMAND_THRESHOLD_LOW < self.demand <= DEMAND_THRESHOLD_MEDIUM

    def is_satisfied(self) -> bool:
        """
        Check if this area has sufficient charging station coverage.

        Satisfied means fewer than 1,000 residents per station.

        Returns:
            True if demand is satisfied (< 1,000).
        """
        return self.demand <= DEMAND_THRESHOLD_LOW

    def has_no_stations(self) -> bool:
        """
        Check if this area has zero charging stations.

        Returns:
            True if there are no stations in the area.
        """
        return self.count == 0

    def get_demand_category(self) -> str:
        """
        Get the demand category as a human-readable string.

        Returns:
            One of: 'critical', 'high', 'medium', 'low', 'satisfied'
        """
        if self.has_no_stations():
            return 'critical'
        elif self.is_high_demand():
            return 'high'
        elif self.is_medium_demand():
            return 'medium'
        elif self.is_low_demand():
            return 'low'
        else:
            return 'satisfied'

    def get_priority_rank(self) -> int:
        """
        Get a priority rank for infrastructure planning.

        Lower rank = higher priority for new stations.

        Returns:
            Priority rank (1=critical, 2=high, 3=medium, 4=low, 5=satisfied)
        """
        category_ranks = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4,
            'satisfied': 5,
        }
        return category_ranks.get(self.get_demand_category(), 5)

    def to_dict(self) -> dict:
        """
        Convert entity to dictionary for persistence or serialization.

        Returns:
            Dictionary representation of the demand result.
        """
        return {
            'plz': self.plz,
            'demand': self.demand,
            'einwohner': self.einwohner,
            'count': self.count,
            'category': self.get_demand_category(),
            'priority': self.get_priority_rank(),
        }

    @classmethod
    def from_data(
        cls,
        plz: str,
        einwohner: int,
        count: int,
        geometry: Any = None
    ) -> "DemandResult":
        """
        Factory method to create DemandResult with automatic demand calculation.

        Args:
            plz: The postal code.
            einwohner: Number of residents.
            count: Number of charging stations.
            geometry: Geographic boundary (optional).

        Returns:
            DemandResult with calculated demand score.
        """
        demand = einwohner / count if count > 0 else float(einwohner)
        return cls(
            plz=plz,
            demand=demand,
            einwohner=einwohner,
            count=count,
            geometry=geometry,
        )
