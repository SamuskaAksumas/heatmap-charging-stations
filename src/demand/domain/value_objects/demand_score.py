"""
Value Object: DemandScore

Represents the demand score for a location, calculated as residents per charging station.
"""
from dataclasses import dataclass
from src.demand.domain.exceptions import InvalidDemandDataException


@dataclass(frozen=True)
class DemandScore:
    """
    Value Object representing a demand score.

    The demand score represents the number of residents per charging station
    in a given area. Higher values indicate higher demand for new stations.

    Attributes:
        value: The demand score (residents per station). Must be >= 0.

    Raises:
        InvalidDemandDataException: If the score is negative.

    Example:
        >>> score = DemandScore(500.0)  # 500 residents per station
        >>> score = DemandScore(-1)  # Raises InvalidDemandDataException
    """
    value: float

    def __post_init__(self) -> None:
        """Validate the demand score upon creation."""
        if self.value < 0:
            raise InvalidDemandDataException(
                f"Demand score cannot be negative: {self.value}"
            )

    def __str__(self) -> str:
        """Return formatted demand score."""
        return f"{self.value:.2f}"

    def is_high_demand(self, threshold: float = 5000.0) -> bool:
        """
        Check if this score indicates high demand.

        Args:
            threshold: The threshold above which demand is considered high.
                      Defaults to 5000 (residents per station).

        Returns:
            True if the score exceeds the threshold.
        """
        return self.value > threshold

    def is_zero_stations(self) -> bool:
        """
        Check if this score represents an area with zero stations.

        In the calculation, zero stations means the score equals
        the full population (residents / 0 is treated as residents).

        Returns:
            True if there are no stations in the area.
        """
        # This is a heuristic - very high scores typically indicate no stations
        return self.value > 10000.0

    @staticmethod
    def calculate(residents: int, stations: int) -> "DemandScore":
        """
        Factory method to calculate demand score from raw values.

        Args:
            residents: Number of residents in the area.
            stations: Number of charging stations in the area.

        Returns:
            DemandScore with calculated value.

        Raises:
            InvalidDemandDataException: If residents is negative.
        """
        if residents < 0:
            raise InvalidDemandDataException(
                f"Residents count cannot be negative: {residents}"
            )

        if stations <= 0:
            # No stations = demand equals full population
            return DemandScore(float(residents))

        return DemandScore(residents / stations)
