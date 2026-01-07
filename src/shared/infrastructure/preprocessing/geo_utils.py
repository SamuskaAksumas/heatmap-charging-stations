"""
Geographic utility functions for preprocessing.

Contains functions for geometry handling and PLZ-based spatial operations.
"""
import pandas as pd
import geopandas as gpd


def sort_by_plz_add_geometry(dfr, dfg, pdict):
    """
    Sort dataframe by PLZ and add geometry from geodata.

    Args:
        dfr: Input dataframe with PLZ column.
        dfg: Geodata dataframe with PLZ and geometry columns.
        pdict: Configuration dictionary with geocode key.

    Returns:
        GeoDataFrame sorted by PLZ with geometry column added.
    """
    dframe = dfr.copy()
    df_geo = dfg.copy()

    sorted_df = dframe\
        .sort_values(by='PLZ')\
        .reset_index(drop=True)\
        .sort_index()

    sorted_df2 = sorted_df.merge(df_geo, on=pdict["geocode"], how='left')
    sorted_df3 = sorted_df2.dropna(subset=['geometry'])

    # Geometry column may already contain shapely geometry objects or WKT strings.
    try:
        # If values are WKT strings, this will succeed.
        sorted_df3['geometry'] = gpd.GeoSeries.from_wkt(sorted_df3['geometry'])
    except Exception:
        # Otherwise, assume they're already geometry objects and construct GeoSeries directly.
        sorted_df3['geometry'] = gpd.GeoSeries(sorted_df3['geometry'])

    ret = gpd.GeoDataFrame(sorted_df3, geometry='geometry')

    return ret


def get_plz_centroid(plz, df_geo):
    """
    Get centroid coordinates for a PLZ.

    Args:
        plz: Postal code (string or int).
        df_geo: Geodata dataframe with PLZ and geometry columns.

    Returns:
        Tuple of (latitude, longitude) or (None, None) if not found.
    """
    try:
        plz_int = int(plz)
        geo_row = df_geo[df_geo['PLZ'] == plz_int]
        if not geo_row.empty:
            geom = geo_row.iloc[0]['geometry']
            if hasattr(geom, 'centroid'):
                return geom.centroid.y, geom.centroid.x
    except:
        pass
    return None, None
