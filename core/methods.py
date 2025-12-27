import pandas                        as pd
import geopandas                     as gpd
import core.HelperTools              as ht

import folium
import numpy as np
# from folium.plugins import HeatMap
import streamlit as st
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
import json
import os
from datetime import datetime
from src.domain.events.suggestion_handled import save_suggestion
from src.domain.events.load_suggestion import load_suggestions

def sort_by_plz_add_geometry(dfr, dfg, pdict): 
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()
    
    sorted_df               = dframe\
        .sort_values(by='PLZ')\
        .reset_index(drop=True)\
        .sort_index()
        
    sorted_df2              = sorted_df.merge(df_geo, on=pdict["geocode"], how ='left')
    sorted_df3              = sorted_df2.dropna(subset=['geometry'])
    
    # Geometry column may already contain shapely geometry objects or WKT strings.
    try:
        # If values are WKT strings, this will succeed.
        sorted_df3['geometry'] = gpd.GeoSeries.from_wkt(sorted_df3['geometry'])
    except Exception:
        # Otherwise, assume they're already geometry objects and construct GeoSeries directly.
        sorted_df3['geometry'] = gpd.GeoSeries(sorted_df3['geometry'])

    ret = gpd.GeoDataFrame(sorted_df3, geometry='geometry')

    return ret
    

# -----------------------------------------------------------------------------
@ht.timer
def preprop_lstat(dfr, dfg, pdict):
    """Preprocessing dataframe from Ladesaeulenregister.csv"""
    dframe = dfr.copy()
    df_geo = dfg.copy()

    dframe2 = dframe.loc[:, ['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']]
    dframe2.rename(columns={"Nennleistung Ladeeinrichtung [kW]": "KW", "Postleitzahl": "PLZ"}, inplace=True)

    # Normalize PLZ to numeric to ensure consistent joins with geodata
    dframe2['PLZ'] = pd.to_numeric(dframe2['PLZ'], errors='coerce')

    # Convert lat/lon to string and replace comma decimals with dot
    dframe2['Breitengrad'] = dframe2['Breitengrad'].astype(str).str.replace(',', '.')
    dframe2['Längengrad'] = dframe2['Längengrad'].astype(str).str.replace(',', '.')

    dframe3 = dframe2[(dframe2["Bundesland"] == 'Berlin') & (dframe2["PLZ"] > 10115) & (dframe2["PLZ"] < 14200)]

    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    return ret

def count_plz_occurrences(df_lstat2):
    """Counts loading stations per PLZ"""
    # Group by PLZ and count occurrences, keeping geometry
    result_df = df_lstat2.groupby('PLZ').agg(
        Number=('PLZ', 'count'),
        geometry=('geometry', 'first')
    ).reset_index()
    
    return result_df


def review_suggestion(suggestion_id, status, reviewer="Admin", notes=""):
    """Review a suggestion (approve/reject)"""
    suggestions = load_suggestions()
    for suggestion in suggestions:
        if suggestion.get('id') == suggestion_id:
            suggestion['status'] = status
            suggestion['reviewed_by'] = reviewer
            suggestion['review_date'] = datetime.now().isoformat()
            suggestion['review_notes'] = notes
            break

    suggestions_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'suggestions.json')
    with open(suggestions_file, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, indent=2, ensure_ascii=False)


def get_plz_centroid(plz, df_geo):
    """Get centroid coordinates for a PLZ"""
    try:
        plz_int = int(plz)
        geo_row = df_geo[df_geo['PLZ'] == plz_int]
        if not geo_row.empty:
            geom = geo_row.iloc[0]['geometry']
            if hasattr(geom, 'centroid'):
                return geom.centroid.y, geom.centroid.x
    except:
        pass
    return None, None
    
# -----------------------------------------------------------------------------
# @ht.timer
# def preprop_geb(dfr, pdict):
#     """Preprocessing dataframe from gebaeude.csv"""
#     dframe      = dfr.copy()
    
#     dframe2     = dframe .loc[:,['lag', 'bezbaw', 'geometry']]
#     dframe2.rename(columns      = {"bezbaw":"Gebaeudeart", "lag": "PLZ"}, inplace = True)
    
    
#     # Now, let's filter the DataFrame
#     dframe3 = dframe2[
#         dframe2['PLZ'].notna() &  # Remove NaN values
#         ~dframe2['PLZ'].astype(str).str.contains(',') &  # Remove entries with commas
#         (dframe2['PLZ'].astype(str).str.len() <= 5)  # Keep entries with 5 or fewer characters
#         ]
    
#     # Convert PLZ to numeric, coercing errors to NaN
#     dframe3['PLZ_numeric'] = pd.to_numeric(dframe3['PLZ'], errors='coerce')

#     # Filter for PLZ between 10000 and 14200
#     filtered_df = dframe3[
#         (dframe3['PLZ_numeric'] >= 10000) & 
#         (dframe3['PLZ_numeric'] <= 14200)
#     ]

#     # Drop the temporary numeric column
#     filtered_df2 = filtered_df.drop('PLZ_numeric', axis=1)
    
#     filtered_df3 = filtered_df2[filtered_df2['Gebaeudeart'].isin(['Freistehendes Einzelgebäude', 'Doppelhaushälfte'])]
    
#     filtered_df4 = (filtered_df3\
#                  .assign(PLZ=lambda x: pd.to_numeric(x['PLZ'], errors='coerce'))[['PLZ', 'Gebaeudeart', 'geometry']]
#                  .sort_values(by='PLZ')
#                  .reset_index(drop=True)
#                  )
    
#     ret                     = filtered_df4.dropna(subset=['geometry'])
        
#     return ret
    
# -----------------------------------------------------------------------------
@ht.timer
def preprop_resid(dfr, dfg, pdict):
    """Preprocessing dataframe from plz_einwohner.csv"""
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()    
    
    dframe2               	= dframe.loc[:,['plz', 'einwohner', 'lat', 'lon']]
    dframe2.rename(columns  = {"plz": "PLZ", "einwohner": "Einwohner", "lat": "Breitengrad", "lon": "Längengrad"}, inplace = True)

    # Convert to string
    dframe2['Breitengrad']  = dframe2['Breitengrad'].astype(str)
    dframe2['Längengrad']   = dframe2['Längengrad'].astype(str)

    # Now replace the commas with periods
    dframe2['Breitengrad']  = dframe2['Breitengrad'].str.replace(',', '.')
    dframe2['Längengrad']   = dframe2['Längengrad'].str.replace(',', '.')

    dframe3                 = dframe2[ 
                                            (dframe2["PLZ"] > 10000) &  
                                            (dframe2["PLZ"] < 14200)]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    
    return ret


# -----------------------------------------------------------------------------
@ht.timer
def make_streamlit_electric_Charging_resid(dfr1, dfr2):
    """
    UI Presentation Layer: 
    Displays the interactive map based on pre-calculated demand and station data.
    """
    # 1. Standardize column names for the UI to match our Entities
    # Ensuring we use the results from our on_demand_calculated event
    dframe_stations = dfr1.copy()
    dframe_analysis = dfr2.copy()

    st.title('Heatmaps: Electric Charging Stations and Residents')

    # Add tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Map View", "Suggest Location", "View Suggestions"])

    with tab1:
        layer_selection = st.radio("Select Layer", ("Residents", "Charging_Stations", "Demand"))

        # Create a Folium map centered on Berlin
        m = folium.Map(location=[52.52, 13.40], zoom_start=10)

        # --- LAYER: RESIDENTS ---
        if layer_selection == "Residents":
            # Uses 'einwohner' column from our ResidentRecord entity
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

        # --- LAYER: CHARGING STATIONS ---
        elif layer_selection == "Charging_Stations":
            # Uses 'count' column from our StationCount entity
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

        # --- LAYER: DEMAND ---
        elif layer_selection == "Demand":
            # USES PRE-CALCULATED 'demand' column from our DemandResult entity
            # We only keep the visual "vmax" logic here to handle outliers
            vmax = int(np.nanpercentile(dframe_analysis['demand'].replace(0, np.nan).dropna(), 95)) \
                   if dframe_analysis['demand'].notna().any() else 1
            
            color_map = LinearColormap(colors=['yellow', 'red'], vmin=0, vmax=vmax)

            for idx, row in dframe_analysis.iterrows():
                val = float(row['demand'])
                display_val = min(val, vmax) # Cap visual color at 95th percentile
                
                folium.GeoJson(
                    row['geometry'],
                    style_function=lambda x, color=color_map(display_val): {
                        'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7
                    },
                    tooltip=f"PLZ: {row['PLZ']}, Demand: {val:.1f} (res/station)"
                ).add_to(m)
            
            color_map.caption = 'Residents per charging station (capped at 95th percentile)'

        # Add common map elements
        color_map.add_to(m)
        folium.LayerControl().add_to(m)
        folium_static(m)

        with tab2:
            st.header("Suggest New Charging Location")
            st.write("Help improve Berlin's charging infrastructure by suggesting new locations where charging stations are needed.")

            with st.form("suggestion_form"):
                col1, col2 = st.columns(2)
                with col1:
                    plz = st.text_input("Postal Code (PLZ)", placeholder="e.g., 10115")
                with col2:
                    address = st.text_input("Address/Location Description", placeholder="Street name, building, or area")

                reason = st.text_area("Why is this location needed?", placeholder="Describe the need for charging stations here...")

                submitted = st.form_submit_button("Submit Suggestion")

                if submitted:
                    if not plz.strip():
                        st.error("Please enter a postal code")
                    elif not address.strip():
                        st.error("Please enter an address or location description")
                    elif not reason.strip():
                        st.error("Please explain why this location needs charging stations")
                    else:
                        try:
                            plz_int = int(plz.strip())
                            if 10000 <= plz_int <= 14200:
                                suggestion = {
                                    "plz": plz.strip(),
                                    "address": address.strip(),
                                    "reason": reason.strip()
                                }
                                save_suggestion(suggestion)
                                st.success("✅ Thank you! Your suggestion has been submitted and will be reviewed.")
                                st.balloons()
                            else:
                                st.error("Please enter a valid Berlin postal code (10000-14200)")
                        except ValueError:
                            st.error("Please enter a valid 5-digit postal code")

        with tab3:
            st.header("Community Suggestions")
            st.write("See suggestions from the community for new charging locations.")

            # --- CHANGED: Admin password protection ---
            admin_password = st.text_input("Enter Admin Password to review", type="password")
            
            if admin_password == "advanced":
                admin_mode = True
                st.success("Admin mode unlocked ✅")
            else:
                admin_mode = False
                st.info("Enter the correct admin password to unlock review features.")
            # ------------------------------------------

            suggestions = load_suggestions()

            if not suggestions:
                st.info("No suggestions yet. Be the first to suggest a new charging location!")
            else:
                st.write(f"**Total suggestions:** {len(suggestions)}")

                # Group suggestions by PLZ
                suggestions_by_plz = {}
                for s in suggestions:
                    plz = s.get('plz', 'Unknown')
                    if plz not in suggestions_by_plz:
                        suggestions_by_plz[plz] = []
                    suggestions_by_plz[plz].append(s)

                # Display suggestions grouped by PLZ
                for plz in sorted(suggestions_by_plz.keys()):
                    with st.expander(f"📍 PLZ {plz} ({len(suggestions_by_plz[plz])} suggestions)"):
                        for suggestion in suggestions_by_plz[plz]:
                            status = suggestion.get('status', 'pending')
                            status_emoji = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(status, "❓")

                            st.write(f"{status_emoji} **Location:** {suggestion.get('address', 'N/A')}")
                            st.write(f"**Reason:** {suggestion.get('reason', 'N/A')}")
                            st.write(f"**Status:** {status.title()}")

                            timestamp = suggestion.get('timestamp', '')
                            if timestamp:
                                try:
                                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    st.caption(f"Suggested on {dt.strftime('%Y-%m-%d %H:%M')}")
                                except:
                                    st.caption(f"Suggested: {timestamp}")

                            # Show review info if available
                            if suggestion.get('reviewed_by'):
                                st.caption(f"Reviewed by {suggestion['reviewed_by']} on {suggestion.get('review_date', '')[:10]}")
                                if suggestion.get('review_notes'):
                                    st.caption(f"Notes: {suggestion['review_notes']}")

                            # Admin review buttons (Only visible if admin_mode is True)
                            if admin_mode and status == 'pending':
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    if st.button(f"✅ Approve #{suggestion['id']}", key=f"approve_{suggestion['id']}"):
                                        review_suggestion(suggestion['id'], 'approved', 'Admin')
                                        st.success("Suggestion approved!")
                                        st.rerun()
                                with col2:
                                    if st.button(f"❌ Reject #{suggestion['id']}", key=f"reject_{suggestion['id']}"):
                                        review_suggestion(suggestion['id'], 'rejected', 'Admin')
                                        st.success("Suggestion rejected!")
                                        st.rerun()
                                with col3:
                                    notes = st.text_input(f"Notes for #{suggestion['id']}", key=f"notes_{suggestion['id']}")
                                    if st.button(f"💬 Add Notes #{suggestion['id']}", key=f"add_notes_{suggestion['id']}"):
                                        review_suggestion(suggestion['id'], status, 'Admin', notes)
                                        st.success("Notes added!")
                                        st.rerun()

                            st.divider()
