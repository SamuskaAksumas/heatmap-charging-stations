import os
import pandas as pd
from core import methods as m1
from core import HelperTools as ht
from config import pdict

# Import from divided layers
from src.infrastructure.readers import read_csv_with_header_detection, load_geodata
from src.domain.events.stations_processed import on_stations_processed
from src.domain.events.residents_processed import process_residents_data
from src.domain.events.demand_calculated import on_demand_calculated

basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(basedir)

@ht.timer
def main():
    # Define directories
    datasets_dir = os.path.join(basedir, 'datasets')
    
    # --- PATH CONSTRUCTION (Where path_residents comes from) ---
    path_geodata_plz = os.path.join(datasets_dir, pdict.get('file_geodat_plz', 'geodata_berlin_plz.csv'))
    path_lstat = os.path.join(datasets_dir, pdict.get('file_lstations', 'Ladesaeulenregister.csv'))
    
    # Get residents filename from config
    residents_file_cfg = pdict.get('file_residents', 'plz_einwohner.csv')
    path_residents = os.path.join(datasets_dir, residents_file_cfg)

    # Fallback logic: if the CSV doesn't exist, check for the Excel version
    if not os.path.exists(path_residents):
        alt_path = os.path.join(datasets_dir, 'plz_einwohner.xlsx')
        if os.path.exists(alt_path):
            path_residents = alt_path
    # -----------------------------------------------------------

    # 1. Load Data (Infrastructure)
    df_geodat_plz = load_geodata(path_geodata_plz)
    df_lstat_raw = read_csv_with_header_detection(path_lstat)

    # 2. Process Residents (Event 1)
    # This now uses the path_residents we constructed above
    df_residents = process_residents_data(path_residents, df_geodat_plz, datasets_dir)

    # 3. Process Stations (Event 2)
    df_stations_count = on_stations_processed(df_lstat_raw, df_geodat_plz, pdict)

    # 4. Calculate Demand (Event 3)
    if df_residents is not None:
        # Pre-process residents to get geometry (original m1 logic)
        gdf_residents_geo = m1.preprop_resid(df_residents, df_geodat_plz, pdict)
        
        # Calculate demand score via the Demand Event
        df_final_analysis = on_demand_calculated(df_stations_count, gdf_residents_geo)

        # 5. UI Presentation
        m1.make_streamlit_electric_Charging_resid(df_stations_count, df_final_analysis)
    else:
        print("Error: Residents data could not be processed. Check file path or format.")

if __name__ == "__main__":
    main()