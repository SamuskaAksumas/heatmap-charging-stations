import os
import pandas as pd
import geopandas as gpd
from core import methods as m1

basedir = os.path.dirname(os.path.abspath(__file__))
proj = os.path.dirname(basedir)
print('proj', proj)

datasets_dir = os.path.join(proj, 'datasets')
path_geodata_plz = os.path.join(datasets_dir, 'geodata_berlin_plz.csv')
path_residents = os.path.join(datasets_dir, 'plz_einwohner.xlsx')
bez_path = os.path.join(datasets_dir, 'berlin_bezirke', 'bezirksgrenzen.shp')

print('files exist:', os.path.exists(path_geodata_plz), os.path.exists(path_residents), os.path.exists(bez_path))

# Read PLZ geodata
df_geodat_plz = pd.read_csv(path_geodata_plz, sep=';')
print('geodat rows', len(df_geodat_plz))

# Read T5 sheet
raw = pd.read_excel(path_residents, sheet_name='T5', header=2, engine='openpyxl')
print('T5 columns:', raw.columns.tolist())
# find district and total columns
cols_low = {c: str(c).lower() for c in raw.columns}
print('cols lower sample:', list(cols_low.items())[:5])

district_col = None
total_col = None
for c, lc in cols_low.items():
    if 'bezirk' in lc:
        district_col = c
    if 'insgesamt' in lc or 'gesamt' in lc or 'insgesamt' in lc:
        total_col = c
if district_col is None:
    district_col = raw.columns[0]
if total_col is None:
    for c in raw.columns[1:]:
        if pd.to_numeric(raw[c], errors='coerce').notna().any():
            total_col = c
            break
print('district_col, total_col:', district_col, total_col)

df_districts = raw[[district_col, total_col]].copy()
df_districts.columns = ['Bezirk', 'Einwohner_Bezirk']
df_districts = df_districts.dropna(subset=['Bezirk'])
print('districts rows:', len(df_districts))
print(df_districts.head())

# load bezirke
gdf_bez = gpd.read_file(bez_path)
print('bezirke columns:', gdf_bez.columns.tolist())
# choose name col
bez_name_col = None
for c in gdf_bez.columns:
    if 'bez' in str(c).lower() or 'name' in str(c).lower():
        bez_name_col = c
        break
print('bez_name_col', bez_name_col)

# normalize
gdf_bez['bezirk_norm'] = gdf_bez[bez_name_col].astype(str).str.strip().str.lower()
df_districts['bezirk_norm'] = df_districts['Bezirk'].astype(str).str.strip().str.lower()

# prepare plz geodata
import geopandas as gpd
from shapely import wkt

df_geodat_plz['geometry'] = df_geodat_plz['geometry'].apply(lambda x: wkt.loads(x))
gdf_plz = gpd.GeoDataFrame(df_geodat_plz, geometry='geometry')
print('plz gdf crs before', gdf_plz.crs)
# set crs
try:
    gdf_plz.set_crs(epsg=4326, inplace=True)
except Exception:
    gdf_plz.crs = 'EPSG:4326'

# centroids
gdf_plz['centroid'] = gdf_plz.geometry.centroid
gdf_plz_centroids = gdf_plz.set_geometry('centroid')
print('plz count', len(gdf_plz_centroids))

# ensure CRS match
if gdf_plz_centroids.crs != gdf_bez.crs:
    print('CRS differ: plz', gdf_plz_centroids.crs, 'bez', gdf_bez.crs)
    try:
        gdf_plz_centroids = gdf_plz_centroids.to_crs(gdf_bez.crs)
        print('reprojected plz to bez crs')
    except Exception as e:
        print('reproj failed', e)

# spatial join
joined = gpd.sjoin(gdf_plz_centroids, gdf_bez.set_geometry('geometry'), how='left', predicate='within')
print('joined rows', len(joined))

joined['bezirk_norm'] = joined[bez_name_col].astype(str).str.strip().str.lower()
plz_counts = joined.groupby('bezirk_norm').size().rename('n_plz').reset_index()
print('plz_counts sample')
print(plz_counts.head())

merged = df_districts.merge(plz_counts, on='bezirk_norm', how='left')
print('merged sample')
print(merged.head(20))

# convert Einwohner_Bezirk
merged['Einwohner_Bezirk_clean'] = merged['Einwohner_Bezirk'].astype(str).str.replace(r"[^0-9-]", "", regex=True)
merged['Einwohner_Bezirk_num'] = pd.to_numeric(merged['Einwohner_Bezirk_clean'], errors='coerce').fillna(0).astype(int)
print('sum district totals (cleaned):', merged['Einwohner_Bezirk_num'].sum())
print('merged n_plz nulls:', merged['n_plz'].isna().sum())

merged2 = merged.dropna(subset=['n_plz']).copy()
merged2['einwohner_per_plz'] = (merged2['Einwohner_Bezirk_num'] / merged2['n_plz']).round().astype(int)
print('einwohner_per_plz stats:', merged2['einwohner_per_plz'].describe())

# Map back to PLZ
joined2 = joined.merge(merged2[['bezirk_norm', 'einwohner_per_plz']], on='bezirk_norm', how='left')
print('joined2 sample cols', joined2.columns.tolist())
print(joined2[['PLZ','bezirk_norm','einwohner_per_plz']].head(30))

# Build df_residents
df_residents_plz = pd.DataFrame({
    'plz': joined2['PLZ'].astype(int),
    'einwohner': joined2['einwohner_per_plz'].fillna(0).astype(int),
    'lat': joined2['centroid'].y,
    'lon': joined2['centroid'].x
})
print('plz-level residents sample')
print(df_residents_plz.head(30))
print('plz-level einwohner stats', df_residents_plz['einwohner'].describe())

# Now run preprop_resid
try:
    gdf_res = m1.preprop_resid(df_residents_plz, df_geodat_plz, {'geocode': 'PLZ'})
    print('gdf_res head')
    print(gdf_res[['PLZ','Einwohner']].head(20))
    print('gdf_res Einwohner stats', gdf_res['Einwohner'].describe())
except Exception as e:
    print('preprop_resid failed', e)

print('done')
