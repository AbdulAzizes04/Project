"""
AI Architectural Floor Plan & 3D Model Generator.
Generates 2D vector layouts with wall thickness, doors, windows, measurements, and 3D house mesh preview.
"""

import plotly.graph_objects as go
import numpy as np
from typing import List, Dict, Any
from ai.planner.room_optimizer import optimize_room_placements

ROOM_COLORS = {
    "Bedrooms": "#E0F2FE",      # Light Cyan Accent
    "Kitchen": "#FEF08A",       # Light Yellow
    "Hall": "#CFFAFE",          # Soft Cyan
    "Dining": "#ECFDF5",       # Soft Mint
    "Bathrooms": "#F1F5F9",    # Slate Light
    "Balcony": "#E0E7FF",      # Soft Indigo
    "Parking": "#E2E8F0",      # Light Gray
    "Staircase": "#FCE7F3",    # Light Pink
    "Utility Room": "#F3E8FF",  # Light Purple
    "Store Room": "#FEF3C7",   # Soft Amber
    "Garden": "#DCFCE7"        # Light Green
}

def generate_2d_floor_plan(
    rooms: List[Dict[str, Any]],
    plot_width: float = 40.0,
    plot_length: float = 50.0,
    floor_name: str = "Ground Floor"
) -> go.Figure:
    """Generates a professional 2D architectural blueprint floor plan using Plotly with Cyan themes."""
    placed_rooms = optimize_room_placements(rooms, plot_width, plot_length)
    
    fig = go.Figure()
    
    # 1. Draw Outer Plot Boundary
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=plot_width, y1=plot_length,
        line=dict(color="#0891B2", width=3, dash="dash"),
        fillcolor="rgba(248, 250, 252, 0.5)"
    )
    
    # Plot Boundary Annotation
    fig.add_annotation(
        x=plot_width / 2, y=plot_length + 2,
        text=f"PLOT BOUNDARY ({plot_width} ft x {plot_length} ft)",
        showarrow=False,
        font=dict(size=12, color="#0891B2", family="Inter")
    )

    # 2. Render each room with wall thickness, doors, windows, and labels
    wall_thick = 0.75 # 9 inches
    
    for r in placed_rooms:
        x, y = r["x"], r["y"]
        w, l = r["width"], r["length"]
        rtype = r["room_type"]
        bg_color = ROOM_COLORS.get(rtype, "#E0F2FE")
        
        # Room outer wall rectangle
        fig.add_shape(
            type="rect",
            x0=x, y0=y, x1=x + w, y1=y + l,
            line=dict(color="#0F172A", width=2.5),
            fillcolor=bg_color,
            opacity=0.85
        )
        
        # Inner wall line (Double-wall architectural effect)
        fig.add_shape(
            type="rect",
            x0=x + wall_thick, y0=y + wall_thick,
            x1=x + w - wall_thick, y1=y + l - wall_thick,
            line=dict(color="#64748B", width=1, dash="dot")
        )
        
        # Door Symbol (Arc & Swing)
        doors_count = r.get("doors", 1)
        if doors_count > 0:
            door_x = x + w / 2
            door_y = y
            fig.add_shape(
                type="line",
                x0=door_x - 1.5, y0=door_y, x1=door_x + 1.5, y1=door_y,
                line=dict(color="#FFFFFF", width=3) # Door cutout
            )
            fig.add_shape(
                type="line",
                x0=door_x - 1.5, y0=door_y, x1=door_x - 1.5, y1=door_y + 2.5,
                line=dict(color="#0891B2", width=2) # Door leaf
            )

        # Window Symbol (Double Line Slot)
        windows_count = r.get("windows", 1)
        if windows_count > 0:
            win_y = y + l / 2
            fig.add_shape(
                type="line",
                x0=x, y0=win_y - 1.5, x1=x, y1=win_y + 1.5,
                line=dict(color="#0284C7", width=4) # Window frame
            )

        # Room Text Label & Dimension Measurement
        fig.add_annotation(
            x=x + w / 2, y=y + l / 2,
            text=f"<b>{rtype}</b><br>{w:.1f}' x {l:.1f}'<br>({w*l:.0f} sq.ft)",
            showarrow=False,
            font=dict(size=11, color="#0F172A", family="Inter"),
            align="center"
        )
        
    fig.update_layout(
        title=f"2D Architectural Floor Plan — {floor_name}",
        xaxis=dict(range=[-3, plot_width + 5], showgrid=True, gridcolor="#E2E8F0", zeroline=False),
        yaxis=dict(range=[-3, plot_length + 5], showgrid=True, gridcolor="#E2E8F0", zeroline=False, scaleanchor="x"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=50, b=20),
        height=550
    )
    
    return fig

def generate_3d_house_preview(floors: List[Dict[str, Any]], plot_width: float = 40.0, plot_length: float = 50.0) -> go.Figure:
    """Generates an interactive 3D House Preview visual model using Plotly Mesh3d/Scatter3d."""
    fig = go.Figure()
    
    wall_height = 10.0 # 10ft per floor
    
    for f_idx, floor in enumerate(floors):
        z_base = f_idx * wall_height
        z_top = z_base + wall_height
        rooms = floor.get("rooms", [])
        placed_rooms = optimize_room_placements(rooms, plot_width, plot_length)
        
        # Floor Slab
        fig.add_trace(go.Mesh3d(
            x=[0, plot_width, plot_width, 0],
            y=[0, 0, plot_length, plot_length],
            z=[z_base, z_base, z_base, z_base],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color="#E0F2FE", opacity=0.7, name=f"Slab {floor.get('floor_name')}"
        ))

        for r in placed_rooms:
            x0, y0 = r["x"], r["y"]
            x1, y1 = x0 + r["width"], y0 + r["length"]
            
            # Draw 3D room wall box wireframes
            wx = [x0, x1, x1, x0, x0, x0, x1, x1, x0, x0, x1, x1, x1, x1, x0, x0]
            wy = [y0, y0, y1, y1, y0, y0, y0, y0, y0, y1, y1, y1, y1, y1, y1, y1]
            wz = [z_base, z_base, z_base, z_base, z_base, z_top, z_top, z_base, z_top, z_top, z_base, z_top, z_top, z_base, z_base, z_top]
            
            fig.add_trace(go.Scatter3d(
                x=wx, y=wy, z=wz,
                mode="lines",
                line=dict(color="#0891B2", width=3),
                name=f"{r['room_type']} ({floor.get('floor_name')})"
            ))
            
            # Add room 3D label centroid
            fig.add_trace(go.Scatter3d(
                x=[(x0+x1)/2], y=[(y0+y1)/2], z=[z_base + 5],
                mode="text",
                text=[f"<b>{r['room_type']}</b>"],
                textfont=dict(color="#0F172A", size=10)
            ))
            
    fig.update_layout(
        title="Interactive 3D House Preview",
        scene=dict(
            xaxis=dict(title="Width (ft)", backgroundcolor="#FFFFFF", gridcolor="#E2E8F0"),
            yaxis=dict(title="Length (ft)", backgroundcolor="#FFFFFF", gridcolor="#E2E8F0"),
            zaxis=dict(title="Height (ft)", backgroundcolor="#FFFFFF", gridcolor="#E2E8F0"),
            aspectmode="data"
        ),
        paper_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=40, b=10),
        height=600,
        showlegend=False
    )
    
    return fig
