"""
Domain entities and value objects for charging infrastructure.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class Location:
    """Value object representing a geographic location."""
    latitude: float
    longitude: float

    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")


@dataclass(frozen=True)
class Capacity:
    """Value object representing charging capacity."""
    power_kw: float
    connector_type: str

    def __post_init__(self):
        if self.power_kw <= 0:
            raise ValueError("Power must be positive")


@dataclass
class ChargingStation:
    """Entity representing a charging station."""
    station_id: str
    location: Location
    capacity: Capacity
    postal_code: str
    address: Optional[str] = None
    operator: Optional[str] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if not self.station_id:
            raise ValueError("Station ID cannot be empty")
        if not self.postal_code:
            raise ValueError("Postal code cannot be empty")

    def update_location(self, new_location: Location) -> None:
        """Update the station's location."""
        self.location = new_location
        self.last_updated = datetime.now()

    def update_capacity(self, new_capacity: Capacity) -> None:
        """Update the station's capacity."""
        self.capacity = new_capacity
        self.last_updated = datetime.now()