"""
Domain entities and value objects for demographics.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PopulationData:
    """Value object representing population statistics."""
    total_population: int
    population_density: Optional[float] = None  # people per km²

    def __post_init__(self):
        if self.total_population < 0:
            raise ValueError("Population cannot be negative")


@dataclass
class DemographicArea:
    """Entity representing demographic data for a geographic area."""
    postal_code: str
    population_data: PopulationData
    area_sq_km: Optional[float] = None

    def __post_init__(self):
        if not self.postal_code:
            raise ValueError("Postal code cannot be empty")

    def calculate_population_density(self) -> Optional[float]:
        """Calculate population density if area data is available."""
        if self.area_sq_km and self.area_sq_km > 0:
            density = self.population_data.total_population / self.area_sq_km
            # Update the population data with density
            object.__setattr__(self.population_data, 'population_density', density)
            return density
        return None

    @property
    def population(self) -> int:
        """Convenience property for total population."""
        return self.population_data.total_population

    @property
    def density(self) -> Optional[float]:
        """Convenience property for population density."""
        return self.population_data.population_density