"""
Domain services for geography.
"""
from typing import List, Optional
from .entities import PostalArea, Coordinate
from .repository import PostalAreaRepository



class GeographyService:
    """Domain service for geographic operations."""

    def __init__(self, repository: PostalAreaRepository):
        self.repository = repository

    def get_centroid_for_postal_code(self, postal_code: str):
        """Get the centroid coordinate for a postal code via repository."""
        return self.repository.get_centroid_for_postal_code(postal_code)

    def get_berlin_postal_areas(self) -> List[PostalArea]:
        """Get all postal areas in Berlin (PLZ 10000-14200)."""
        return self.repository.get_postal_codes_in_range("10000", "14200")

    def find_postal_code_for_location(self, coordinate: Coordinate) -> Optional[str]:
        """Find the postal code that contains the given coordinate."""
        postal_area = self.repository.find_postal_area_for_coordinate(coordinate)
        return postal_area.postal_code if postal_area else None

    def validate_berlin_postal_code(self, postal_code: str) -> bool:
        """Validate if a postal code is within Berlin's range."""
        try:
            code_int = int(postal_code)
            return 10000 <= code_int <= 14200
        except ValueError:
            return False

    def get_centroid_coordinates(self, postal_codes: List[str]) -> dict:
        """Get centroid coordinates for multiple postal codes."""
        centroids = {}
        for postal_code in postal_codes:
            centroid = self.repository.get_centroid_for_postal_code(postal_code)
            if centroid:
                centroids[postal_code] = centroid
        return centroids

    def calculate_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        """Calculate approximate distance between two coordinates in kilometers."""
        # Haversine formula for distance calculation
        import math

        lat1, lon1 = math.radians(coord1.latitude), math.radians(coord1.longitude)
        lat2, lon2 = math.radians(coord2.latitude), math.radians(coord2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        # Earth's radius in kilometers
        radius = 6371
        return radius * c