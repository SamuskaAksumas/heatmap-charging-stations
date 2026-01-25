<<<<<<< HEAD
"""Render demand heatmap on Folium map."""
=======
>>>>>>> 607d696 (Revamp project structure using DDD approach)
import folium
import numpy as np
from branca.colormap import LinearColormap

<<<<<<< HEAD

def display_demand(m, dframe_analysis):
    """Render demand heatmap layer with color gradient (yellow→red)."""
    # Calculate vmax based on 95th percentile to handle outliers
    demand_values = dframe_analysis['demand'].replace(0, np.nan).dropna()

=======
def display_demand(m: folium.Map, dframe_analysis):
    """
    Domain Service: Renders the demand heatmap.
    
    This function takes the results calculated by the DemandAggregate and 
    visualizes them. Logic remains here to keep the domain context self-contained.
    """
    # Filter out 0 or NaN for color scaling
    demand_values = dframe_analysis['demand'].replace(0, np.nan).dropna()

    # Calculate vmax based on 95th percentile to handle outliers (e.g., areas with 0 stations)
>>>>>>> 607d696 (Revamp project structure using DDD approach)
    if not demand_values.empty:
        vmax = int(np.nanpercentile(demand_values, 95))
    else:
        vmax = 1

    color_map = LinearColormap(colors=['yellow', 'red'], vmin=0, vmax=vmax)

    for _, row in dframe_analysis.iterrows():
        val = float(row['demand'])
<<<<<<< HEAD
        display_val = min(val, vmax) # Cap visual color for better heatmap contrast
=======
        # Cap visual color at vmax for better contrast
        display_val = min(val, vmax) 
>>>>>>> 607d696 (Revamp project structure using DDD approach)

        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=color_map(display_val): {
<<<<<<< HEAD
                'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7
            },
            tooltip=f"PLZ: {row['PLZ']}, Demand: {val:.1f} (res/station)"
        ).add_to(m)

    color_map.caption = 'Residents per charging station (Demand Score)'
    color_map.add_to(m)
    return m
=======
                'fillColor': color, 
                'color': 'black', 
                'weight': 1, 
                'fillOpacity': 0.7
            },
            tooltip=f"PLZ: {row['PLZ']}, Residents: {row['Einwohner']}, Demand: {val:.1f}"
        ).add_to(m)

    color_map.caption = 'Demand Score (Residents per Station)'
    color_map.add_to(m)
    
    return m
>>>>>>> 607d696 (Revamp project structure using DDD approach)
