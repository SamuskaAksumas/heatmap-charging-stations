"""Preprocessing for charging station data (Ladesaeulenregister.csv)."""
import pandas as pd
from src.shared.infrastructure.utils import timer
from .geo_utils import sort_by_plz_add_geometry


@timer
def preprop_lstat(dfr, dfg, pdict):
    """Preprocess station data: filter Berlin, add geometry."""
    dframe = dfr.copy()
    df_geo = dfg.copy()

    dframe2 = dframe.loc[:, ['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']]
    dframe2.rename(columns={"Nennleistung Ladeeinrichtung [kW]": "KW", "Postleitzahl": "PLZ"}, inplace=True)

    # Normalize PLZ to numeric to ensure consistent joins with geodata
    dframe2['PLZ'] = pd.to_numeric(dframe2['PLZ'], errors='coerce')

    # Convert lat/lon to string and replace comma decimals with dot
    dframe2['Breitengrad'] = dframe2['Breitengrad'].astype(str).str.replace(',', '.')
    dframe2['Längengrad'] = dframe2['Längengrad'].astype(str).str.replace(',', '.')

    dframe3 = dframe2[(dframe2["Bundesland"] == 'Berlin') & (dframe2["PLZ"] > 10115) & (dframe2["PLZ"] < 14200)]

    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    return ret


def count_plz_occurrences(df_lstat2):
    """Count charging stations per PLZ, keep geometry."""
    # Group by PLZ and count occurrences, keeping geometry
    result_df = df_lstat2.groupby('PLZ').agg(
        Number=('PLZ', 'count'),
        geometry=('geometry', 'first')
    ).reset_index()

    return result_df
