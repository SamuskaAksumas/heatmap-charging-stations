import os
import io
import pandas                        as pd
import geopandas                     as gpd
from shapely.geometry                import Point
from core import methods             as m1
from core import HelperTools         as ht

from config                          import pdict


# Ensure working directory is project root (where this file lives)
basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(basedir)


def _read_csv_with_header_detection(path, sep=';'):
    """Read a CSV that may contain metadata lines before the header.
    Find a header row by scanning for a line that contains expected column names
    (like 'Ladeeinrichtungs-ID' or 'Postleitzahl') and use that as header.
    """
    with open(path, 'r', encoding='latin1') as fh:
        header_row = 0
        for i, line in enumerate(fh):
            if 'Ladeeinrichtungs-ID' in line or 'Postleitzahl' in line or (line.count(sep) > 1 and 'Postleitzahl' in line):
                header_row = i
                break

    df = pd.read_csv(path, sep=sep, header=header_row, encoding='latin1')
    return df


@ht.timer
def main():
    """Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin"""

    # Paths
    datasets_dir = os.path.join(basedir, 'datasets')
    path_geodata_plz = os.path.join(datasets_dir, pdict.get('file_geodat_plz', 'geodata_berlin_plz.csv'))
    path_lstat = os.path.join(datasets_dir, pdict.get('file_lstations', 'Ladesaeulenregister.csv'))

    # config may point to a CSV but repo contains an Excel file — try config path first then fallback
    residents_file_cfg = pdict.get('file_residents', 'plz_einwohner.csv')
    path_residents = os.path.join(datasets_dir, residents_file_cfg)
    if not os.path.exists(path_residents):
        alt = os.path.join(datasets_dir, 'plz_einwohner.xlsx')
        if os.path.exists(alt):
            path_residents = alt

    # 1) Load geodata (PLZ polygons)
    df_geodat_plz = pd.read_csv(path_geodata_plz, sep=';')

    # 2) Load charging stations CSV (robust header detection because file contains metadata lines)
    df_lstat = _read_csv_with_header_detection(path_lstat, sep=';')

    # 3) Preprocess charging stations and count per PLZ
    gdf_lstat3 = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    df_lstat2 = m1.count_plz_occurrences(gdf_lstat3)

    # 4) Load residents data (Excel or CSV).
    df_residents = None
    if path_residents.lower().endswith(('.xlsx', '.xls')):
        # Try to find PLZ-level table in sheet 'T14' first using header detection
        try:
            raw = pd.read_excel(path_residents, sheet_name='T14', header=None, engine='openpyxl')
            header_row = None
            for i in range(min(10, len(raw))):
                vals = raw.iloc[i].astype(str).str.strip().str.lower().tolist()
                if 'postleitzahl' in vals and any('ins' in v or 'gesamt' in v for v in vals):
                    header_row = i
                    break
            if header_row is None:
                header_row = 2
            df_t14 = pd.read_excel(path_residents, sheet_name='T14', header=header_row, engine='openpyxl')
        except Exception:
            df_t14 = None

        if df_t14 is not None:
            # detect the PLZ and total columns
            cols_low = {c: str(c).strip().lower() for c in df_t14.columns}
            plz_col = None
            total_col = None
            for c, lc in cols_low.items():
                if 'postleitzahl' in lc or lc == 'plz' or 'postleitzahl' in str(c).lower():
                    plz_col = c
                if 'insgesamt' in lc or lc == 'ins-' or 'gesamt' in lc or 'in insgesamt' in lc:
                    total_col = c

            if plz_col is not None and total_col is not None:
                df_res = df_t14[[plz_col, total_col]].copy()
                df_res.columns = ['plz', 'einwohner']
                df_res['plz'] = df_res['plz'].astype(str).str.extract(r'(\d{5})')[0]
                df_res['plz'] = pd.to_numeric(df_res['plz'], errors='coerce')
                # einwohner is numeric from Excel; convert directly without regex (regex removes decimal points)
                df_res['einwohner'] = pd.to_numeric(df_res['einwohner'], errors='coerce').fillna(0).astype(int)
                # Note: T14 lists each PLZ once per district. Each row is a unique (PLZ, district) entry.
                # Do NOT aggregate—sum of all rows = expected total.
                df_residents = df_res.dropna(subset=['plz'])

                # attach PLZ centroid lat/lon
                df_geodat_plz_loc = df_geodat_plz.copy()
                df_geodat_plz_loc['geometry'] = gpd.GeoSeries.from_wkt(df_geodat_plz_loc['geometry'])
                gdf_plz = gpd.GeoDataFrame(df_geodat_plz_loc, geometry='geometry')
                try:
                    gdf_plz.set_crs(epsg=4326, inplace=True)
                except Exception:
                    gdf_plz.crs = 'EPSG:4326'
                gdf_plz['centroid'] = gdf_plz.geometry.centroid
                merged_plz = df_residents.merge(gdf_plz[['PLZ', 'centroid']], left_on='plz', right_on='PLZ', how='left')
                merged_plz['lat'] = merged_plz['centroid'].apply(lambda g: g.y if g is not None else None)
                merged_plz['lon'] = merged_plz['centroid'].apply(lambda g: g.x if g is not None else None)
                df_residents = merged_plz[['plz', 'einwohner', 'lat', 'lon']].copy()

    # If T14 failed or is not present, fall back to older logic (CSV or T5 Bezirke totals)
    if df_residents is None:
        if path_residents.lower().endswith(('.xlsx', '.xls')):
            df_read = pd.read_excel(path_residents, engine='openpyxl')
        else:
            df_read = pd.read_csv(path_residents, sep=';')

        # normalize column names to lower-case keys
        col_map = {c: c.strip().lower() for c in df_read.columns}
        df_read.rename(columns=col_map, inplace=True)

        # detect if this is a Bezirke summary (T5)
        cols = list(df_read.columns)
        if any('bezirk' in str(c).lower() for c in cols) or all(str(c).lower().startswith('unnamed') or str(c).strip()=='' for c in cols):
            try:
                df_t5 = pd.read_excel(path_residents, sheet_name='T5', header=2, engine='openpyxl')
            except Exception:
                df_t5 = pd.read_excel(path_residents, sheet_name='T5', header=None, engine='openpyxl')

            # find district and total columns
            tcols = {c: str(c).lower() for c in df_t5.columns}
            district_col = None
            total_col = None
            for c, lc in tcols.items():
                if 'bezirk' in lc or 'bezirk' in str(c).lower():
                    district_col = c
                if 'insgesamt' in lc or 'in insgesamt' in lc or 'gesamt' in lc or 'in insgesamt' in str(c).lower():
                    total_col = c

            if district_col is None:
                district_col = df_t5.columns[0]
            if total_col is None:
                for c in df_t5.columns[1:]:
                    if pd.to_numeric(df_t5[c], errors='coerce').notna().any():
                        total_col = c
                        break

            if total_col is not None:
                df_districts = df_t5[[district_col, total_col]].copy()
                df_districts.columns = ['Bezirk', 'Einwohner_Bezirk']
                df_districts = df_districts.dropna(subset=['Bezirk'])

                # Read Bezirke shapefile and map Bezirke -> PLZ via PLZ centroids
                bez_path = os.path.join(datasets_dir, 'berlin_bezirke', 'bezirksgrenzen.shp')
                if os.path.exists(bez_path):
                    gdf_bez = gpd.read_file(bez_path)
                    if 'Gemeinde_n' in gdf_bez.columns:
                        bez_name_col = 'Gemeinde_n'
                    elif 'Gemeinde_s' in gdf_bez.columns:
                        bez_name_col = 'Gemeinde_s'
                    else:
                        bez_name_col = None
                        for c in gdf_bez.columns:
                            if 'gemeinde' in str(c).lower() or 'bezirk' in str(c).lower() or 'name' in str(c).lower():
                                bez_name_col = c
                                break

                    gdf_bez['bezirk_norm'] = gdf_bez[bez_name_col].astype(str).str.strip().str.lower()
                    df_districts['bezirk_norm'] = df_districts['Bezirk'].astype(str).str.strip().str.lower()

                    valid_bez = set(gdf_bez['bezirk_norm'].tolist())
                    df_districts = df_districts[df_districts['bezirk_norm'].isin(valid_bez)].copy()

                    df_geodat_plz_loc = df_geodat_plz.copy()
                    df_geodat_plz_loc['geometry'] = gpd.GeoSeries.from_wkt(df_geodat_plz_loc['geometry'])
                    gdf_plz = gpd.GeoDataFrame(df_geodat_plz_loc, geometry='geometry')
                    try:
                        gdf_plz.set_crs(epsg=4326, inplace=True)
                    except Exception:
                        gdf_plz.crs = 'EPSG:4326'
                    gdf_plz['centroid'] = gdf_plz.geometry.centroid
                    gdf_plz_centroids = gdf_plz.set_geometry('centroid')
                    if gdf_plz_centroids.crs != gdf_bez.crs:
                        gdf_plz_centroids = gdf_plz_centroids.to_crs(gdf_bez.crs)

                    joined = gpd.sjoin(gdf_plz_centroids, gdf_bez.set_geometry('geometry'), how='left', predicate='within')
                    joined['bezirk_norm'] = joined[bez_name_col].astype(str).str.strip().str.lower()

                    plz_counts = joined.groupby('bezirk_norm').size().rename('n_plz').reset_index()
                    merged = df_districts.merge(plz_counts, on='bezirk_norm', how='left')
                    merged['Einwohner_Bezirk'] = merged['Einwohner_Bezirk'].astype(str).str.replace(r"[^0-9-]", "", regex=True)
                    merged['Einwohner_Bezirk'] = pd.to_numeric(merged['Einwohner_Bezirk'], errors='coerce').fillna(0).astype(int)
                    merged = merged.dropna(subset=['n_plz'])
                    merged['einwohner_per_plz'] = (merged['Einwohner_Bezirk'] / merged['n_plz']).round().astype(int)
                    joined2 = joined.merge(merged[['bezirk_norm', 'einwohner_per_plz']], on='bezirk_norm', how='left')
                    df_residents = pd.DataFrame({
                        'plz': joined2['PLZ'].astype(int),
                        'einwohner': joined2['einwohner_per_plz'].fillna(0).astype(int),
                        'lat': joined2['centroid'].y,
                        'lon': joined2['centroid'].x
                    })
        else:
            # Not T5 format; try to map common column names if present
            df_read_cols = {c.lower(): c for c in df_read.columns}
            # simple mapping
            if 'postleitzahl' in df_read_cols and 'insgesamt' in df_read_cols:
                df_tmp = df_read[[df_read_cols['postleitzahl'], df_read_cols['insgesamt']]].copy()
                df_tmp.columns = ['plz', 'einwohner']
                df_tmp['plz'] = df_tmp['plz'].astype(str).str.extract(r'(\d{5})')[0]
                df_tmp['plz'] = pd.to_numeric(df_tmp['plz'], errors='coerce')
                df_tmp['einwohner'] = df_tmp['einwohner'].astype(str).str.replace(r"[^0-9-]", "", regex=True)
                df_tmp['einwohner'] = pd.to_numeric(df_tmp['einwohner'], errors='coerce').fillna(0).astype(int)
                df_residents = df_tmp

    # If still no df_residents, raise a clear error later when validating columns

    # Try to map common variants to 'plz','einwohner','lat','lon'
    mapper = {}
    if 'plz' in df_residents.columns:
        mapper['plz'] = 'plz'
    else:
        for c in df_residents.columns:
            if 'plz' in c:
                mapper[c] = 'plz'
                break

    if 'einwohner' in df_residents.columns:
        mapper['einwohner'] = 'einwohner'
    else:
        for c in df_residents.columns:
            if 'einw' in c:
                mapper[c] = 'einwohner'
                break

    # lat / lon variants
    lat_col = None
    lon_col = None
    for c in df_residents.columns:
        if c in ('lat', 'breitengrad', 'latitude'):
            lat_col = c
        if c in ('lon', 'lng', 'longitude', 'längengrad'):
            lon_col = c
    if lat_col:
        mapper[lat_col] = 'lat'
    if lon_col:
        mapper[lon_col] = 'lon'

    # apply mapping (only keys that exist)
    final_mapper = {k: v for k, v in mapper.items() if k in df_residents.columns}
    if final_mapper:
        df_residents.rename(columns=final_mapper, inplace=True)

    # Ensure required columns exist; if not, raise informative error
    required = {'plz', 'einwohner', 'lat', 'lon'}
    if not required.issubset(set(df_residents.columns)):
        missing = required - set(df_residents.columns)
        raise RuntimeError(f"Residents file is missing required columns: {missing}. Columns found: {list(df_residents.columns)}")

    # 5) Preprocess residents and attach geometries
    gdf_residents2 = m1.preprop_resid(df_residents, df_geodat_plz, pdict)

    # 6) Call Streamlit page builder
    m1.make_streamlit_electric_Charging_resid(df_lstat2, gdf_residents2)


if __name__ == "__main__":
    main()

# currentWorkingDirectory = "C:\\(...)\\project1"
# #currentWorkingDirectory = "/mount/src/berlingeoheatmap1/"

# # -----------------------------------------------------------------------------
# import os
# os.chdir(currentWorkingDirectory)
# print("Current working directory\n" + os.getcwd())

# import pandas                        as pd
# from core import methods             as m1
# from core import HelperTools         as ht

# from config                          import pdict

# # -----------------------------------------------------------------------------
# @ht.timer
# def main():
#     """Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin"""

#     df_geodat_plz   = #
    
#     df_lstat        = #
#     df_lstat2       = #
#     gdf_lstat3      = #
    
#     df_residents    = #
#     gdf_residents2  = #
    
# # -----------------------------------------------------------------------------------------------------------------------

#     #


# if __name__ == "__main__": 
#     main()

