"""
Domain entities and value objects for geography.
"""
from dataclasses import dataclass
from typing import Optional, Any
import geopandas as gpd


@dataclass(frozen=True)
class Coordinate:
    """Value object representing geographic coordinates."""
    latitude: float
    longitude: float

    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")


@dataclass
class PostalArea:
    """Entity representing a postal code area."""
    postal_code: str
    geometry: Any  # GeoPandas geometry object
    centroid: Optional[Coordinate] = None
    population: Optional[int] = None
    area_sq_km: Optional[float] = None

    def __post_init__(self):
        if not self.postal_code:
            raise ValueError("Postal code cannot be empty")
        if not hasattr(self.geometry, '__geo_interface__'):
            raise ValueError("Geometry must be a valid GeoPandas geometry object")

    def calculate_centroid(self) -> Coordinate:
        """Calculate the centroid of this postal area."""
        if self.geometry is None:
            raise ValueError("Geometry is required to calculate centroid")

        centroid = self.geometry.centroid
        return Coordinate(latitude=centroid.y, longitude=centroid.x)

    def contains_point(self, point: Coordinate) -> bool:
        """Check if a point is within this postal area."""
        from shapely.geometry import Point
        point_geom = Point(point.longitude, point.latitude)
        return self.geometry.contains(point_geom)

    def get_area(self) -> float:
        """Get the area of this postal area in square kilometers."""
        if self.area_sq_km is not None:
            return self.area_sq_km

        # Calculate area (assuming geometry is in appropriate CRS)
        # This is a simplified calculation - in reality you'd want proper CRS handling
        area_sqm = self.geometry.area
        self.area_sq_km = area_sqm / 1_000_000  # Convert to km²
        return self.area_sq_km