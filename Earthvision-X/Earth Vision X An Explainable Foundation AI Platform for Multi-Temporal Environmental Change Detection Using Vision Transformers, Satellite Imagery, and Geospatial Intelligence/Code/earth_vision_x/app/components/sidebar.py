"""
Enterprise Sidebar Navigation Component for EARTH VISION-X Dashboard.
"""

import streamlit as st

def render_html(html_str: str):
    """Clean HTML string renderer eliminating markdown code block escaping."""
    clean_lines = [line.strip() for line in html_str.strip().split("\n")]
    st.markdown("".join(clean_lines), unsafe_allow_html=True)

def render_sidebar() -> str:
    """Renders enterprise Palantir/Azure AI Studio style sidebar navigation menu."""
    with st.sidebar:
        # Brand Header
        render_html(
            """
            <div class="sidebar-brand-container">
                <span class="sidebar-brand-icon">🌍</span>
                <div>
                    <h3 class="sidebar-brand-title">EARTH VISION-X</h3>
                    <p class="sidebar-brand-sub">Foundation AI & Geospatial Platform</p>
                </div>
            </div>
            <div class="nav-section-header">NAVIGATION MENU</div>
            """
        )

        options = [
            "📊 Executive Overview",
            "🛰️ Satellite Acquisition & Studio",
            "🗺️ GIS Maps & Heatmaps",
            "🌐 Select EO Domain Workstation...",
            "ℹ️ About Platform & Specs"
        ]

        selected = st.radio("Primary Navigation", options, index=0, label_visibility="collapsed")

        selected_domain = "change_detection"
        if selected == "🌐 Select EO Domain Workstation...":
            render_html("<div class='nav-section-header'>ANALYSIS DOMAINS</div>")
            domain_options = {
                "🌤️ Weather Forecasting": "weather",
                "🌡️ Climate Monitoring": "climate",
                "🌊 Flood Monitoring": "flood",
                "🔥 Wildfire Detection": "wildfire",
                "🏚️ Earthquake Damage": "earthquake",
                "⛰️ Landslide Detection": "landslide",
                "🌲 Forest Analysis": "forest",
                "🌾 Agriculture": "agriculture",
                "💧 Water Resource Management": "water",
                "🏙️ Urban Intelligence": "urban",
                "🌫️ Air Quality": "air_quality",
                "🏖️ Coastal Monitoring": "coastal",
                "⛏️ Mining Detection": "mining",
                "🐾 Biodiversity": "biodiversity",
                "🔄 Change Detection": "change_detection"
            }
            sel_dom_name = st.selectbox("Earth Observation Domain", list(domain_options.keys()), index=0)
            selected_domain = domain_options[sel_dom_name]

        # Bottom System Monitor Section
        render_html(
            """
            <div class="system-monitor-card">
                <div class="system-monitor-title">
                    <span>🖥️ System Telemetry</span>
                    <span class="pulse-badge"><span class="pulse-dot"></span>ONLINE</span>
                </div>
                
                <div class="system-label">
                    <span>GPU (NVIDIA RTX 4090)</span>
                    <span style="color: #38BDF8; font-weight: 700;">42%</span>
                </div>
                <div class="metric-progress-bar">
                    <div class="metric-progress-fill-gpu" style="width: 42%;"></div>
                </div>

                <div class="system-label">
                    <span>CPU Load (32 Cores)</span>
                    <span style="color: #34D399; font-weight: 700;">18%</span>
                </div>
                <div class="metric-progress-bar">
                    <div class="metric-progress-fill-cpu" style="width: 18%;"></div>
                </div>

                <div class="system-label">
                    <span>VRAM / RAM</span>
                    <span style="color: #FBBF24; font-weight: 700;">12.4 GB / 32 GB</span>
                </div>
                <div class="metric-progress-bar">
                    <div class="metric-progress-fill-ram" style="width: 38.7%;"></div>
                </div>

                <div style="font-size: 0.68rem; color: #64748B; margin-top: 10px; text-align: center; font-family: 'JetBrains Mono', monospace;">
                    v1.0.0-IEEE | PyTorch 2.3 + TensorRT
                </div>
            </div>
            """
        )

        route_map = {
            "📊 Executive Overview": ("dashboard", "dashboard"),
            "🛰️ Satellite Acquisition & Studio": ("upload", "upload"),
            "🗺️ GIS Maps & Heatmaps": ("heatmap", "heatmap"),
            "🌐 Select EO Domain Workstation...": ("domain", selected_domain),
            "ℹ️ About Platform & Specs": ("about", "about")
        }
        return route_map.get(selected, ("dashboard", "dashboard"))




