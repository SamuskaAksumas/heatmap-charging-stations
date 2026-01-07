"""
Main Streamlit application for the Electric Charging Stations Heatmap.

This is the UI Presentation Layer that displays the interactive map
based on pre-calculated demand and station data.
"""
import folium
import streamlit as st
from streamlit_folium import folium_static

from src.shared.infrastructure.utils import timer
from src.suggestion.application.services.suggestion_service import SuggestionService
from src.suggestion.infrastructure.repositories.suggestion_repository import SuggestionRepository
from .components.map_view import render_map_layer
from .components.suggestion_form import render_suggestion_form
from .components.suggestion_list import render_suggestion_list


@timer
def make_streamlit_electric_charging_resid(dfr1, dfr2, demand_service):
    """
    UI Presentation Layer:
    Displays the interactive map based on pre-calculated demand and station data.

    Args:
        dfr1: DataFrame with station counts per PLZ.
        dfr2: DataFrame with resident and demand data per PLZ.
        demand_service: Service for retrieving demand calculation results.
    """
    suggestion_repo = SuggestionRepository()
    suggestion_service = SuggestionService(suggestion_repo)

    # Standardize column names for the UI to match our Entities
    dframe_stations = dfr1.copy()
    dframe_analysis = dfr2.copy()

    st.title('Heatmaps: Electric Charging Stations and Residents')

    # Add tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Map View", "Suggest Location", "View Suggestions"])

    with tab1:
        layer_selection = st.radio("Select Layer", ("Residents", "Charging_Stations", "Demand"))

        # Create a Folium map centered on Berlin
        m = folium.Map(location=[52.52, 13.40], zoom_start=10)

        # Render the selected layer
        render_map_layer(m, layer_selection, dframe_stations, dframe_analysis, demand_service)

        folium.LayerControl().add_to(m)
        folium_static(m)

    with tab2:
        render_suggestion_form(suggestion_service)

    with tab3:
        render_suggestion_list(suggestion_service)
