"""
Repository interfaces for geography domain.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import geopandas as gpd

from .entities import PostalArea, Coordinate


class PostalAreaRepository(ABC):
    """Abstract repository for postal area data access."""

    @abstractmethod
    def get_all(self) -> List[PostalArea]:
        """Get all postal areas."""
        pass

    @abstractmethod
    def get_by_postal_code(self, postal_code: str) -> Optional[PostalArea]:
        """Get a postal area by postal code."""
        pass

    @abstractmethod
    def get_postal_codes_in_range(self, min_code: str, max_code: str) -> List[PostalArea]:
        """Get postal areas within a postal code range."""
        pass

    @abstractmethod
    def find_postal_area_for_coordinate(self, coordinate: Coordinate) -> Optional[PostalArea]:
        """Find which postal area contains the given coordinate."""
        pass

    @abstractmethod
    def get_centroid_for_postal_code(self, postal_code: str) -> Optional[Coordinate]:
        """Get the centroid coordinate for a postal code."""
        pass

    @abstractmethod
    def get_geodataframe(self) -> gpd.GeoDataFrame:
        """Get the underlying GeoDataFrame for spatial operations."""
        pass