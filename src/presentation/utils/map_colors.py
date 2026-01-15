"""Color mapping utilities for heatmap visualization."""
from branca.colormap import LinearColormap


def create_color_map(vmin, vmax, colors=None):
    """Create linear color map (default: yellow→red)."""
    if colors is None:
        colors = ['yellow', 'red']
    return LinearColormap(colors=colors, vmin=vmin, vmax=vmax)
