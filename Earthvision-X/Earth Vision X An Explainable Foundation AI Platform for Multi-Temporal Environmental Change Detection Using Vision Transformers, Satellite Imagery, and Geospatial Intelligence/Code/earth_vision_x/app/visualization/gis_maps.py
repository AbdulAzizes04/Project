"""
Interactive GIS Map Engine.
Provides interactive satellite map view, temporal side-by-side comparison,
multiple basemap providers (Esri Satellite, OpenStreetMap, Terrain), layer controls,
prediction overlays, measurement tools, and Folium plugins.
"""

import numpy as np
import base64
from io import BytesIO
from PIL import Image

try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

class GISMapVisualizer:
    @staticmethod
    def _array_to_base64_url(img_array: np.ndarray) -> str:
        img_uint = (img_array * 255).astype(np.uint8) if img_array.max() <= 1.0 else img_array.astype(np.uint8)
        pil_img = Image.fromarray(img_uint)
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG")
        b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64_str}"

    @staticmethod
    def create_interactive_map(
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        lat: float = 12.9716,
        lon: float = 77.5946,
        zoom: int = 14,
        overlay_img: np.ndarray = None
    ):
        """
        Creates interactive Folium GIS map with multiple basemaps and layer controls.
        """
        if not FOLIUM_AVAILABLE:
            return None

        # Base Map with Satellite Tiles
        m = folium.Map(location=[lat, lon], zoom_start=zoom, tiles=None)

        # 1. Esri World Imagery (Satellite)
        folium.TileLayer(
            tiles="https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            name="🛰️ Esri Satellite Basemap",
            overlay=False,
            control=True
        ).add_to(m)

        # 2. OpenStreetMap Standard
        folium.TileLayer(
            tiles="openstreetmap",
            name="🗺️ OpenStreetMap Standard",
            overlay=False,
            control=True
        ).add_to(m)

        # 3. Terrain / Topography Basemap
        folium.TileLayer(
            tiles="https://services.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Topo Map",
            name="🏔️ Terrain & Topography Basemap",
            overlay=False,
            control=True
        ).add_to(m)

        # Convert images to base64
        t1_url = GISMapVisualizer._array_to_base64_url(img_t1)
        t2_url = GISMapVisualizer._array_to_base64_url(img_t2)

        delta = 0.025
        bounds = [[lat - delta, lon - delta], [lat + delta, lon + delta]]

        # Raster Overlays
        folium.raster_layers.ImageOverlay(
            name="📷 Sentinel-2 Time 1 (Before)",
            image=t1_url,
            bounds=bounds,
            opacity=0.85
        ).add_to(m)

        folium.raster_layers.ImageOverlay(
            name="📷 Sentinel-2 Time 2 (After)",
            image=t2_url,
            bounds=bounds,
            opacity=0.85
        ).add_to(m)

        if overlay_img is not None:
            ov_url = GISMapVisualizer._array_to_base64_url(overlay_img)
            folium.raster_layers.ImageOverlay(
                name="🎯 AI Prediction Overlay",
                image=ov_url,
                bounds=bounds,
                opacity=0.75
            ).add_to(m)

        # Add Measure Tool and Draw AOI Plugins
        try:
            plugins.MeasureControl(position="topright", active_color="#38BDF8", completed_color="#10B981").add_to(m)
            plugins.Draw(export=True, filename="aoi_bbox.geojson").add_to(m)
        except Exception:
            pass

        folium.LayerControl(collapsed=False).add_to(m)
        return m

