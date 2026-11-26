"""
ChristLift: Real-Time Campus Elevator Traffic & Maintenance Monitor

Clean SaaS-inspired multi-page Streamlit application using st.navigation(..., position="sidebar")
and modular architecture across views/ and utils/.
Supports Light, Dark, and System themes natively via the top-right (⋮) Settings menu.
"""

import streamlit as st
from utils.simulator import initialize_session, seed_historical_logs, BUILDING_CONFIG

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

        /* Chart Load Entrance Animations (0 -> target value, clockwise pie sweep) */
        @keyframes pieClockwiseReveal {
            0% { transform: rotate(-180deg) scale(0.25); opacity: 0; }
            60% { opacity: 1; }
            100% { transform: rotate(0deg) scale(1); opacity: 1; }
        }
        @keyframes barGrowFromZero {
            0% { transform: scale(0.02); opacity: 0.2; }
            100% { transform: scale(1); opacity: 1; }
        }
        @keyframes sweepLeftToRight {
            0% { clip-path: inset(0 100% 0 0); opacity: 0.35; }
            100% { clip-path: inset(0 0 0 0); opacity: 1; }
        }
        @keyframes radarExpand {
            0% { transform: scale(0.05); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }
        @keyframes fadeScaleIn {
            0% { transform: scale(0.96); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }

        .js-plotly-plot .pielayer {
            transform-box: fill-box;
            transform-origin: center center;
            animation: pieClockwiseReveal 0.9s cubic-bezier(0.22, 1, 0.36, 1);
        }
        .js-plotly-plot .scatterlayer {
            animation: sweepLeftToRight 0.95s cubic-bezier(0.22, 1, 0.36, 1);
        }
        .js-plotly-plot .heatmaplayer {
            transform-origin: center center;
            animation: fadeScaleIn 0.8s ease-out;
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
            transform-box: fill-box;
            transform-origin: left bottom;
            animation: barGrowFromZero 0.85s cubic-bezier(0.22, 1, 0.36, 1);
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

        .js-plotly-plot .polarlayer .trace {
            transform-box: fill-box;
            transform-origin: center center;
            animation: radarExpand 0.9s cubic-bezier(0.22, 1, 0.36, 1);
            transition: filter 0.22s ease !important;
        }
        .js-plotly-plot .scatterlayer .trace {
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

# 5. Sidebar Navigation & Scrollable Campus Fleet Info
with st.sidebar:
    is_live_now = st.session_state.get("live_feed", True)
    st.caption(f"{'🟢 Live Simulation (30s)' if is_live_now else '⏸️ Simulation Paused'} • 24 Lifts")

    fleet_sb = st.session_state.get("fleet", [])
    op_cnt = sum(1 for l in fleet_sb if l.get("Operational_Status") == "Operational")
    alert_cnt = len(fleet_sb) - op_cnt
    avg_campus_load = int(sum(l.get("Passenger_Load_Percent", 0) for l in fleet_sb) / max(1, len(fleet_sb)))

    st.markdown(
        f"""
        <div style="background-color:rgba(128,128,128,0.08); border:1px solid rgba(128,128,128,0.2); border-radius:8px; padding:8px 10px; margin:6px 0 8px 0; font-size:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="opacity:0.8;">Operational</span>
                <b>{op_cnt} / 24</b>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="opacity:0.8;">Avg Load</span>
                <b>{avg_campus_load}%</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if alert_cnt > 0:
        st.warning(f"⚠️ {alert_cnt} lift(s) need attention", icon="🔔")
    else:
        st.success("All 24 lifts running normally", icon="✅")

    st.markdown("**Campus Building Directory**")
    with st.container(height=230, border=True):
        for blk, cfg in BUILDING_CONFIG.items():
            blk_lifts = [l for l in fleet_sb if l.get("Block") == blk]
            blk_load = int(sum(l.get("Passenger_Load_Percent", 0) for l in blk_lifts) / max(1, len(blk_lifts)))
            min_lbl = "B1" if cfg.get("min_floor", 0) == -1 else "G"
            st.markdown(
                f"<div style='font-size:12px; margin-bottom:6px;'>"
                f"<b>{blk}</b><br>"
                f"<span style='opacity:0.75; font-size:11px;'>{cfg['lifts']} Lifts • {min_lbl}–{cfg['max_floor']}F • Load {blk_load}%</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    with st.expander("Peak Hours & Legend", expanded=False):
        st.markdown(
            """
            - **Morning:** `08:30 – 09:30`
            - **Lunch:** `12:30 – 14:00`
            - **Evening:** `16:00 – 17:30`
            - 🟢 `< 60%` Normal
            - 🔵 `60 – 84%` Moderate
            - 🔴 `≥ 85%` High Load / Alert
            """
        )

pages = [
    st.Page("views/overview.py", title="Overview", icon="📈", default=True),
    st.Page("views/digital_twin.py", title="Live Digital Twin", icon="🏢"),
    st.Page("views/maintenance.py", title="Maintenance & Logs", icon="🔔"),
]

nav = st.navigation(pages, position="sidebar")
nav.run()
