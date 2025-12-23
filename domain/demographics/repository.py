"""
Repository interfaces for demographics domain.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from .entities import DemographicArea


class DemographicRepository(ABC):
    """Abstract repository for demographic data access."""

    @abstractmethod
    def get_all(self) -> List[DemographicArea]:
        """Get all demographic areas."""
        pass

    @abstractmethod
    def get_by_postal_code(self, postal_code: str) -> Optional[DemographicArea]:
        """Get demographic data for a specific postal code."""
        pass

    @abstractmethod
    def get_population_by_postal_code(self, postal_code: str) -> Optional[int]:
        """Get population for a specific postal code."""
        pass

    @abstractmethod
    def get_total_population(self) -> int:
        """Get total population across all areas."""
        pass

    @abstractmethod
    def get_postal_codes_by_population_range(self, min_pop: int, max_pop: int) -> List[str]:
        """Get postal codes with population within a range."""
        pass