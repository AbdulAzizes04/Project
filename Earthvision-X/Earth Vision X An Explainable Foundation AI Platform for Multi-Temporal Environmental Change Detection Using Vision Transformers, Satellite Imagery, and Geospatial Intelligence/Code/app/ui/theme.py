"""
Custom Enterprise Scientific CSS Styling for EARTH VISION-X Dashboard.
Color Palette:
- Background: Deep Space Navy (#080E1A, #0B132B)
- Surface Cards: Translucent Frosted Glass (#0F1B33, rgba(15, 27, 51, 0.75))
- Borders: Subtle Cyan / Cobalt Glow (rgba(56, 189, 248, 0.25))
- Primary Accent: Scientific Cyan (#38BDF8)
- Secondary Accent: Environmental Emerald (#10B981)
- Danger / Change: Crimson Amber (#EF4444, #F59E0B)
"""

import streamlit as st

def inject_custom_css():
    """Injects high-end enterprise CSS into Streamlit DOM."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Global Theme Override */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #F1F5F9;
        }

        .stApp {
            background: radial-gradient(circle at 50% 0%, #0F1D38 0%, #080E1A 60%, #040810 100%) !important;
            background-attachment: fixed !important;
        }

        /* Glassmorphic Container Cards */
        .evx-card {
            background: rgba(15, 27, 51, 0.75);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .evx-card:hover {
            border-color: rgba(56, 189, 248, 0.45);
            box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.15);
        }

        /* Metric Cards */
        .metric-tile {
            background: linear-gradient(135deg, rgba(17, 34, 64, 0.8) 0%, rgba(10, 20, 40, 0.8) 100%);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 10px;
            padding: 14px 18px;
            text-align: left;
            position: relative;
            overflow: hidden;
        }

        .metric-tile::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
            background: #38BDF8;
        }

        .metric-tile.emerald::before { background: #10B981; }
        .metric-tile.crimson::before { background: #EF4444; }
        .metric-tile.amber::before { background: #F59E0B; }

        .metric-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }

        .metric-val {
            font-size: 1.6rem;
            font-weight: 700;
            color: #F8FAFC;
            font-family: 'JetBrains Mono', monospace;
            line-height: 1.2;
        }

        .metric-sub {
            font-size: 0.72rem;
            color: #38BDF8;
            margin-top: 4px;
        }

        /* Header Bar */
        .evx-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(13, 25, 48, 0.9);
            border-bottom: 1px solid rgba(56, 189, 248, 0.2);
            padding: 14px 24px;
            border-radius: 12px;
            margin-bottom: 20px;
        }

        .evx-header-title {
            font-size: 1.35rem;
            font-weight: 800;
            color: #F8FAFC;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: -0.02em;
        }

        .evx-header-badge {
            background: rgba(56, 189, 248, 0.15);
            color: #38BDF8;
            border: 1px solid rgba(56, 189, 248, 0.4);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }

        /* Pulse Status Badge */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 9999px;
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 8px #10B981;
        }

        /* AI Insight Narrative Box */
        .ai-story-box {
            background: linear-gradient(135deg, rgba(24, 38, 70, 0.7) 0%, rgba(13, 23, 46, 0.8) 100%);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-left: 5px solid #38BDF8;
            border-radius: 10px;
            padding: 16px 20px;
            font-size: 0.88rem;
            line-height: 1.6;
            color: #E2E8F0;
            margin: 14px 0;
        }

        /* Satellite Image Card */
        .sat-frame {
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 10px;
            overflow: hidden;
            background: #0B1326;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }

        .sat-frame-header {
            background: #0F1D38;
            padding: 8px 12px;
            border-bottom: 1px solid rgba(56, 189, 248, 0.2);
            font-size: 0.8rem;
            font-weight: 700;
            color: #38BDF8;
            display: flex;
            justify-content: space-between;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #080E1A;
        }
        ::-webkit-scrollbar-thumb {
            background: #1E3A8A;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #38BDF8;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
