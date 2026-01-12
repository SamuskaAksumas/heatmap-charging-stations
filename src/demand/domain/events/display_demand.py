"""Render demand heatmap on Folium map."""
import folium
import numpy as np
from branca.colormap import LinearColormap


def display_demand(m, dframe_analysis):
    """Render demand heatmap layer with color gradient (yellow→red)."""
    # Calculate vmax based on 95th percentile to handle outliers
    demand_values = dframe_analysis['demand'].replace(0, np.nan).dropna()
    
    if not demand_values.empty:
        vmax = int(np.nanpercentile(demand_values, 95))
    else:
        vmax = 1
        
    color_map = LinearColormap(colors=['yellow', 'red'], vmin=0, vmax=vmax)

    for idx, row in dframe_analysis.iterrows():
        val = float(row['demand'])
        display_val = min(val, vmax) # Cap visual color for better heatmap contrast
        
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=color_map(display_val): {
                'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7
            },
            tooltip=f"PLZ: {row['PLZ']}, Demand: {val:.1f} (res/station)"
        ).add_to(m)
    
    color_map.caption = 'Residents per charging station (Demand Score)'
    color_map.add_to(m)
    return m