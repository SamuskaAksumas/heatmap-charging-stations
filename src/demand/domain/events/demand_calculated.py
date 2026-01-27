<<<<<<< HEAD
"""Calculate demand score per PLZ based on residents and charging stations."""
import numpy as np
import pandas as pd


def on_demand_calculated(df_stations_count: pd.DataFrame, df_residents_geo: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate demand for charging stations per PLZ.

    Demand = Residents / Stations (higher = more need for stations)
    If no stations exist, demand equals the resident count.

    Args:
        df_stations_count: DataFrame with PLZ and Number (station count)
        df_residents_geo: DataFrame with PLZ, Einwohner, and geometry

    Returns:
        DataFrame with added 'demand' column
    """
    result = df_residents_geo.copy()
    stations = df_stations_count[['PLZ', 'Number']].copy()

    # Merge stations with residents
    result = result.merge(stations, on='PLZ', how='left')
    result['Number'] = result['Number'].fillna(0).astype(int)

    # Calculate demand: residents per station (or just residents if no stations)
    result['demand'] = result.apply(
        lambda row: row['Einwohner'] / row['Number'] if row['Number'] > 0 else float(row['Einwohner']),
        axis=1
    )
    result['demand'] = result['demand'].replace([np.inf, -np.inf], np.nan).fillna(0)

    return result
=======
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class DemandCalculatedEvent:
    """
    Domain Event: Represents the successful completion of a demand analysis.
    This fulfills the DDD requirement of separating 'State Changes' from 'Notifications'.
    """
    area_count: int
    occurred_at: datetime = field(default_factory=datetime.now)
    status: str = "COMPLETED"

    def __str__(self):
        return f"DemandCalculatedEvent: Analysis of {self.area_count} areas finished at {self.occurred_at}."
>>>>>>> 607d696 (Revamp project structure using DDD approach)
