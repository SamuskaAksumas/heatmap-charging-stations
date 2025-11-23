import os
import pandas as pd
import geopandas as gpd

root = os.path.dirname(os.path.dirname(__file__))
datasets_dir = os.path.join(root, 'datasets')

geodat_path = os.path.join(datasets_dir, 'geodata_berlin_plz.csv')
residents_xlsx = os.path.join(datasets_dir, 'plz_einwohner.xlsx')

print('Reading PLZ geodata...')
df_geodat = pd.read_csv(geodat_path, sep=';')
df_geodat['geometry'] = gpd.GeoSeries.from_wkt(df_geodat['geometry'])

gdf_plz = gpd.GeoDataFrame(df_geodat, geometry='geometry')
try:
    gdf_plz.set_crs(epsg=4326, inplace=True)
except Exception:
    gdf_plz.crs = 'EPSG:4326'

gdf_plz['centroid'] = gdf_plz.geometry.centroid

print('Trying to read sheet T14 from residents xlsx with header detection...')
df_t14 = None
try:
    # read without header and search for a header row that contains 'Postleitzahl'
    df_raw = pd.read_excel(residents_xlsx, sheet_name='T14', header=None, engine='openpyxl')
    print('First 10 rows (raw) of T14 for inspection:')
    print(df_raw.head(10))
    header_row = None
    for i in range(min(10, len(df_raw))):
        row_vals = df_raw.iloc[i].astype(str).str.strip().str.lower().tolist()
        # prefer rows that contain both 'postleitzahl' and 'bezirk' as the header
        if any(v == 'postleitzahl' for v in row_vals) and any('bezirk' in v for v in row_vals):
            header_row = i
            break
        # fallback: exact 'postleitzahl' match alone
        if any(v == 'postleitzahl' for v in row_vals):
            header_row = i
            break
    if header_row is None:
        # fallback to header=2 as previously used
        header_row = 2
    df_t14 = pd.read_excel(residents_xlsx, sheet_name='T14', header=header_row, engine='openpyxl')
    print(f'Read T14 with detected header={header_row}')
except Exception as e:
    print('Failed to read T14:', e)

if df_t14 is None:
    print('No T14 sheet found; aborting diagnostics.')
    raise SystemExit(1)

cols_low = {c: str(c).strip().lower() for c in df_t14.columns}
plz_col = None
total_col = None
for c, lc in cols_low.items():
    if 'postleitzahl' in lc or lc == 'plz' or 'postleitzahl' in str(c).lower():
        plz_col = c
    if 'insgesamt' in lc or lc == 'insgesamt' or 'gesamt' in lc or 'in insgesamt' in lc:
        total_col = c

print('Detected columns:', plz_col, total_col)
if plz_col is None or total_col is None:
    print('Could not find required columns in T14. Columns are:', list(df_t14.columns))
    raise SystemExit(1)

df_res = df_t14[[plz_col, total_col]].copy()
df_res.columns = ['plz', 'einwohner']
df_res['plz'] = df_res['plz'].astype(str).str.extract(r'(\d{5})')[0]
df_res['plz'] = pd.to_numeric(df_res['plz'], errors='coerce')

df_res['einwohner'] = df_res['einwohner'].astype(str).str.replace(r"[^0-9-]", "", regex=True)
df_res['einwohner'] = pd.to_numeric(df_res['einwohner'], errors='coerce').fillna(0).astype(int)

# Aggregate rows per PLZ (T14 may list a PLZ multiple times across districts)
df_res = df_res.groupby('plz', as_index=False)['einwohner'].sum()

# merge with centroids
merged = df_res.merge(gdf_plz[['PLZ', 'centroid']], left_on='plz', right_on='PLZ', how='left')
merged['lat'] = merged['centroid'].apply(lambda g: g.y if g is not None else None)
merged['lon'] = merged['centroid'].apply(lambda g: g.x if g is not None else None)

print('\nPLZ-level residents stats from T14:')
print('T14 DataFrame head (after header detection):')
print(df_t14.head(10))
print('Detected df_t14.columns:', list(df_t14.columns))

print('\ncount (plz rows):', len(merged))
print('valid plz with geometry:', merged['centroid'].notna().sum())
merged_valid = merged[merged['centroid'].notna()].copy()
print('sum einwohner (matched PLZs):', merged_valid['einwohner'].sum())
print('min einwohner (matched PLZs):', merged_valid['einwohner'].min())
print('max einwohner (matched PLZs):', merged_valid['einwohner'].max())
print('mean einwohner (matched PLZs):', merged_valid['einwohner'].mean())

# print a sample of top/bottom
print('\nSample top 10 by einwohner:')
print(merged.sort_values('einwohner', ascending=False).head(10)[['plz', 'einwohner']])
print('\nSample bottom 10 by einwohner:')
print(merged.sort_values('einwohner', ascending=True).head(10)[['plz', 'einwohner']])
