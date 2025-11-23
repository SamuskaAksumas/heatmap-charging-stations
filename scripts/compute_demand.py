import os
import sys
import json
import pandas as pd
import geopandas as gpd

# Ensure project root is on sys.path so local packages (core, config) can be imported
basedir = os.path.abspath(os.path.dirname(__file__) + os.sep + '..')
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from core import methods as m1
from config import pdict

basedir = os.path.abspath(os.path.dirname(__file__) + os.sep + '..')
datasets_dir = os.path.join(basedir, 'datasets')
path_geodata_plz = os.path.join(datasets_dir, pdict.get('file_geodat_plz'))
path_lstat = os.path.join(datasets_dir, pdict.get('file_lstations'))
path_residents = os.path.join(datasets_dir, pdict.get('file_residents'))
if not os.path.exists(path_residents):
    alt_xlsx = os.path.join(datasets_dir, 'plz_einwohner.xlsx')
    if os.path.exists(alt_xlsx):
        path_residents = alt_xlsx

out_csv = os.path.join(basedir, 'tmp_plz_demand.csv')
out_json = os.path.join(basedir, 'tmp_plz_demand_summary.json')

# read geodata
try:
    df_geodat_plz = pd.read_csv(path_geodata_plz, sep=';')
    df_geodat_plz['geometry'] = gpd.GeoSeries.from_wkt(df_geodat_plz['geometry'])
except Exception as e:
    print('ERROR reading geodata_plz', e)
    raise

# read lstat with header detection
header_row=0
with open(path_lstat, 'r', encoding='latin1') as fh:
    for i,line in enumerate(fh):
        if 'Ladeeinrichtungs-ID' in line or 'Postleitzahl' in line or (line.count(';')>1 and 'Postleitzahl' in line):
            header_row=i
            break

df_lstat = pd.read_csv(path_lstat, sep=';', header=header_row, encoding='latin1', low_memory=False)

# preprocess lstat and count
gdf_lstat3 = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
df_lstat2 = m1.count_plz_occurrences(gdf_lstat3)

# read residents using T14 if possible

def read_residents(path_residents, df_geodat_plz):
    if path_residents.lower().endswith(('.xlsx','.xls')):
        try:
            raw = pd.read_excel(path_residents, sheet_name='T14', header=None, engine='openpyxl')
            header_row=None
            for i in range(min(10,len(raw))):
                vals = raw.iloc[i].astype(str).str.strip().str.lower().tolist()
                if 'postleitzahl' in vals and any('ins' in v or 'gesamt' in v for v in vals):
                    header_row=i
                    break
            if header_row is None: header_row=2
            df_t14 = pd.read_excel(path_residents, sheet_name='T14', header=header_row, engine='openpyxl')
        except Exception:
            df_t14=None
        if df_t14 is not None:
            cols_low = {c: str(c).strip().lower() for c in df_t14.columns}
            plz_col=None; total_col=None
            for c, lc in cols_low.items():
                if 'postleitzahl' in lc or lc=='plz' or 'postleitzahl' in str(c).lower(): plz_col=c
                if 'insgesamt' in lc or 'ins-' in lc or 'gesamt' in lc or 'in insgesamt' in lc: total_col=c
            if plz_col is not None and total_col is not None:
                df_res = df_t14[[plz_col, total_col]].copy()
                df_res.columns=['plz','einwohner']
                df_res['plz']=df_res['plz'].astype(str).str.extract(r'(\d{5})')[0]
                df_res['plz']=pd.to_numeric(df_res['plz'], errors='coerce')
                df_res['einwohner']=df_res['einwohner'].astype(str).str.replace(r"[^0-9-]","",regex=True)
                df_res['einwohner']=pd.to_numeric(df_res['einwohner'], errors='coerce').fillna(0).astype(int)
                df_residents = df_res.groupby('plz', as_index=False)['einwohner'].sum()
                # attach centroids
                gdf_plz = gpd.GeoDataFrame(df_geodat_plz.copy(), geometry='geometry')
                try:
                    gdf_plz.set_crs(epsg=4326, inplace=True)
                except Exception:
                    gdf_plz.crs='EPSG:4326'
                gdf_plz['centroid']=gdf_plz.geometry.centroid
                merged = df_residents.merge(gdf_plz[['PLZ','centroid']], left_on='plz', right_on='PLZ', how='left')
                merged['lat']=merged['centroid'].apply(lambda g: g.y if g is not None else None)
                merged['lon']=merged['centroid'].apply(lambda g: g.x if g is not None else None)
                return merged[['plz','einwohner','lat','lon']]
    # fallback: try csv
    df_read = pd.read_csv(path_residents, sep=';')
    cmap={c.lower():c for c in df_read.columns}
    if 'postleitzahl' in cmap and 'insgesamt' in cmap:
        tmp = df_read[[cmap['postleitzahl'], cmap['insgesamt']]].copy()
        tmp.columns=['plz','einwohner']
        tmp['plz']=tmp['plz'].astype(str).str.extract(r'(\d{5})')[0]
        tmp['plz']=pd.to_numeric(tmp['plz'], errors='coerce')
        tmp['einwohner']=tmp['einwohner'].astype(str).str.replace(r"[^0-9-]","",regex=True)
        tmp['einwohner']=pd.to_numeric(tmp['einwohner'], errors='coerce').fillna(0).astype(int)
        return tmp
    return None

res = read_residents(path_residents, df_geodat_plz)
if res is None:
    raise RuntimeError('No residents data found')

# Merge counts and residents
counts = df_lstat2.copy()
counts.rename(columns={'PLZ':'plz','Number':'num_stations'}, inplace=True)
merged = res.merge(counts, on='plz', how='left')
merged['num_stations']=merged['num_stations'].fillna(0).astype(int)
merged['einwohner']=merged['einwohner'].fillna(0).astype(int)

# demand metric: residents per station (use num_stations, but avoid div by zero)
merged['res_per_station'] = merged.apply(lambda r: r['einwohner'] / r['num_stations'] if r['num_stations']>0 else float('inf'), axis=1)

# prepare summaries
summary = {}
summary['total_residents'] = int(merged['einwohner'].sum())
summary['total_stations'] = int(counts['num_stations'].sum())

inf_zero = merged[merged['res_per_station']==float('inf')].sort_values(by='einwohner', ascending=False).head(20)
regular = merged[merged['res_per_station']!=float('inf')].sort_values(by='res_per_station', ascending=False).head(20)

summary['top_zero_stations'] = inf_zero[['plz','einwohner','num_stations']].to_dict(orient='records')
summary['top_high_demand'] = regular[['plz','einwohner','num_stations','res_per_station']].to_dict(orient='records')

# save outputs
merged.sort_values(by=['res_per_station','einwohner'], ascending=[False,False]).to_csv(out_csv, index=False)
with open(out_json, 'w', encoding='utf8') as fh:
    json.dump({'paths':{'project_root': basedir, 'datasets': datasets_dir, 'geodata_plz': path_geodata_plz, 'lstat': path_lstat, 'residents': path_residents, 'out_csv': out_csv, 'out_json': out_json}, 'summary': summary}, fh, ensure_ascii=False, indent=2)
print('WROTE', out_csv)
print('WROTE', out_json)
print('TOP_ZERO_SAMPLE', summary['top_zero_stations'][:5])
print('TOP_HIGH_DEMAND_SAMPLE', summary['top_high_demand'][:5])
