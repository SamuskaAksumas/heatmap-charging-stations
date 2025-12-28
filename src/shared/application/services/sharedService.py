from src.shared.domain.events.residents_processed import process_residents_data
from src.shared.domain.events.stations_processed import on_stations_processed

class SharedService:
    def __init__(self, repository):
        self.repository = repository

    def get_processed_residents(self, path, df_geo, datasets_dir):
        """Orchestrates resident data cleaning."""
        # Note: You can also handle the logic of finding the .xlsx vs .csv here
        return process_residents_data(path, df_geo, datasets_dir)

    def get_processed_stations(self, path_stations, df_geo, pdict):
        """Orchestrates station counting cleaning."""
        raw_stations = self.repository.read_csv_with_header_detection(path_stations)
        if raw_stations is not None:
            return on_stations_processed(raw_stations, df_geo, pdict)
        return None