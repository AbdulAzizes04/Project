"""
Digital Twin 3D Model Generator for BuildVerse AI.
Generates 3D Plotly BIM structural elements colored dynamically with rich cyan color palette and crisp architectural edges.
"""

import plotly.graph_objects as go
from typing import List, Dict, Any

STATUS_STYLES = {
    "Completed": {"color": "#0891B2", "opacity": 0.85, "line": "#0E7490"},    # Rich Vibrant Cyan
    "In-Progress": {"color": "#38BDF8", "opacity": 0.65, "line": "#0284C7"},  # Electric Light Cyan
    "Pending": {"color": "#E2E8F0", "opacity": 0.25, "line": "#94A3B8"}       # Subtle Translucent Slate
}

def generate_digital_twin_3d(twin_elements: List[Dict[str, Any]]) -> go.Figure:
    """Generates an interactive 3D Digital Twin model with distinct floor levels and cyan color palette."""
    fig = go.Figure()
    
    if not twin_elements:
        twin_elements = [
            {"element_name": "Foundation Slab", "phase": "Foundation", "status": "Completed", "box": [0, 0, 0, 40, 50, 2]},
            {"element_name": "Ground Columns & Walls", "phase": "Columns", "status": "Completed", "box": [1, 1, 2, 38, 48, 10]},
            {"element_name": "1st Floor Slab & Beams", "phase": "Slab", "status": "Completed", "box": [0, 0, 12, 40, 50, 2]},
            {"element_name": "2nd Floor Brick Walls", "phase": "Brick Work", "status": "In-Progress", "box": [1, 1, 14, 38, 48, 10]},
            {"element_name": "Plastering & Wiring", "phase": "Plastering", "status": "In-Progress", "box": [1.5, 1.5, 14.5, 37, 47, 9]},
            {"element_name": "Roof & Parapet", "phase": "Finishing", "status": "Pending", "box": [0, 0, 24, 40, 50, 3]}
        ]
        
    for elem in twin_elements:
        name = elem.get("element_name", "Element")
        status = elem.get("status", "Pending")
        box = elem.get("box", [0, 0, 0, 10, 10, 5])
        
        x0, y0, z0, dx, dy, dz = box
        x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
        
        style = STATUS_STYLES.get(status, STATUS_STYLES["Pending"])
        color = style["color"]
        opacity = style["opacity"]
        line_color = style["line"]
        
        # 3D Box Mesh
        fig.add_trace(go.Mesh3d(
            x=[x0, x1, x1, x0, x0, x1, x1, x0],
            y=[y0, y0, y1, y1, y0, y0, y1, y1],
            z=[z0, z0, z0, z0, z1, z1, z1, z1],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color,
            opacity=opacity,
            name=f"{name} ({status})",
            flatshading=True
        ))

        # Distinct 3D Wireframe Edges
        wx = [x0, x1, x1, x0, x0, x0, x1, x1, x0, x0, x1, x1, x1, x1, x0, x0]
        wy = [y0, y0, y1, y1, y0, y0, y0, y0, y0, y1, y1, y1, y1, y1, y1, y1]
        wz = [z0, z0, z0, z0, z0, z1, z1, z0, z1, z1, z0, z1, z1, z0, z0, z1]

        fig.add_trace(go.Scatter3d(
            x=wx, y=wy, z=wz,
            mode="lines",
            line=dict(color=line_color, width=2.5),
            showlegend=False
        ))

    fig.update_layout(
        title="Live 3D Digital Twin Structural Model",
        scene=dict(
            xaxis=dict(title="Width X (ft)", backgroundcolor="#FFFFFF", gridcolor="#E2E8F0"),
            yaxis=dict(title="Length Y (ft)", backgroundcolor="#FFFFFF", gridcolor="#E2E8F0"),
            zaxis=dict(title="Height Z (ft)", backgroundcolor="#FFFFFF", gridcolor="#E2E8F0"),
            camera=dict(eye=dict(x=1.4, y=1.4, z=1.2)),
            aspectmode="data"
        ),
        paper_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=40, b=10),
        height=650
    )
    
    return fig
