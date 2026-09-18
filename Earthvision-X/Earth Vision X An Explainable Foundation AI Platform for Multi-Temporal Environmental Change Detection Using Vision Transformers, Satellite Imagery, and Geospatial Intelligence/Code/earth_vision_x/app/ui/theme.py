"""
Streamlit Enterprise Visual Styling and CSS Injector for EARTH VISION-X.
Theme: Deep Space Blue (#08111F), Glassmorphic Slate (#0F172A), Electric Blue (#3B82F6), Cyan (#06B6D4).
"""

import streamlit as st

def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* 1. Hide Default Chrome while forcing Sidebar to stay open */
        #MainMenu { visibility: hidden; display: none !important; }
        footer { visibility: hidden; display: none !important; }
        header[data-testid="stHeader"] { visibility: hidden; display: none !important; height: 0 !important; }
        .stDeployButton { display: none !important; }
        div[data-testid="stToolbar"] { display: none !important; }
        div[data-testid="stDecoration"] { display: none !important; }
        div[data-testid="stStatusWidget"] { display: none !important; }

        /* 2. Global Root & Layout Settings */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #08111F !important;
            color: #E2E8F0 !important;
        }

        .stApp {
            background-color: #08111F !important;
        }

        [data-testid="stAppViewContainer"] {
            background-color: #08111F !important;
            display: flex !important;
            flex-direction: row !important;
        }

        /* 3. Enterprise Left Sidebar (~280px) FORCED PERMANENTLY OPEN */
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"][aria-expanded="false"],
        section[data-testid="stSidebar"][aria-expanded="true"] {
            display: flex !important;
            visibility: visible !important;
            transform: none !important;
            margin-left: 0 !important;
            left: 0 !important;
            min-width: 280px !important;
            width: 280px !important;
            max-width: 280px !important;
            position: relative !important;
            z-index: 100 !important;
            background-color: #0B1626 !important;
            border-right: 1px solid rgba(59, 130, 246, 0.2) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
        }

        /* Main Viewport Container */
        [data-testid="stAppViewContainer"] > section.main {
            flex: 1 !important;
            width: calc(100% - 280px) !important;
        }

        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 99% !important;
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Sidebar Logo Header */
        .sidebar-brand-container {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.5) 0%, rgba(15, 23, 42, 0.95) 100%);
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 12px;
            margin-bottom: 16px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }
        .sidebar-brand-icon {
            font-size: 2.2rem;
            filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.6));
            animation: pulse-glow 3s infinite alternate;
        }
        @keyframes pulse-glow {
            0% { filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.4)); }
            100% { filter: drop-shadow(0 0 14px rgba(56, 189, 248, 0.8)); }
        }
        .sidebar-brand-title {
            font-size: 1.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #38BDF8, #60A5FA, #93C5FD);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.06em;
            margin: 0;
        }
        .sidebar-brand-sub {
            font-size: 0.72rem;
            color: #94A3B8;
            margin: 2px 0 0 0;
            font-weight: 500;
            letter-spacing: 0.02em;
        }

        /* Sidebar Navigation Radio Group Custom UI/UX */
        section[data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 6px !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            background: rgba(15, 23, 42, 0.65) !important;
            border: 1px solid rgba(59, 130, 246, 0.18) !important;
            border-radius: 9px !important;
            padding: 10px 14px !important;
            margin-bottom: 4px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(30, 58, 138, 0.4) !important;
            border-color: rgba(56, 189, 248, 0.5) !important;
            transform: translateX(4px) !important;
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.15) !important;
        }
        /* Hide Default Radio Circle Dot */
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }
        /* Active / Checked Navigation Item Styling */
        section[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"],
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.35) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
            border: 1px solid rgba(56, 189, 248, 0.65) !important;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.25), inset 3px 0 0 #38BDF8 !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            color: #CBD5E1 !important;
            letter-spacing: 0.01em !important;
            margin: 0 !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] div[data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p {
            color: #38BDF8 !important;
            font-weight: 700 !important;
            text-shadow: 0 0 8px rgba(56, 189, 248, 0.4);
        }

        /* Sidebar Section Header Labels */
        .nav-section-header {
            font-size: 0.68rem;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 16px 4px 6px 4px;
        }

        /* Sidebar Selectbox Customization */
        section[data-testid="stSidebar"] div[data-baseweb="select"] {
            background: rgba(15, 23, 42, 0.85) !important;
            border: 1px solid rgba(56, 189, 248, 0.35) !important;
            border-radius: 8px !important;
        }

        /* Sidebar System Monitor Card */
        .system-monitor-card {
            background: rgba(11, 22, 38, 0.95);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 12px;
            padding: 14px;
            margin-top: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        .system-monitor-title {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #38BDF8;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .pulse-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 0.68rem;
            color: #34D399;
            font-weight: 700;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 2px 8px;
            border-radius: 12px;
        }
        .pulse-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #10B981;
            box-shadow: 0 0 8px #10B981;
            animation: pulse-ring 2s infinite;
        }
        @keyframes pulse-ring {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        .metric-progress-bar {
            background: #1E293B;
            border-radius: 6px;
            height: 6px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .metric-progress-fill-gpu {
            background: linear-gradient(90deg, #3B82F6, #06B6D4);
            height: 100%;
        }
        .metric-progress-fill-cpu {
            background: linear-gradient(90deg, #10B981, #34D399);
            height: 100%;
        }
        .metric-progress-fill-ram {
            background: linear-gradient(90deg, #F59E0B, #FBBF24);
            height: 100%;
        }
        .system-label {
            font-size: 0.75rem;
            color: #94A3B8;
            display: flex;
            justify-content: space-between;
            margin-bottom: 3px;
        }

        /* 4. Top Enterprise Header Bar */
        .top-header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(59, 130, 246, 0.25);
            border-radius: 12px;
            padding: 14px 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }
        .header-logo-group {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .header-title-text {
            font-size: 1.35rem;
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: -0.01em;
            margin: 0;
        }
        .model-badge {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(6, 182, 212, 0.25) 100%);
            border: 1px solid rgba(59, 130, 246, 0.5);
            color: #60A5FA;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .confidence-badge {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #34D399;
            font-size: 0.82rem;
            font-weight: 700;
            padding: 6px 14px;
            border-radius: 20px;
        }
        .header-right-group {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .user-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3B82F6, #8B5CF6);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.85rem;
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.2);
        }

        /* 5. Enterprise Card Containers */
        .glass-card {
            background: rgba(15, 23, 42, 0.85) !important;
            backdrop-filter: blur(16px);
            border: 1px solid rgba(59, 130, 246, 0.2) !important;
            border-radius: 12px !important;
            padding: 18px 22px !important;
            margin-bottom: 16px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .glass-card:hover {
            border-color: rgba(59, 130, 246, 0.45) !important;
        }

        /* Card Section Header */
        .card-header-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* 6. KPI Metric Cards */
        .kpi-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
            border: 1px solid rgba(59, 130, 246, 0.25);
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
            text-align: center;
        }
        .kpi-title {
            font-size: 0.78rem;
            font-weight: 600;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .kpi-value {
            font-size: 1.65rem;
            font-weight: 800;
            color: #38BDF8;
            margin-top: 4px;
            font-family: 'JetBrains Mono', monospace;
        }
        .kpi-sub {
            font-size: 0.72rem;
            color: #34D399;
            font-weight: 600;
            margin-top: 2px;
        }

        /* 7. Image Meta Overlay Card */
        .img-meta-tag {
            background: rgba(30, 58, 138, 0.4);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 0.75rem;
            color: #93C5FD;
            font-family: 'JetBrains Mono', monospace;
            display: inline-block;
            margin-right: 6px;
            margin-bottom: 6px;
        }

        /* 8. AI Natural Language Insight Box */
        .insight-card {
            background: rgba(15, 23, 42, 0.95) !important;
            border-left: 4px solid #3B82F6 !important;
            border-top: 1px solid rgba(59, 130, 246, 0.2) !important;
            border-right: 1px solid rgba(59, 130, 246, 0.2) !important;
            border-bottom: 1px solid rgba(59, 130, 246, 0.2) !important;
            padding: 16px 20px !important;
            border-radius: 8px !important;
            margin: 14px 0 !important;
            font-size: 0.9rem !important;
            line-height: 1.6 !important;
            color: #E2E8F0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        .insight-card p, .insight-card span, .insight-card div, .insight-card strong {
            color: #E2E8F0 !important;
        }

        /* Custom Legend Badges */
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8rem;
            color: #CBD5E1;
            margin-bottom: 6px;
        }
        .legend-color-box {
            width: 14px;
            height: 14px;
            border-radius: 3px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

