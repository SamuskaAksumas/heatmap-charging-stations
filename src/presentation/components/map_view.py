"""Map view component - Renders geographic data layers on Folium map."""
import folium
from branca.colormap import LinearColormap


def render_map_layer(m, layer_selection, dframe_stations, dframe_analysis, demand_service):
    """Render selected layer (Residents/Charging_Stations/Demand)."""
    from src.demand.domain.events.display_demand import display_demand
    import streamlit as st

    if layer_selection == "Residents":
        _render_residents_layer(m, dframe_analysis)
    elif layer_selection == "Charging_Stations":
        _render_stations_layer(m, dframe_stations)
    elif layer_selection == "Demand":
        _render_demand_layer(m, demand_service, st)


def _render_residents_layer(m, dframe_analysis):
    """Render the residents heatmap layer."""
    color_map = LinearColormap(
        colors=['yellow', 'red'],
        vmin=dframe_analysis['Einwohner'].min(),
        vmax=dframe_analysis['Einwohner'].max()
    )

    for idx, row in dframe_analysis.iterrows():
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=color_map(row['Einwohner']): {
                'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7
            },
            tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}"
        ).add_to(m)


def _render_stations_layer(m, dframe_stations):
    """Render the charging stations heatmap layer."""
    vmin = int(dframe_stations['Number'].min()) if 'Number' in dframe_stations.columns else 0
    vmax = int(dframe_stations['Number'].max()) if 'Number' in dframe_stations.columns else 1

    color_map = LinearColormap(colors=['yellow', 'red'], vmin=vmin, vmax=vmax)

    for idx, row in dframe_stations.iterrows():
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=color_map(row['Number']): {
                'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7
            },
            tooltip=f"PLZ: {row['PLZ']}, Stations: {row['Number']}"
        ).add_to(m)


def _render_demand_layer(m, demand_service, st):
    """Render the demand heatmap layer."""
    from src.demand.domain.events.display_demand import display_demand

    analysis_data = demand_service.get_latest_results()
    if analysis_data is not None:
        display_demand(m, analysis_data)
    else:
        st.warning("Please run the calculation first or check data sources.")
