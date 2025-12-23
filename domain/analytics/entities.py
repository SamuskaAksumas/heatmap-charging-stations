"""
Domain entities and value objects for analytics.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class DemandMetrics:
    """Value object representing demand calculation results."""
    residents_per_station: float
    demand_level: str  # "low", "medium", "high", "critical"
    station_count: int
    resident_count: int

    def __post_init__(self):
        if self.residents_per_station < 0:
            raise ValueError("Residents per station cannot be negative")
        if self.station_count < 0:
            raise ValueError("Station count cannot be negative")
        if self.resident_count < 0:
            raise ValueError("Resident count cannot be negative")


@dataclass
class DemandAnalysis:
    """Entity representing demand analysis for a postal area."""
    postal_code: str
    metrics: DemandMetrics
    calculated_at: Optional[str] = None  # ISO datetime string

    def __post_init__(self):
        if not self.postal_code:
            raise ValueError("Postal code cannot be empty")

    def get_demand_score(self) -> float:
        """Get a numerical demand score (higher = more demand)."""
        return self.metrics.residents_per_station

    def is_high_demand(self) -> bool:
        """Check if this area has high charging demand."""
        return self.metrics.demand_level in ["high", "critical"]

    def needs_more_stations(self) -> bool:
        """Determine if more charging stations are needed."""
        return self.get_demand_score() > 50  # Threshold for needing more stations


@dataclass(frozen=True)
class HeatmapData:
    """Value object representing heatmap visualization data."""
    postal_code: str
    value: float
    color_intensity: float  # 0-1 scale for coloring

    def __post_init__(self):
        if not self.postal_code:
            raise ValueError("Postal code cannot be empty")
        if not (0 <= self.color_intensity <= 1):
            raise ValueError("Color intensity must be between 0 and 1")