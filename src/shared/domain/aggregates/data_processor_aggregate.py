import pandas as pd
from typing import List
from src.shared.domain.entities.location_stats import LocationStats
from src.shared.domain.value_objects.postal_code import PostalCode

class DataProcessorAggregate:
    """Aggregate Root: Manages the transformation of raw data into Domain Entities."""
    
    def __init__(self):
        self.locations: List[LocationStats] = []

    def process_raw_residents(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Business logic to validate and transform resident data."""
        processed_list = []
        for _, row in df_raw.iterrows():
            try:
                # Use Value Object to validate the PLZ
                plz_vo = PostalCode(str(row['plz']))
                
                entity = LocationStats(
                    plz=plz_vo,
                    count=int(row['einwohner']),
                    lat=float(row['lat']),
                    lon=float(row['lon'])
                )
                self.locations.append(entity)
                processed_list.append(row.to_dict())
            except (ValueError, KeyError):
                continue
        return pd.DataFrame(processed_list)