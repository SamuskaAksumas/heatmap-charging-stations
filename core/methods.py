import pandas                        as pd
import geopandas                     as gpd
import core.HelperTools              as ht

import folium
import numpy as np
# from folium.plugins import HeatMap
import streamlit as st
from streamlit_folium import folium_static
from branca.colormap import LinearColormap



def sort_by_plz_add_geometry(dfr, dfg, pdict): 
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()
    
    sorted_df               = dframe\
        .sort_values(by='PLZ')\
        .reset_index(drop=True)\
        .sort_index()
        
    sorted_df2              = sorted_df.merge(df_geo, on=pdict["geocode"], how ='left')
    sorted_df3              = sorted_df2.dropna(subset=['geometry'])
    
    # Geometry column may already contain shapely geometry objects or WKT strings.
    try:
        # If values are WKT strings, this will succeed.
        sorted_df3['geometry'] = gpd.GeoSeries.from_wkt(sorted_df3['geometry'])
    except Exception:
        # Otherwise, assume they're already geometry objects and construct GeoSeries directly.
        sorted_df3['geometry'] = gpd.GeoSeries(sorted_df3['geometry'])

    ret = gpd.GeoDataFrame(sorted_df3, geometry='geometry')

    return ret
    

# -----------------------------------------------------------------------------
@ht.timer
def preprop_lstat(dfr, dfg, pdict):
    """Preprocessing dataframe from Ladesaeulenregister.csv"""
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
    """Counts loading stations per PLZ"""
    # Group by PLZ and count occurrences, keeping geometry
    result_df = df_lstat2.groupby('PLZ').agg(
        Number=('PLZ', 'count'),
        geometry=('geometry', 'first')
    ).reset_index()
    
    return result_df
    
# -----------------------------------------------------------------------------
# @ht.timer
# def preprop_geb(dfr, pdict):
#     """Preprocessing dataframe from gebaeude.csv"""
#     dframe      = dfr.copy()
    
#     dframe2     = dframe .loc[:,['lag', 'bezbaw', 'geometry']]
#     dframe2.rename(columns      = {"bezbaw":"Gebaeudeart", "lag": "PLZ"}, inplace = True)
    
    
#     # Now, let's filter the DataFrame
#     dframe3 = dframe2[
#         dframe2['PLZ'].notna() &  # Remove NaN values
#         ~dframe2['PLZ'].astype(str).str.contains(',') &  # Remove entries with commas
#         (dframe2['PLZ'].astype(str).str.len() <= 5)  # Keep entries with 5 or fewer characters
#         ]
    
#     # Convert PLZ to numeric, coercing errors to NaN
#     dframe3['PLZ_numeric'] = pd.to_numeric(dframe3['PLZ'], errors='coerce')

#     # Filter for PLZ between 10000 and 14200
#     filtered_df = dframe3[
#         (dframe3['PLZ_numeric'] >= 10000) & 
#         (dframe3['PLZ_numeric'] <= 14200)
#     ]

#     # Drop the temporary numeric column
#     filtered_df2 = filtered_df.drop('PLZ_numeric', axis=1)
    
#     filtered_df3 = filtered_df2[filtered_df2['Gebaeudeart'].isin(['Freistehendes Einzelgebäude', 'Doppelhaushälfte'])]
    
#     filtered_df4 = (filtered_df3\
#                  .assign(PLZ=lambda x: pd.to_numeric(x['PLZ'], errors='coerce'))[['PLZ', 'Gebaeudeart', 'geometry']]
#                  .sort_values(by='PLZ')
#                  .reset_index(drop=True)
#                  )
    
#     ret                     = filtered_df4.dropna(subset=['geometry'])
        
#     return ret
    
# -----------------------------------------------------------------------------
@ht.timer
def preprop_resid(dfr, dfg, pdict):
    """Preprocessing dataframe from plz_einwohner.csv"""
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()    
    
    dframe2               	= dframe.loc[:,['plz', 'einwohner', 'lat', 'lon']]
    dframe2.rename(columns  = {"plz": "PLZ", "einwohner": "Einwohner", "lat": "Breitengrad", "lon": "Längengrad"}, inplace = True)

    # Convert to string
    dframe2['Breitengrad']  = dframe2['Breitengrad'].astype(str)
    dframe2['Längengrad']   = dframe2['Längengrad'].astype(str)

    # Now replace the commas with periods
    dframe2['Breitengrad']  = dframe2['Breitengrad'].str.replace(',', '.')
    dframe2['Längengrad']   = dframe2['Längengrad'].str.replace(',', '.')

    dframe3                 = dframe2[ 
                                            (dframe2["PLZ"] > 10000) &  
                                            (dframe2["PLZ"] < 14200)]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    
    return ret


# -----------------------------------------------------------------------------
@ht.timer
def make_streamlit_electric_Charging_resid(dfr1, dfr2):
    """Makes Streamlit App with Heatmap of Electric Charging Stations and Residents"""
    
    dframe1 = dfr1.copy()
    dframe2 = dfr2.copy()


    # Streamlit app
    st.title('Heatmaps: Electric Charging Stations and Residents')

    # Create a radio button for layer selection
    # layer_selection = st.radio("Select Layer", ("Number of Residents per PLZ (Postal code)", "Number of Charging Stations per PLZ (Postal code)"))

    layer_selection = st.radio("Select Layer", ("Residents", "Charging_Stations", "Demand"))

    # Create a Folium map
    m = folium.Map(location=[52.52, 13.40], zoom_start=10)

    if layer_selection == "Residents":
        
        # Create a color map for Residents
        color_map = LinearColormap(colors=['yellow', 'red'], vmin=dframe2['Einwohner'].min(), vmax=dframe2['Einwohner'].max())

        # Add polygons to the map for Residents
        for idx, row in dframe2.iterrows():
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color_map(row['Einwohner']): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                },
                tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}"
            ).add_to(m)
        
        # Display the dataframe for Residents
        # st.subheader('Residents Data')
        # st.dataframe(gdf_residents2)

    else:
        # Build full PLZ GeoDataFrame (use residents geometries) and merge counts so zeros are explicit
        try:
            full_gdf = dframe2[['PLZ', 'geometry']].merge(dframe1[['PLZ', 'Number']], on='PLZ', how='left')
            full_gdf['Number'] = full_gdf['Number'].fillna(0).astype(int)
        except Exception:
            full_gdf = dframe1.copy()
            if 'Number' in full_gdf.columns:
                full_gdf['Number'] = full_gdf['Number'].fillna(0).astype(int)
            else:
                full_gdf['Number'] = 0

        # compute colormap vmin/vmax from full_gdf to include zeros
        vmin = int(full_gdf['Number'].min()) if 'Number' in full_gdf.columns else 0
        vmax = int(full_gdf['Number'].max()) if 'Number' in full_gdf.columns else 1
        color_map = LinearColormap(colors=['yellow', 'red'], vmin=vmin, vmax=vmax)

        for idx, row in full_gdf.iterrows():
            num = int(row['Number']) if 'Number' in row and pd.notna(row['Number']) else 0
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color_map(num): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                },
                tooltip=f"PLZ: {row.get('PLZ', '')}, Number: {num}"
            ).add_to(m)

        # Display the dataframe for Numbers
        # st.subheader('Numbers Data')
        # st.dataframe(gdf_lstat3)

    if layer_selection == "Demand":
        # Build full PLZ GeoDataFrame merging residents + station counts
        try:
            # detect residents column name in the residents GeoDataFrame
            res_col = None
            for c in dframe2.columns:
                if str(c).lower().startswith('einw') or 'einw' in str(c).lower():
                    res_col = c
                    break

            if res_col is not None:
                temp_res = dframe2[['PLZ', 'geometry', res_col]].rename(columns={res_col: 'Einwohner'})
            else:
                temp_res = dframe2[['PLZ', 'geometry']].copy()
                temp_res['Einwohner'] = 0

            full_gdf = temp_res.merge(dframe1[['PLZ', 'Number']], on='PLZ', how='left')
            full_gdf['Number'] = full_gdf['Number'].fillna(0).astype(int)
            full_gdf['Einwohner'] = full_gdf['Einwohner'].fillna(0).astype(int)
        except Exception:
            # Fallback: try to build from available frames
            full_gdf = dframe2.copy()
            if 'PLZ' in dframe1.columns and 'Number' in dframe1.columns:
                counts = dframe1[['PLZ', 'Number']].copy()
                full_gdf = full_gdf.merge(counts, on='PLZ', how='left')
            if 'Number' not in full_gdf.columns:
                full_gdf['Number'] = 0
            if 'Einwohner' not in full_gdf.columns:
                full_gdf['Einwohner'] = 0

        # Demand: residents per station; if zero stations, use residents (marks high demand)
        def compute_demand(row):
            if row['Number'] > 0:
                return row['Einwohner'] / row['Number']
            else:
                # treat zero-station PLZ as high-demand equal to residents
                return float(row['Einwohner'])

        full_gdf['demand'] = full_gdf.apply(compute_demand, axis=1)

        # Replace infinite or NaN
        full_gdf['demand'] = full_gdf['demand'].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Color scaling: vmin 0, vmax = 95th percentile to avoid outlier saturation
        vmax = int(np.nanpercentile(full_gdf['demand'].replace(0, np.nan).dropna(), 95)) if full_gdf['demand'].notna().any() else int(full_gdf['demand'].max() or 1)
        if vmax <= 0:
            vmax = int(full_gdf['demand'].max() or 1)
        color_map = LinearColormap(colors=['yellow', 'red'], vmin=0, vmax=vmax)

        # Draw PLZ polygons with color corresponding to demand
        for idx, row in full_gdf.iterrows():
            val = float(row['demand']) if 'demand' in row and pd.notna(row['demand']) else 0.0
            # Cap display value for color lookup to vmax so legend remains readable
            display_val = min(val, vmax)
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color_map(display_val): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                },
                tooltip=f"PLZ: {row.get('PLZ', '')}, Demand: {val:.1f} (res/station)"
            ).add_to(m)

        # Add color map legend
        color_map.caption = 'Residents per charging station (capped at 95th percentile)'
        color_map.add_to(m)

    # Add color map to the map
    color_map.add_to(m)
    
    folium_static(m, width=800, height=600)
    
    







