"""Geographic utilities for PLZ-based spatial operations."""
import geopandas as gpd


def sort_by_plz_add_geometry(dfr, dfg, pdict):
    """Sort by PLZ and merge with geodata geometry."""
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
    """Get centroid (lat, lon) for a PLZ from geodata."""
    try:
        plz_int = int(plz)
        geo_row = df_geo[df_geo['PLZ'] == plz_int]
        if not geo_row.empty:
            geom = geo_row.iloc[0]['geometry']
            if hasattr(geom, 'centroid'):
                return geom.centroid.y, geom.centroid.x
    except Exception:
        pass
    return None, None
