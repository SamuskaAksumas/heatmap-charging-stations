from dataclasses import dataclass
from src.shared.domain.value_objects.postal_code import PostalCode

@dataclass
class LocationStats:
    """Entity: Represents a geographic area (PLZ) with its specific stats."""
    plz: PostalCode
    count: int
    lat: float
    lon: float