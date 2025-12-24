import numpy as np
import pandas as pd

def on_demand_calculated(df_stations_count, df_residents_geo):
    # 1. Prepare Residents
    full_gdf = df_residents_geo.copy()
    
    # 2. Prepare Stations (Handle 'Number' vs 'count' rename)
    stations = df_stations_count.copy()
    
    # If the input uses 'count' (like in your test), rename it to 'Number'
    # so the rest of your calculation logic works perfectly.
    if 'count' in stations.columns and 'Number' not in stations.columns:
        stations = stations.rename(columns={'count': 'Number'})
    
    # Safety select
    stations = stations[['PLZ', 'Number']]
    
    # 3. Merge
    full_gdf = full_gdf.merge(stations, on='PLZ', how='left')
    full_gdf['Number'] = full_gdf['Number'].fillna(0).astype(int)
    
    # 4. Demand Calculation Logic
    def compute_demand(row):
        # Using the same logic as your provided code
        if row['Number'] > 0:
            return row['Einwohner'] / row['Number']
        else:
            return float(row['Einwohner']) 

    full_gdf['demand'] = full_gdf.apply(compute_demand, axis=1)
    full_gdf['demand'] = full_gdf['demand'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Return with 'count' so your test expectations match
    return full_gdf.rename(columns={'Number': 'count'})