"""
Interactive Mapping and Geospatial Layer Management for EARTH VISION-X.
Generates Folium interactive maps displaying:
- AOI bounding box and polygon
- T1 (2016) True Color Satellite Layer
- T2 (2026) True Color Satellite Layer
- Binary Change Mask Overlay with color-coded classification
- NDVI and NDWI Delta Layers
- Layer Control and coordinates tooltips
"""

import folium
from folium import plugins
from typing import Dict, Any, Tuple, Optional
import numpy as np
import base64
import io
from PIL import Image

class MapVisualizer:
    """
    Creates rich interactive Folium maps with layer controls.
    """

    @staticmethod
    def _array_to_data_url(img_rgb: np.ndarray) -> str:
        """Converts RGB numpy array to base64 PNG data URL for Folium ImageOverlay."""
        img_u8 = (np.clip(img_rgb, 0.0, 1.0) * 255).astype(np.uint8) if img_rgb.max() <= 1.0 else img_rgb.astype(np.uint8)
        pil_img = Image.fromarray(img_u8)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    @staticmethod
    def create_interactive_map(
        lat: float,
        lon: float,
        aoi_bbox: Tuple[float, float, float, float],
        img_t1: Optional[np.ndarray] = None,
        img_t2: Optional[np.ndarray] = None,
        change_mask: Optional[np.ndarray] = None,
        ndvi_change: Optional[np.ndarray] = None,
        zoom_start: int = 12
    ) -> folium.Map:
        """
        Creates multi-layer Folium interactive map.
        bbox format: (min_lat, min_lon, max_lat, max_lon)
        """
        min_lat, min_lon, max_lat, max_lon = aoi_bbox
        bounds = [[min_lat, min_lon], [max_lat, max_lon]]

        # Base map with dark / satellite styling
        m = folium.Map(
            location=[lat, lon],
            zoom_start=zoom_start,
            tiles="CartoDB dark_matter",
            control_scale=True
        )

        # Optional Google / Esri satellite tile layer
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            name="🛰️ Esri Satellite Basemap",
            overlay=False
        ).add_to(m)

        # 1. AOI Bounding Box Polygon
        folium.Rectangle(
            bounds=bounds,
            color="#38BDF8",
            weight=2,
            fill=True,
            fill_color="#38BDF8",
            fill_opacity=0.08,
            name="📍 Area of Interest (AOI)",
            tooltip=f"AOI Centroid: ({lat:.4f}, {lon:.4f})"
        ).add_to(m)

        # 2. T1 (2016) Satellite Image Overlay
        if img_t1 is not None:
            t1_url = MapVisualizer._array_to_data_url(img_t1)
            folium.raster_layers.ImageOverlay(
                image=t1_url,
                bounds=bounds,
                opacity=0.9,
                name="📷 T1 Satellite Imagery (2016)",
                interactive=True
            ).add_to(m)

        # 3. T2 (2026) Satellite Image Overlay
        if img_t2 is not None:
            t2_url = MapVisualizer._array_to_data_url(img_t2)
            folium.raster_layers.ImageOverlay(
                image=t2_url,
                bounds=bounds,
                opacity=0.9,
                name="📷 T2 Satellite Imagery (2026)",
                interactive=True
            ).add_to(m)

        # 4. Change Mask Overlay (Red highlights for detected change)
        if change_mask is not None:
            # Color changed pixels in luminous red/coral with transparency
            h, w = change_mask.shape[:2]
            rgba = np.zeros((h, w, 4), dtype=np.uint8)
            changed = change_mask > 0
            rgba[changed, 0] = 239 # R
            rgba[changed, 1] = 68  # G
            rgba[changed, 2] = 68  # B
            rgba[changed, 3] = 190 # Alpha

            pil_mask = Image.fromarray(rgba, mode="RGBA")
            buf = io.BytesIO()
            pil_mask.save(buf, format="PNG")
            mask_url = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

            folium.raster_layers.ImageOverlay(
                image=mask_url,
                bounds=bounds,
                opacity=0.85,
                name="🎯 Detected Change Mask",
                interactive=True
            ).add_to(m)

        # 5. NDVI Change Overlay (Green for vegetation gain, orange for loss)
        if ndvi_change is not None:
            h, w = ndvi_change.shape[:2]
            ndvi_rgba = np.zeros((h, w, 4), dtype=np.uint8)
            loss = ndvi_change < -0.15
            gain = ndvi_change > 0.15

            # Loss: Orange/Red
            ndvi_rgba[loss, 0] = 249
            ndvi_rgba[loss, 1] = 115
            ndvi_rgba[loss, 2] = 22
            ndvi_rgba[loss, 3] = 175

            # Gain: Emerald
            ndvi_rgba[gain, 0] = 16
            ndvi_rgba[gain, 1] = 185
            ndvi_rgba[gain, 2] = 129
            ndvi_rgba[gain, 3] = 175

            pil_ndvi = Image.fromarray(ndvi_rgba, mode="RGBA")
            buf2 = io.BytesIO()
            pil_ndvi.save(buf2, format="PNG")
            ndvi_url = f"data:image/png;base64,{base64.b64encode(buf2.getvalue()).decode('utf-8')}"

            folium.raster_layers.ImageOverlay(
                image=ndvi_url,
                bounds=bounds,
                opacity=0.75,
                name="🌱 NDVI Canopy Variance Layer",
                interactive=True
            ).add_to(m)

        # Fullscreen and Layer Controls
        plugins.Fullscreen(position="topright").add_to(m)
        folium.LayerControl(position="topright", collapsed=False).add_to(m)

        return m
