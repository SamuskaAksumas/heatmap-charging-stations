from src.shared.infrastructure.preprocessing import preprop_lstat, count_plz_occurrences


def on_stations_processed(df_lstat, df_geodat_plz, pdict):
    """Orchestrates the original station preprocessing."""
    gdf_lstat3 = preprop_lstat(df_lstat, df_geodat_plz, pdict)
    df_lstat2 = count_plz_occurrences(gdf_lstat3)
    return df_lstat2
