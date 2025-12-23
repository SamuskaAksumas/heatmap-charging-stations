"""
Main application entry point using Domain-Driven Design architecture.
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config_ddd import Config
from infrastructure.repositories.implementations import (
    CsvChargingStationRepository,
    ShapefilePostalAreaRepository,
    ExcelDemographicRepository,
    JsonSuggestionRepository
)
from domain.charging_infrastructure.services import ChargingStationService
from domain.geography.services import GeographyService
from domain.demographics.services import DemographicsService
from domain.community_engagement.services import CommunityEngagementService
from domain.analytics.services import AnalyticsService
from application.services.implementations import MapService, SuggestionService, AnalyticsServiceApp
from presentation.ui import ChargingMapUI


def create_application():
    """Create and wire the application components."""

    # Validate configuration
    Config.validate_paths()

    # Infrastructure layer - repositories
    charging_repo = CsvChargingStationRepository(str(Config.CHARGING_STATIONS_CSV))
    postal_repo = ShapefilePostalAreaRepository(str(Config.POSTAL_AREAS_SHAPEFILE))
    demographic_repo = ExcelDemographicRepository(str(Config.DEMOGRAPHICS_EXCEL))
    suggestion_repo = JsonSuggestionRepository(str(Config.SUGGESTIONS_JSON))

    # Domain layer - services
    charging_service = ChargingStationService(charging_repo)
    geography_service = GeographyService(postal_repo)
    demographics_service = DemographicsService(demographic_repo)
    community_service = CommunityEngagementService(suggestion_repo)
    analytics_service = AnalyticsService(
        charging_repo, demographic_repo
    )

    # Application layer - services
    map_service = MapService(charging_service, geography_service, analytics_service, demographics_service)
    suggestion_app_service = SuggestionService(suggestion_repo, geography_service)
    analytics_app_service = AnalyticsServiceApp(analytics_service)

    # Presentation layer - UI
    ui = ChargingMapUI(map_service, suggestion_app_service, analytics_app_service, geography_service)

    return ui


def main():
    """Main application entry point."""
    try:
        # Create the application
        app = create_application()

        # Run the Streamlit app
        import streamlit as st

        # Configure page
        st.set_page_config(
            page_title="Berlin Charging Map",
            page_icon="🔌",
            layout="wide"
        )

        # Render the main page
        app.render_main_page()

    except Exception as e:
        print(f"Application error: {str(e)}")
        print("Please check the data files and configuration.")
        try:
            import streamlit as st
            st.error(f"Application error: {str(e)}")
            st.error("Please check the data files and configuration.")
        except:
            pass


if __name__ == "__main__":
    main()