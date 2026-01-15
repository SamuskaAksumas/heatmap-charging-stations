"""Process charging station data and count per PLZ."""
from src.shared.infrastructure.preprocessing import preprop_lstat, count_plz_occurrences


def on_stations_processed(df_lstat, df_geodat_plz, pdict):
    """Preprocess stations and count per PLZ."""
    gdf_lstat3 = preprop_lstat(df_lstat, df_geodat_plz, pdict)
    return count_plz_occurrences(gdf_lstat3)
