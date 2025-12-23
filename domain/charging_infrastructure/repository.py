"""
Repository interfaces for charging infrastructure domain.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd

from .entities import ChargingStation


class ChargingStationRepository(ABC):
    """Abstract repository for charging station data access."""

    @abstractmethod
    def get_all(self) -> List[ChargingStation]:
        """Get all charging stations."""
        pass

    @abstractmethod
    def get_by_postal_code(self, postal_code: str) -> List[ChargingStation]:
        """Get charging stations by postal code."""
        pass

    @abstractmethod
    def get_by_id(self, station_id: str) -> Optional[ChargingStation]:
        """Get a charging station by ID."""
        pass

    @abstractmethod
    def count_by_postal_code(self, postal_code: str) -> int:
        """Count charging stations in a postal code area."""
        pass

    @abstractmethod
    def get_postal_codes_with_stations(self) -> List[str]:
        """Get all postal codes that have charging stations."""
        pass