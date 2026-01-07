"""
Preprocessing functions for resident data.

Contains functions for processing the plz_einwohner data.
"""
from src.shared.infrastructure.utils import timer
from .geo_utils import sort_by_plz_add_geometry


@timer
def preprop_resid(dfr, dfg, pdict):
    """Preprocessing dataframe from plz_einwohner.csv"""
    dframe = dfr.copy()
    df_geo = dfg.copy()

    dframe2 = dframe.loc[:, ['plz', 'einwohner', 'lat', 'lon']]
    dframe2.rename(columns={"plz": "PLZ", "einwohner": "Einwohner", "lat": "Breitengrad", "lon": "Längengrad"}, inplace=True)

    # Convert to string
    dframe2['Breitengrad'] = dframe2['Breitengrad'].astype(str)
    dframe2['Längengrad'] = dframe2['Längengrad'].astype(str)

    # Now replace the commas with periods
    dframe2['Breitengrad'] = dframe2['Breitengrad'].str.replace(',', '.')
    dframe2['Längengrad'] = dframe2['Längengrad'].str.replace(',', '.')

    dframe3 = dframe2[
        (dframe2["PLZ"] > 10000) &
        (dframe2["PLZ"] < 14200)]

    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)

    return ret
