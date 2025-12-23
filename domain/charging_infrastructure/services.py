"""
Domain services for charging infrastructure.
"""
from typing import List, Dict
from .entities import ChargingStation
from .repository import ChargingStationRepository


class ChargingStationService:
    """Domain service for charging station operations."""

    def __init__(self, repository: ChargingStationRepository):
        self.repository = repository

    def get_stations_summary_by_postal_code(self) -> Dict[str, int]:
        """Get a summary of charging stations count by postal code."""
        summary = {}
        all_stations = self.repository.get_all()

        for station in all_stations:
            postal_code = station.postal_code
            summary[postal_code] = summary.get(postal_code, 0) + 1

        return summary

    def calculate_total_capacity_by_postal_code(self) -> Dict[str, float]:
        """Calculate total charging capacity by postal code."""
        capacity_by_plz = {}
        all_stations = self.repository.get_all()

        for station in all_stations:
            postal_code = station.postal_code
            capacity = station.capacity.power_kw
            capacity_by_plz[postal_code] = capacity_by_plz.get(postal_code, 0) + capacity

        return capacity_by_plz

    def find_stations_in_area(self, postal_codes: List[str]) -> List[ChargingStation]:
        """Find all charging stations in given postal code areas."""
        stations = []
        for postal_code in postal_codes:
            stations.extend(self.repository.get_by_postal_code(postal_code))
        return stations