"""SharedService - Orchestrates shared data processing."""
from src.shared.domain.events.residents_processed import process_residents_data
from src.shared.domain.events.stations_processed import on_stations_processed


class SharedService:
    """Service for processing shared data (residents, stations)."""

    def __init__(self, repository):
        self.repository = repository

    def get_processed_residents(self, path, df_geo, datasets_dir):
        """Process resident data from Excel/CSV."""
        return process_residents_data(path, df_geo, datasets_dir)

    def get_processed_stations(self, path_stations, df_geo, pdict):
        """Process and count stations per PLZ."""
        raw_stations = self.repository.read_csv_with_header_detection(path_stations)
        if raw_stations is not None:
            return on_stations_processed(raw_stations, df_geo, pdict)
        return None