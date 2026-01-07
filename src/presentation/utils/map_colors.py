"""
Color mapping utilities for map visualization.

Contains functions for creating color scales for heatmap layers.
"""
from branca.colormap import LinearColormap


def create_color_map(vmin, vmax, colors=None):
    """
    Create a linear color map for visualization.

    Args:
        vmin: Minimum value for the color scale.
        vmax: Maximum value for the color scale.
        colors: List of colors for the gradient. Defaults to yellow-red.

    Returns:
        LinearColormap instance.
    """
    if colors is None:
        colors = ['yellow', 'red']
    return LinearColormap(colors=colors, vmin=vmin, vmax=vmax)
