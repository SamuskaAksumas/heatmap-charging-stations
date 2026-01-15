"""
Main application entry point (Composition Root).

Orchestrates data loading, processing, and visualization for the
Berlin Electric Charging Stations Heatmap application.
"""
import os

from config import pdict

# Infrastructure Layer
from src.demand.infrastructure.repositories.demand_repository import DemandRepository
from src.shared.infrastructure.repositories.shared_repository import SharedRepository

# Application Layer
from src.demand.application.services.demand_service import DemandService
from src.shared.application.services.shared_service import SharedService

# Preprocessing (Infrastructure)
from src.shared.infrastructure.preprocessing import preprop_resid

# Presentation Layer
from src.presentation.streamlit_app import make_streamlit_electric_charging_resid

# Utilities
from src.shared.infrastructure.utils import timer

basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(basedir)


@timer
def main():
    """Main application entry point."""
    demand_repo = DemandRepository()
    demand_service = DemandService(demand_repo)
    shared_repo = SharedRepository()
    shared_service = SharedService(shared_repo)

    # Define directories
    datasets_dir = os.path.join(basedir, 'src', 'shared', 'infrastructure', 'datasets')

    # Path construction
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

    # 1. Load Data (Infrastructure)
    df_geodat_plz = shared_repo.load_geodata(path_geodata_plz)
    df_lstat_raw = shared_repo.read_csv_with_header_detection(path_lstat)

    # 2. Process Residents (Event 1)
    df_residents = shared_service.get_processed_residents(path_residents, df_geodat_plz, datasets_dir)

    # 3. Process Stations (Event 2)
    df_stations_count = shared_service.get_processed_stations(path_lstat, df_geodat_plz, pdict)

    # 4. Calculate Demand (Event 3)
    if df_residents is not None:
        # Pre-process residents to get geometry
        gdf_residents_geo = preprop_resid(df_residents, df_geodat_plz, pdict)

        # Calculate demand score via the Demand Event
        df_final_analysis = demand_service.calculate_demand(df_stations_count, gdf_residents_geo)

        # 5. UI Presentation
        make_streamlit_electric_charging_resid(df_stations_count, df_final_analysis, demand_service)
    else:
        print("Error: Residents data could not be processed. Check file path or format.")


if __name__ == "__main__":
    main()
