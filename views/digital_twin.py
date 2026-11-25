"""
ChristLift - Page 2: Live Digital Twin (Real-Time Shaft & Telemetry Monitor)
Updates smoothly every 10 seconds when Live Tick is enabled; stops completely when paused.
Features:
- Visual Elevator Shafts (0 to Building Max Floor) with moving cars and hover popups
- Auto-appending live telemetry feed table
- Multi-line live traffic load trend (smooth splines + hover popups)
- Busy hour capacity analysis
- Lift Performance Radar
"""

import os
import io
from collections import deque
import pandas as pd
import streamlit as st

from utils.charts import (
    build_elevator_shafts_chart,
    build_live_traffic_line_chart,
    build_busy_hour_chart,
    build_lift_performance_radar
)
from utils.simulator import CSV_FILE, BLOCKS, simulate_tick, initialize_session, get_max_floor

WIDTH_STRETCH = {"width": "stretch"}
CHART_CONFIG = {"displayModeBar": "hover", "displaylogo": False}


def get_recent_logs(n=240):
    """Efficiently loads only the last n telemetry rows from lift_logs.csv."""
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 100:
        try:
            with open(CSV_FILE, "r", encoding="utf-8", errors="replace") as f:
                header = f.readline()
                if not header:
                    return pd.DataFrame()
                tail_lines = list(deque(f, maxlen=n))
            if not tail_lines:
                return pd.DataFrame()
            df = pd.read_csv(io.StringIO(header + "".join(tail_lines)))
            if not df.empty and "Timestamp" in df.columns:
                df["Passenger_Load_Percent"] = pd.to_numeric(df["Passenger_Load_Percent"], errors="coerce").fillna(0)
                df["Current_Floor"] = pd.to_numeric(df["Current_Floor"], errors="coerce").fillna(0).astype(int)
                df["Est_Wait_Sec"] = pd.to_numeric(df["Est_Wait_Sec"], errors="coerce").fillna(30).astype(int)
                return df
        except Exception:
            pass
    return pd.DataFrame()


def _render_twin_body(selected_block):
    """Renders the Digital Twin layout without forcing a background timer."""
    fleet = st.session_state.get("fleet", [])
    block_fleet = [l for l in fleet if l.get("Block") == selected_block]
    if not block_fleet:
        block_fleet = [l for l in fleet if l.get("Block") == "Central Block"]
    block_fleet_df = pd.DataFrame(block_fleet)

    recent_df = get_recent_logs(240)
    max_floor = get_max_floor(selected_block)
    n_lifts = len(block_fleet_df)

    col_left, col_right = st.columns([1.15, 1.05])

    # ------------------------------------------
    # LEFT COLUMN: SHAFTS + TELEMETRY TABLE
    # ------------------------------------------
    with col_left:
        with st.container(border=True):
            sh_h1, sh_h2 = st.columns([3.0, 1.0], vertical_alignment="center")
            with sh_h1:
                st.markdown(
                    f"""
                    <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                        Shaft Height Live Location Tracking
                    </div>
                    <div style="font-size:11px; color:var(--text-color); opacity:0.7; margin-bottom:4px;">
                        Real-time vertical position (Ground&ndash;{max_floor}th Floor) &bull; {selected_block} ({n_lifts} Lifts)
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with sh_h2:
                with st.popover("🔍 Details", **WIDTH_STRETCH):
                    st.markdown(f"**{selected_block} Live Snapshot**")
                    st.dataframe(
                        block_fleet_df[["Lift_ID", "Current_Floor", "Direction", "Passenger_Load_Percent", "Est_Wait_Sec", "Operational_Status"]],
                        hide_index=True,
                        **WIDTH_STRETCH
                    )

            fig_shafts = build_elevator_shafts_chart(block_fleet_df, max_floor=max_floor)
            st.plotly_chart(fig_shafts, **WIDTH_STRETCH, config=CHART_CONFIG)

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                    Live Telemetry Feed (CSV Appended)
                </div>
                <div style="font-size:11px; color:var(--text-color); opacity:0.7; margin-bottom:6px;">
                    Updates every 10 seconds when Live Tick is active &bull; saved to lift_logs.csv
                </div>
                """,
                unsafe_allow_html=True
            )

            feed_df = recent_df[recent_df["Block"] == selected_block] if not recent_df.empty else pd.DataFrame()
            if feed_df.empty and not recent_df.empty:
                feed_df = recent_df

            if not feed_df.empty:
                display_feed = feed_df[["Timestamp", "Lift_ID", "Current_Floor", "Direction", "Passenger_Load_Percent", "Operational_Status"]].tail(12).iloc[::-1].copy()
                display_feed["Direction"] = display_feed["Direction"].apply(lambda d: f"▲ {d}" if "Up" in str(d) else (f"▼ {d}" if "Down" in str(d) else f"● {d}"))
                display_feed["Passenger_Load_Percent"] = display_feed["Passenger_Load_Percent"].apply(lambda l: f"{int(l)}%")

                st.dataframe(
                    display_feed,
                    column_config={
                        "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
                        "Lift_ID": st.column_config.TextColumn("Lift ID", width="small"),
                        "Current_Floor": st.column_config.TextColumn("Floor", width="small"),
                        "Direction": st.column_config.TextColumn("Direction", width="small"),
                        "Passenger_Load_Percent": st.column_config.TextColumn("Load %", width="small"),
                        "Operational_Status": st.column_config.TextColumn("Status", width="medium")
                    },
                    hide_index=True,
                    height=200,
                    **WIDTH_STRETCH
                )
            else:
                st.info("Awaiting telemetry stream...")

    # ------------------------------------------
    # RIGHT COLUMN: TRENDS + BUSY HOUR + RADAR
    # ------------------------------------------
    with col_right:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                    Live Traffic Load % Over Time
                </div>
                <div style="font-size:11px; color:var(--text-color); opacity:0.7;">
                    Smooth rolling capacity load fluctuation for {selected_block} elevators
                </div>
                """,
                unsafe_allow_html=True
            )
            fig_line = build_live_traffic_line_chart(recent_df, selected_block)
            st.plotly_chart(fig_line, **WIDTH_STRETCH, config=CHART_CONFIG)

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        r_sub1, r_sub2 = st.columns([1.0, 1.1])

        with r_sub1:
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="font-size:13px; font-weight:600; color:var(--text-color);">
                        Busy Hour Analysis
                    </div>
                    <div style="font-size:10px; color:var(--text-color); opacity:0.7;">
                        Peak capacity (08:00–20:00)
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                fig_busy = build_busy_hour_chart(recent_df, selected_block)
                st.plotly_chart(fig_busy, **WIDTH_STRETCH, config=CHART_CONFIG)

        with r_sub2:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="font-size:13px; font-weight:600; color:var(--text-color);">
                        Lift Performance Radar
                    </div>
                    <div style="font-size:10px; color:var(--text-color); opacity:0.7;">
                        Health, Load, Speed &amp; Coverage &bull; {selected_block}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                fig_radar = build_lift_performance_radar(block_fleet_df, selected_block)
                st.plotly_chart(fig_radar, **WIDTH_STRETCH, config=CHART_CONFIG)


@st.fragment(run_every=10)
def render_live_twin_fragment(selected_block):
    """Auto-refreshing 10-second fragment, only invoked when Live Tick is enabled."""
    if st.session_state.get("live_feed", True):
        simulate_tick()
    _render_twin_body(selected_block)


def _sync_twin_live():
    val = st.session_state["twin_live_toggle"]
    st.session_state["live_feed"] = val
    st.session_state["overview_live_toggle"] = val


def render_digital_twin():
    initialize_session()

    if "twin_block_filter" not in st.session_state or st.session_state["twin_block_filter"] not in BLOCKS:
        st.session_state["twin_block_filter"] = BLOCKS[0]
    if "twin_live_toggle" not in st.session_state:
        st.session_state["twin_live_toggle"] = st.session_state.get("live_feed", True)

    top_c1, top_c2 = st.columns([1.8, 2.2], vertical_alignment="center")

    with top_c1:
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:22px;">🏢</span>
                <span style="font-size:20px; font-weight:700; color:var(--text-color); letter-spacing:-0.02em;">Live Digital Twin</span>
            </div>
            <div style="font-size:12px; color:var(--text-color); opacity:0.7; margin-top:-2px;">
                Real-time elevator shaft kinematics, performance radar, and 10s telemetry stream
            </div>
            """,
            unsafe_allow_html=True
        )

    with top_c2:
        ctrl1, ctrl2, ctrl3 = st.columns([1.6, 1.3, 0.9], vertical_alignment="center")

        with ctrl1:
            selected_block = st.selectbox(
                "Campus Block",
                options=BLOCKS,
                key="twin_block_filter",
                label_visibility="collapsed"
            )

        with ctrl2:
            live_status = st.toggle(
                "🟢 Live Tick (10s)",
                key="twin_live_toggle",
                on_change=_sync_twin_live,
                help="Toggle 10-second auto-refresh simulation"
            )

        with ctrl3:
            if st.button("Step Tick ⏩", help="Manually step simulation tick", **WIDTH_STRETCH):
                prev = st.session_state.get("live_feed", True)
                st.session_state["live_feed"] = True
                simulate_tick()
                st.session_state["live_feed"] = prev
                st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Only run the 10-second auto-refresh fragment when Live Tick is ON;
    # when OFF, render statically so the page stops completely without blinking.
    if st.session_state.get("live_feed", True):
        render_live_twin_fragment(selected_block)
    else:
        _render_twin_body(selected_block)


render_digital_twin()
