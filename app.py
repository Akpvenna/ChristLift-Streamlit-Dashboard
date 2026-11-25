"""
ChristLift: Real-Time Campus Elevator Traffic & Maintenance Monitor

Clean SaaS-inspired multi-page Streamlit application using st.navigation(..., position="sidebar")
and modular architecture across views/ and utils/.
Supports Light, Dark, and System themes natively via the top-right (⋮) Settings menu.
"""

import streamlit as st
from utils.simulator import initialize_session, seed_historical_logs

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="ChristLift | Smart Elevator Monitor",
    page_icon="🛗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Global Theme-Adaptive SaaS CSS Styling
st.markdown(
    """
    <style>
        /* Base typography & clean SaaS look */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        /* Clean top spacing with sidebar navigation */
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }

        /* Interactive, Bold KPI Metric Cards */
        div[data-testid="stMetric"] {
            background-color: var(--secondary-background-color) !important;
            border: 1.5px solid rgba(128, 128, 128, 0.22) !important;
            border-radius: 12px !important;
            padding: 14px 18px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
            transition: transform 0.22s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.22s ease, border-color 0.22s ease !important;
            cursor: pointer !important;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-4px) !important;
            border-color: #4F46E5 !important;
            box-shadow: 0 12px 24px -6px rgba(79, 70, 229, 0.22) !important;
        }

        /* Bold all text inside KPI Metric Cards */
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] p,
        div[data-testid="stMetricLabel"] label {
            font-weight: 700 !important;
            font-size: 0.92rem !important;
            letter-spacing: -0.01em !important;
        }
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] div {
            font-weight: 800 !important;
            letter-spacing: -0.02em !important;
        }
        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] div {
            font-weight: 700 !important;
        }

        /* Generic bordered containers (theme-adaptive) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: var(--secondary-background-color) !important;
            border: 1px solid rgba(128, 128, 128, 0.2) !important;
            border-radius: 10px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        }

        /* Clean buttons */
        button[kind="primary"] {
            background-color: #4F46E5 !important;
            border-color: #4F46E5 !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
        }
        button[kind="secondary"] {
            border-radius: 6px !important;
            font-weight: 600 !important;
        }

        /* Interactive Plotly SVG Hover-Pop Animations across all charts */
        .js-plotly-plot .pielayer .slice {
            transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), filter 0.25s ease !important;
            transform-box: fill-box !important;
            transform-origin: center center !important;
            cursor: pointer !important;
        }
        .js-plotly-plot .pielayer .slice:hover {
            transform: scale(1.08) !important;
            filter: drop-shadow(0 8px 16px rgba(79, 70, 229, 0.35)) brightness(1.06) !important;
        }

        .js-plotly-plot .barlayer .point path,
        .js-plotly-plot .waterfalllayer .point path {
            transition: transform 0.22s cubic-bezier(0.22, 1, 0.36, 1), filter 0.22s ease !important;
            transform-box: fill-box !important;
            transform-origin: center center !important;
            cursor: pointer !important;
        }
        .js-plotly-plot .barlayer .point:hover path,
        .js-plotly-plot .waterfalllayer .point:hover path {
            transform: scale(1.05) !important;
            filter: drop-shadow(0 6px 12px rgba(79, 70, 229, 0.32)) brightness(1.08) !important;
        }

        .js-plotly-plot .scatterlayer .point,
        .js-plotly-plot .polarlayer .point {
            transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1), filter 0.2s ease !important;
            transform-box: fill-box !important;
            transform-origin: center center !important;
            cursor: pointer !important;
        }
        .js-plotly-plot .scatterlayer .point:hover,
        .js-plotly-plot .polarlayer .point:hover {
            transform: scale(1.65) !important;
            filter: drop-shadow(0 3px 8px rgba(79, 70, 229, 0.45)) !important;
        }

        .js-plotly-plot .scatterlayer .trace,
        .js-plotly-plot .polarlayer .trace {
            transition: filter 0.22s ease !important;
        }
        .js-plotly-plot .scatterlayer .trace:hover,
        .js-plotly-plot .polarlayer .trace:hover {
            filter: drop-shadow(0 4px 10px rgba(79, 70, 229, 0.25)) !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Initialize Session & Seed 7-Day Historical Logs (24 Lifts across 6 Blocks)
initialize_session()
seed_historical_logs(days=7)

# 4. Simple, Clean Theme-Adaptive Heading
st.markdown(
    "<h2 style='margin:0 0 10px 0; font-weight:800; letter-spacing:-0.02em; color:var(--text-color);'>🛗 ChristLift</h2>",
    unsafe_allow_html=True
)

# 5. Sidebar Navigation
with st.sidebar:
    st.markdown("### 🛗 ChristLift")
    st.caption("Campus Elevator Monitor • 24 Lifts")

pages = [
    st.Page("views/overview.py", title="Overview", icon="📈", default=True),
    st.Page("views/digital_twin.py", title="Live Digital Twin", icon="🏢"),
    st.Page("views/maintenance.py", title="Maintenance & Logs", icon="🔔"),
]

nav = st.navigation(pages, position="sidebar")
nav.run()
