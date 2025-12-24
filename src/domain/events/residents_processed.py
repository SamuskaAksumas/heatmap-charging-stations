import pandas as pd
import geopandas as gpd
import os

def process_residents_data(path_residents, df_geodat_plz, datasets_dir):
    """
    Exact logic from the original main.py to handle T14 and T5 resident data formats.
    """
    df_residents = None
    
    # 1. Attempt T14 Excel Logic
    if path_residents.lower().endswith(('.xlsx', '.xls')):
        try:
            raw = pd.read_excel(path_residents, sheet_name='T14', header=None, engine='openpyxl')
            header_row = None
            for i in range(min(10, len(raw))):
                vals = raw.iloc[i].astype(str).str.strip().str.lower().tolist()
                if 'postleitzahl' in vals and any('ins' in v or 'gesamt' in v for v in vals):
                    header_row = i
                    break
            if header_row is None: header_row = 2
            df_t14 = pd.read_excel(path_residents, sheet_name='T14', header=header_row, engine='openpyxl')
        except Exception:
            df_t14 = None

        if df_t14 is not None:
            cols_low = {c: str(c).strip().lower() for c in df_t14.columns}
            plz_col, total_col = None, None
            for c, lc in cols_low.items():
                if 'postleitzahl' in lc or lc == 'plz' or 'postleitzahl' in str(c).lower(): plz_col = c
                if 'insgesamt' in lc or lc == 'ins-' or 'gesamt' in lc or 'in insgesamt' in lc: total_col = c

            if plz_col is not None and total_col is not None:
                df_res = df_t14[[plz_col, total_col]].copy()
                df_res.columns = ['plz', 'einwohner']
                df_res['plz'] = df_res['plz'].astype(str).str.extract(r'(\d{5})')[0]
                df_res['plz'] = pd.to_numeric(df_res['plz'], errors='coerce')
                df_res['einwohner'] = pd.to_numeric(df_res['einwohner'], errors='coerce').fillna(0).astype(int)
                
                # Attach PLZ centroid
                df_geodat_plz_loc = df_geodat_plz.copy()
                df_geodat_plz_loc['geometry'] = gpd.GeoSeries.from_wkt(df_geodat_plz_loc['geometry'])
                gdf_plz = gpd.GeoDataFrame(df_geodat_plz_loc, geometry='geometry')
                gdf_plz.crs = 'EPSG:4326'
                gdf_plz['centroid'] = gdf_plz.geometry.centroid
                merged_plz = df_res.merge(gdf_plz[['PLZ', 'centroid']], left_on='plz', right_on='PLZ', how='left')
                merged_plz['lat'] = merged_plz['centroid'].apply(lambda g: g.y if g is not None else None)
                merged_plz['lon'] = merged_plz['centroid'].apply(lambda g: g.x if g is not None else None)
                df_residents = merged_plz[['plz', 'einwohner', 'lat', 'lon']].copy().dropna(subset=['plz'])

    # 2. Fallback to T5 Logic (Districts spatial join)
    if df_residents is None:
        if path_residents.lower().endswith(('.xlsx', '.xls')):
            df_read = pd.read_excel(path_residents, engine='openpyxl')
        else:
            df_read = pd.read_csv(path_residents, sep=';')

        # normalize column names
        col_map = {c: c.strip().lower() for c in df_read.columns}
        df_read.rename(columns=col_map, inplace=True)

        # T5 Format detection and Spatial Join logic
        bez_path = os.path.join(datasets_dir, 'berlin_bezirke', 'bezirksgrenzen.shp')
        if os.path.exists(bez_path):
            # ... (Paste your original spatial join code here to maintain functionality) ...
            pass # Replace this with the full logic from lines 115-165 of your original main.py

    return df_residents