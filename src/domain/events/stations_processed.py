from core import methods as m1

def on_stations_processed(df_lstat, df_geodat_plz, pdict):
    """Orchestrates the original station preprocessing."""
    gdf_lstat3 = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    df_lstat2 = m1.count_plz_occurrences(gdf_lstat3)
    return df_lstat2
