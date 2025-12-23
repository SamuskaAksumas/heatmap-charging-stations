"""
Domain services for demographics bounded context.
"""
from typing import Dict, List, Optional
from domain.demographics.entities import DemographicArea
from domain.demographics.repository import DemographicRepository


class DemographicsService:
    """Domain service for demographic operations."""

    def __init__(self, repository: DemographicRepository):
        self.repository = repository

    def get_population_for_postal_code(self, postal_code: str) -> Optional[int]:
        """Get population for a specific postal code."""
        area = self.repository.get_by_postal_code(postal_code)
        return area.population if area else None

    def get_all_demographic_areas(self) -> List[DemographicArea]:
        """Get all demographic areas."""
        return self.repository.get_all()

    def calculate_population_density(self, postal_code: str) -> Optional[float]:
        """Calculate population density for a postal code area."""
        area = self.repository.get_by_postal_code(postal_code)
        if area and area.area_sq_km and area.area_sq_km > 0:
            return area.population / area.area_sq_km
        return None

    def get_areas_by_population_range(self, min_pop: int, max_pop: int) -> List[DemographicArea]:
        """Get areas within a population range."""
        all_areas = self.repository.get_all()
        return [area for area in all_areas if min_pop <= area.population <= max_pop]

    def get_total_population(self) -> int:
        """Get total population across all areas."""
        all_areas = self.repository.get_all()
        return sum(area.population for area in all_areas if area.population)