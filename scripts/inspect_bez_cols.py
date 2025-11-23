import os
import geopandas as gpd
basedir = os.path.dirname(os.path.abspath(__file__))
proj = os.path.dirname(basedir)
datasets_dir = os.path.join(proj, 'datasets')
bez_path = os.path.join(datasets_dir, 'berlin_bezirke', 'bezirksgrenzen.shp')
print('bez_path', bez_path)
gdf_bez = gpd.read_file(bez_path)
print('columns:', gdf_bez.columns.tolist())
for c in gdf_bez.columns:
    print('col', c, 'sample:', gdf_bez[c].iloc[:10].tolist())
