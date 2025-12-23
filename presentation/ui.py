"""
Presentation layer for the charging station visualization application.
"""
import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
from typing import Dict, List

from application.services.implementations import MapService, SuggestionService, AnalyticsServiceApp
from domain.charging_infrastructure.entities import ChargingStation
from domain.community_engagement.entities import ChargingSuggestion
from domain.geography.services import GeographyService


class ChargingMapUI:
    """Main UI class for the charging station map application."""

    def __init__(self, map_service: MapService, suggestion_service: SuggestionService,
                 analytics_service: AnalyticsServiceApp, geography_service: GeographyService):
        self.map_service = map_service
        self.suggestion_service = suggestion_service
        self.analytics_service = analytics_service
        self.geography_service = geography_service

    def render_main_page(self):
        """Render the main application page."""
        st.title("Berlin Charging Station Map")
        st.markdown("Interactive visualization of charging infrastructure and demand analysis")

        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Map View", "Analytics", "Suggestions", "About"])

        with tab1:
            self.render_map_view()

        with tab2:
            self.render_analytics_view()

        with tab3:
            self.render_suggestions_view()

        with tab4:
            self.render_about_view()

    def render_map_view(self):
        """Render the interactive map view."""
        st.header("Berlin Charging Infrastructure Map")

        # Heatmap type selection
        heatmap_type = st.radio(
            "Select heatmap type:",
            ["Charging Stations", "Demand Analysis", "Residents"],
            index=0,
            help="Choose which data to visualize as a heatmap"
        )

        # Create base map
        m = folium.Map(location=[52.5200, 13.4050], zoom_start=10)

        # Add the selected heatmap layer
        if heatmap_type == "Charging Stations":
            self._add_charging_stations_heatmap(m)
        elif heatmap_type == "Demand Analysis":
            self._add_demand_heatmap_layer(m)
        elif heatmap_type == "Residents":
            self._add_residents_heatmap(m)

        # Display the map
        folium_static(m)

    def render_analytics_view(self):
        """Render the analytics dashboard."""
        st.header("Analytics Dashboard")

        # Get demand report
        report = self.analytics_service.generate_demand_report()

        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Areas Analyzed", report['total_areas_analyzed'])

        with col2:
            st.metric("High Demand Areas", report['high_demand_areas'])

        with col3:
            st.metric("Areas Needing Stations", report['areas_needing_stations'])

        with col4:
            st.metric("Avg Demand Score", f"{report['average_demand_score']:.1f}")

        # High demand areas table
        st.subheader("High Demand Areas")
        high_demand_areas = self.analytics_service.get_high_demand_areas()

        if high_demand_areas:
            st.write(f"Found {len(high_demand_areas)} high demand areas:")
            for area in high_demand_areas[:10]:  # Show top 10
                st.write(f"- {area}")
        else:
            st.write("No high demand areas identified.")

    def render_suggestions_view(self):
        """Render the suggestions management view."""
        st.header("Charging Station Suggestions")

        # Tabs for different suggestion actions
        tab1, tab2, tab3 = st.tabs(["Submit Suggestion", "Review Suggestions", "View Approved"])

        with tab1:
            self._render_submit_suggestion_form()

        with tab2:
            self._render_review_suggestions()

        with tab3:
            self._render_approved_suggestions()

    def render_about_view(self):
        """Render the about page."""
        st.header("About This Application")

        st.markdown("""
        This application provides an interactive visualization of Berlin's charging infrastructure
        and helps identify areas that may benefit from additional charging stations.

        **Features:**
        - Interactive map showing existing charging stations
        - Demand analysis based on population and current infrastructure
        - Community-driven suggestions for new charging locations
        - Analytics dashboard with key metrics

        **Data Sources:**
        - Charging station data from public APIs
        - Demographic data from Berlin statistical office
        - Geographic boundaries from OpenStreetMap
        """)

    def _add_charging_stations_heatmap(self, map_obj):
        """Add charging stations heatmap to the map."""
        stations_data = self.map_service.generate_charging_stations_layer()

        # Create heatmap data points
        heat_data = []
        if stations_data:
            # Get values for normalization
            counts = list(stations_data.values())
            max_count = max(counts) if counts else 1
            min_count = min(counts) if counts else 0

            for postal_code, count in stations_data.items():
                lat, lon = self._get_postal_code_centroid(postal_code)
                # Normalize count to 0-1 range
                if max_count > min_count:
                    weight = (count - min_count) / (max_count - min_count)
                else:
                    weight = 0.5
                weight = max(0.0, min(1.0, weight))
                heat_data.append([lat, lon, weight])

        if heat_data:
            from folium.plugins import HeatMap
            HeatMap(heat_data).add_to(map_obj)

    def _add_demand_heatmap_layer(self, map_obj):
        """Add demand heatmap layer to the map."""
        heatmap_data = self.map_service.get_heatmap_data()

        # Create heatmap data points
        heat_data = []
        if heatmap_data:
            # Get the actual values for proper normalization
            values = [data_point.value for data_point in heatmap_data]
            max_value = max(values) if values else 1
            min_value = min(values) if values else 0

            for data_point in heatmap_data:
                lat, lon = self._get_postal_code_centroid(data_point.postal_code)
                # Normalize to 0-1 range based on actual data
                if max_value > min_value:
                    weight = (data_point.value - min_value) / (max_value - min_value)
                else:
                    weight = 0.5  # Default if all values are the same
                # Ensure weight is between 0 and 1
                weight = max(0.0, min(1.0, weight))
                heat_data.append([lat, lon, weight])

        if heat_data:
            from folium.plugins import HeatMap
            HeatMap(heat_data).add_to(map_obj)

    def _add_residents_heatmap(self, map_obj):
        """Add residents heatmap to the map."""
        residents_data = self.map_service.generate_residents_layer()

        # Create heatmap data points
        heat_data = []
        if residents_data:
            # Get values for normalization
            populations = list(residents_data.values())
            max_pop = max(populations) if populations else 1
            min_pop = min(populations) if populations else 0

            for postal_code, population in residents_data.items():
                lat, lon = self._get_postal_code_centroid(postal_code)
                # Normalize population to 0-1 range
                if max_pop > min_pop:
                    weight = (population - min_pop) / (max_pop - min_pop)
                else:
                    weight = 0.5
                weight = max(0.0, min(1.0, weight))
                heat_data.append([lat, lon, weight])

        if heat_data:
            from folium.plugins import HeatMap
            HeatMap(heat_data).add_to(map_obj)

    def _render_submit_suggestion_form(self):
        """Render the suggestion submission form."""
        st.subheader("Suggest a New Charging Location")

        with st.form("suggestion_form"):
            postal_code = st.text_input("Berlin Postal Code (PLZ)", max_chars=5)
            address = st.text_input("Address")
            reason = st.text_area("Reason for suggestion")

            submitted = st.form_submit_button("Submit Suggestion")

            if submitted:
                if not postal_code or not address or not reason:
                    st.error("Please fill in all fields.")
                else:
                    try:
                        suggestion = self.suggestion_service.submit_suggestion(
                            postal_code, address, reason
                        )
                        st.success(f"Suggestion submitted successfully! ID: {suggestion.id}")
                    except ValueError as e:
                        st.error(str(e))

    def _render_review_suggestions(self):
        """Render the suggestion review interface."""
        st.subheader("Review Pending Suggestions")

        pending_suggestions = self.suggestion_service.get_pending_suggestions()

        if not pending_suggestions:
            st.write("No pending suggestions to review.")
            return

        for suggestion in pending_suggestions:
            with st.expander(f"Suggestion #{suggestion.id} - PLZ {suggestion.postal_code}"):

                st.write(f"**Address:** {suggestion.address}")
                st.write(f"**Reason:** {suggestion.reason}")
                st.write(f"**Submitted:** {suggestion.submitted_at.strftime('%Y-%m-%d %H:%M')}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Approve #{suggestion.id}", key=f"approve_{suggestion.id}"):
                        reviewer = st.session_state.get('reviewer', 'Anonymous')
                        success = self.suggestion_service.review_suggestion(
                            suggestion.id, 'approve', reviewer
                        )
                        if success:
                            st.success("Suggestion approved!")
                            st.rerun()
                        else:
                            st.error("Failed to approve suggestion.")

                with col2:
                    if st.button(f"Reject #{suggestion.id}", key=f"reject_{suggestion.id}"):
                        reviewer = st.session_state.get('reviewer', 'Anonymous')
                        success = self.suggestion_service.review_suggestion(
                            suggestion.id, 'reject', reviewer
                        )
                        if success:
                            st.success("Suggestion rejected!")
                            st.rerun()
                        else:
                            st.error("Failed to reject suggestion.")

    def _render_approved_suggestions(self):
        """Render approved suggestions list."""
        st.subheader("Approved Suggestions")

        approved_suggestions = self.suggestion_service.get_approved_suggestions()

        if not approved_suggestions:
            st.write("No approved suggestions yet.")
            return

        for suggestion in approved_suggestions:
            with st.expander(f"Suggestion #{suggestion.id} - PLZ {suggestion.postal_code}"):
                st.write(f"**Address:** {suggestion.address}")
                st.write(f"**Reason:** {suggestion.reason}")
                st.write(f"**Submitted:** {suggestion.submitted_at.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Approved by:** {suggestion.review_info.reviewer}")
                if suggestion.review_info.notes:
                    st.write(f"**Notes:** {suggestion.review_info.notes}")

    def _get_postal_code_centroid(self, postal_code: str) -> tuple:
        """Get centroid coordinates for a Berlin postal code."""
        try:
            centroid = self.geography_service.get_centroid_for_postal_code(postal_code)
            if centroid:
                return (centroid.latitude, centroid.longitude)
        except Exception as e:
            print(f"Exception during centroid lookup for PLZ {postal_code}: {e}")

        print(f"Centroid not found for PLZ {postal_code}, using Berlin center fallback.")
        # Fallback to Berlin center if centroid not found
        return (52.5200, 13.4050)