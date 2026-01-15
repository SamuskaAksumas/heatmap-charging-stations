"""Domain Events for the Shared bounded context."""
from .residents_processed import process_residents_data
from .stations_processed import on_stations_processed

__all__ = [
    "process_residents_data",
    "on_stations_processed",
]
