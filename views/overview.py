"""
ChristLift - Page 1: Overview (Executive Campus Analytics)
Nimbus BI-inspired clean SaaS interface with top control bar, KPI sparklines,
stacked area volume, waterfall capacity bridge, weekday x hour heatmap,
floor zone donut, and rich fleet performance table.
"""

import os
import pandas as pd
import streamlit as st

from utils.charts import (
    build_stacked_area_chart,
    build_waterfall_bridge_chart,
    build_weekday_hour_heatmap,
    build_floor_zone_donut
)
from utils.simulator import CSV_FILE, BLOCKS, initialize_session

WIDTH_STRETCH = {"width": "stretch"}
CHART_CONFIG = {"displayModeBar": "hover", "displaylogo": False}


@st.cache_data(ttl=10)
def load_data():
    """Loads and caches elevator telemetry logs for 10 seconds."""
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 100:
        try:
            df = pd.read_csv(CSV_FILE)
            if "Timestamp" in df.columns:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="mixed", errors="coerce")
                df = df.dropna(subset=["Timestamp"])
                df["Passenger_Load_Percent"] = pd.to_numeric(df["Passenger_Load_Percent"], errors="coerce").fillna(0)
                df["Est_Wait_Sec"] = pd.to_numeric(df["Est_Wait_Sec"], errors="coerce").fillna(30)
                df["Energy_kWh"] = pd.to_numeric(df["Energy_kWh"], errors="coerce").fillna(0.15)
                df["Health_Score"] = pd.to_numeric(df["Health_Score"], errors="coerce").fillna(95)
                return df
        except Exception:
            pass
    return pd.DataFrame()


def _sync_overview_live():
    val = st.session_state["overview_live_toggle"]
    st.session_state["live_feed"] = val
    st.session_state["twin_live_toggle"] = val


def render_overview():
    initialize_session()
    df = load_data()

    block_opts = ["All Blocks"] + BLOCKS
    if "overview_block_filter" not in st.session_state or st.session_state["overview_block_filter"] not in block_opts:
        st.session_state["overview_block_filter"] = "All Blocks"
    if "overview_time_window" not in st.session_state:
        st.session_state["overview_time_window"] = "24H"
    if "overview_live_toggle" not in st.session_state:
        st.session_state["overview_live_toggle"] = st.session_state.get("live_feed", True)

    # ==========================================
    # 1. TOP HEADER & CONTROL BAR
    # ==========================================
    top_c1, top_c2 = st.columns([1.8, 2.2], vertical_alignment="center")

    with top_c1:
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:22px;">📈</span>
                <span style="font-size:20px; font-weight:700; color:var(--text-color); letter-spacing:-0.02em;">Overview</span>
            </div>
            <div style="font-size:12px; color:var(--text-color); opacity:0.7; margin-top:-2px;">
                All campus blocks &bull; real-time elevator traffic &amp; fleet capacity analytics
            </div>
            """,
            unsafe_allow_html=True
        )

    with top_c2:
        ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.3, 1.4, 0.9, 1.0], vertical_alignment="center")

        with ctrl1:
            # Time Window Selector (1-click key binding)
            try:
                time_window = st.segmented_control(
                    "Time Window",
                    options=["1H", "6H", "24H", "7D"],
                    key="overview_time_window",
                    label_visibility="collapsed"
                )
            except AttributeError:
                time_window = st.radio(
                    "Time Window",
                    options=["1H", "6H", "24H", "7D"],
                    key="overview_time_window",
                    horizontal=True,
                    label_visibility="collapsed"
                )
            active_window = time_window or "24H"

        with ctrl2:
            # Block Filter (1-click key binding — no index override!)
            selected_block = st.selectbox(
                "Filter Block",
                options=block_opts,
                key="overview_block_filter",
                label_visibility="collapsed"
            )

        with ctrl3:
            # Live Feed Badge / Toggle
            st.toggle("Live", key="overview_live_toggle", on_change=_sync_overview_live, help="Simulation tick loop")

        with ctrl4:
            # CSV Download
            if not df.empty:
                csv_bytes = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Export CSV",
                    data=csv_bytes,
                    file_name="christlift_logs.csv",
                    mime="text/csv",
                    **WIDTH_STRETCH
                )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Filter data based on selection
    filtered_df = df.copy() if not df.empty else pd.DataFrame()
    if not filtered_df.empty:
        max_time = filtered_df["Timestamp"].max()
        if active_window == "1H":
            cutoff = max_time - pd.Timedelta(hours=1)
        elif active_window == "6H":
            cutoff = max_time - pd.Timedelta(hours=6)
        elif active_window == "24H":
            cutoff = max_time - pd.Timedelta(hours=24)
        else:
            cutoff = max_time - pd.Timedelta(days=7)

        filtered_df = filtered_df[filtered_df["Timestamp"] >= cutoff]

        if selected_block != "All Blocks":
            filtered_df = filtered_df[filtered_df["Block"] == selected_block]

    # Calculate real or baseline KPI values
    fleet_state = st.session_state.get("fleet", [])
    relevant_fleet = [l for l in fleet_state if selected_block == "All Blocks" or l.get("Block") == selected_block]
    active_count = sum(1 for l in relevant_fleet if l.get("Operational_Status") == "Operational")
    total_relevant = max(1, len(relevant_fleet))
    active_ratio = f"{active_count} / {total_relevant}"

    if not filtered_df.empty:
        avg_load = int(filtered_df["Passenger_Load_Percent"].mean())
        avg_wait_sec = filtered_df["Est_Wait_Sec"].mean()
        avg_wait_min = round(avg_wait_sec / 60, 1)
        total_energy = round(filtered_df["Energy_kWh"].sum(), 1)

        # Build real sparkline trends bucketed by Timestamp
        ts_agg = (
            filtered_df.sort_values("Timestamp")
            .groupby("Timestamp")
            .agg(
                load=("Passenger_Load_Percent", "mean"),
                wait=("Est_Wait_Sec", "mean"),
                energy=("Energy_kWh", "sum"),
                op=("Operational_Status", lambda s: int((s == "Operational").sum())),
            )
            .tail(12)
        )
        active_series = [int(v) for v in ts_agg["op"].tolist()] or [active_count]
        load_series = [int(round(v)) for v in ts_agg["load"].tolist()] or [avg_load]
        wait_series = [round(v / 60, 2) for v in ts_agg["wait"].tolist()] or [avg_wait_min]
        energy_series = [round(v, 2) for v in ts_agg["energy"].tolist()] or [total_energy]

        load_delta = f"{load_series[-1] - load_series[0]:+d}% over window" if len(load_series) >= 2 else "Window average"
        wait_delta = f"{round(wait_series[-1] - wait_series[0], 1):+.1f} mins over window" if len(wait_series) >= 2 else "Window average"
    else:
        avg_load = 68
        avg_wait_min = 1.8
        total_energy = 12.4
        active_series = [active_count] * 6
        load_series = [avg_load] * 6
        wait_series = [avg_wait_min] * 6
        energy_series = [total_energy] * 6
        load_delta = "Window average"
        wait_delta = "Window average"

    # ==========================================
    # 2. ROW 1: 4 INTERACTIVE KPI METRIC CARDS
    # ==========================================
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        st.metric(
            label="Active Elevators",
            value=active_ratio,
            delta="100% Operational" if active_count == total_relevant else f"{total_relevant - active_count} Inactive",
            chart_data=active_series,
            chart_type="area",
            help="Total elevators currently operational across selected campus blocks.",
            border=True
        )
        with st.popover("🔍 Inspect Fleet Status", **WIDTH_STRETCH):
            st.markdown("**Operational Status by Block**")
            for b in BLOCKS:
                b_lifts = [l for l in fleet_state if l.get("Block") == b]
                b_ok = sum(1 for l in b_lifts if l.get("Operational_Status") == "Operational")
                st.write(f"- **{b}:** {b_ok} / {len(b_lifts)} Operational")

    with kpi_col2:
        st.metric(
            label="Avg Traffic Load",
            value=f"{avg_load}%",
            delta=load_delta,
            delta_color="normal",
            chart_data=load_series,
            chart_type="bar",
            help="Average passenger capacity utilization across the selected time window.",
            border=True
        )
        with st.popover("🔍 Inspect Load by Block", **WIDTH_STRETCH):
            st.markdown("**Live Load % by Block**")
            for b in BLOCKS:
                b_lifts = [l for l in fleet_state if l.get("Block") == b]
                b_avg = int(sum(l.get("Passenger_Load_Percent", 0) for l in b_lifts) / max(1, len(b_lifts)))
                st.progress(b_avg / 100, text=f"**{b}:** {b_avg}%")

    with kpi_col3:
        st.metric(
            label="Avg Waiting Time",
            value=f"{avg_wait_min} mins",
            delta=wait_delta,
            delta_color="inverse",
            chart_data=wait_series,
            chart_type="line",
            help="Estimated average waiting time for elevator dispatch.",
            border=True
        )
        with st.popover("🔍 Inspect Wait Times", **WIDTH_STRETCH):
            st.markdown("**Estimated Wait Time by Block**")
            for b in BLOCKS:
                b_lifts = [l for l in fleet_state if l.get("Block") == b]
                b_wait = round(sum(l.get("Est_Wait_Sec", 30) for l in b_lifts) / max(1, len(b_lifts)) / 60, 2)
                st.write(f"- **{b}:** {b_wait} mins avg")

    with kpi_col4:
        st.metric(
            label="Simulated Fleet Energy",
            value=f"{total_energy} kWh",
            delta=f"{active_window} Total Draw",
            delta_color="off",
            chart_data=energy_series,
            chart_type="bar",
            help="Cumulative simulated electrical draw across active traction motors in the selected window.",
            border=True
        )
        with st.popover("🔍 Inspect Energy Draw", **WIDTH_STRETCH):
            st.markdown("**Instantaneous Draw by Block**")
            for b in BLOCKS:
                b_lifts = [l for l in fleet_state if l.get("Block") == b]
                b_kwh = round(sum(l.get("Energy_kWh", 0.15) for l in b_lifts), 2)
                st.write(f"- **{b}:** {b_kwh} kWh / tick")

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 3. ROW 2: 2-COLUMN ANALYTICAL CHARTS
    # ==========================================
    row2_col1, row2_col2 = st.columns([1.3, 1.0])

    with row2_col1:
        with st.container(border=True):
            r2_head1, r2_head2 = st.columns([2.5, 1.0], vertical_alignment="center")
            with r2_head1:
                st.markdown(
                    """
                    <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                        Elevator Traffic Volume by Campus Block
                    </div>
                    <div style="font-size:11px; color:var(--text-color); opacity:0.7;">
                        Cumulative trip frequency stacked across all 6 campus blocks
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with r2_head2:
                try:
                    area_mode = st.segmented_control(
                        "Area Mode",
                        options=["Trips", "% Share"],
                        default="Trips",
                        label_visibility="collapsed"
                    )
                except AttributeError:
                    area_mode = st.radio(
                        "Area Mode",
                        options=["Trips", "% Share"],
                        index=0,
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                area_mode = area_mode or "Trips"

            fig_area = build_stacked_area_chart(filtered_df if not filtered_df.empty else df, view_mode=area_mode)
            st.plotly_chart(fig_area, **WIDTH_STRETCH, config=CHART_CONFIG)

    with row2_col2:
        with st.container(border=True):
            w_h1, w_h2 = st.columns([2.5, 1.0], vertical_alignment="center")
            with w_h1:
                st.markdown(
                    """
                    <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                        Daily Fleet Capacity Bridge
                    </div>
                    <div style="font-size:11px; color:var(--text-color); opacity:0.7;">
                        Net effective trip capacity tracking rush surges &amp; maintenance delays
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with w_h2:
                with st.popover("🔍 Inspect", **WIDTH_STRETCH):
                    total_t = len(filtered_df) if not filtered_df.empty else len(df)
                    st.markdown("**Capacity Bridge Breakdown**")
                    st.write(f"- **Base Capacity:** {int(total_t * 0.78):,} trips")
                    st.write(f"- **Rush Surge:** +{int(total_t * 0.22):,} trips")
                    st.write(f"- **Smart Dispatch:** +{int(total_t * 0.08):,} trips")
                    st.write(f"- **Overload Delay:** -{int(total_t * 0.06):,} trips")
                    st.write(f"- **Maint. Downtime:** -{int(total_t * 0.03):,} trips")
            fig_bridge = build_waterfall_bridge_chart(filtered_df if not filtered_df.empty else df)
            st.plotly_chart(fig_bridge, **WIDTH_STRETCH, config=CHART_CONFIG)

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 4. ROW 3: FULL-WIDTH WEEKDAY X HOUR HEATMAP
    # ==========================================
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                When Students Use Campus Elevators
            </div>
            <div style="font-size:11px; color:var(--text-color); opacity:0.7;">
                Elevator passenger load density across Mon–Sun and 00:00–23:00 ({selected_block})
            </div>
            """,
            unsafe_allow_html=True
        )
        fig_heat = build_weekday_hour_heatmap(filtered_df if not filtered_df.empty else df)
        st.plotly_chart(fig_heat, **WIDTH_STRETCH, config=CHART_CONFIG)

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 5. ROW 4: 1:2 SPLIT (DONUT + RICH FLEET TABLE)
    # ==========================================
    row4_col1, row4_col2 = st.columns([1.0, 2.0])

    with row4_col1:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                    Traffic Share by Floor Zone
                </div>
                <div style="font-size:11px; color:var(--text-color); opacity:0.7;">
                    Demand distribution across Ground to 10th Floor
                </div>
                """,
                unsafe_allow_html=True
            )
            fig_donut = build_floor_zone_donut(filtered_df if not filtered_df.empty else df)
            st.plotly_chart(fig_donut, **WIDTH_STRETCH, config=CHART_CONFIG)

    with row4_col2:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                    Elevator Fleet Performance
                </div>
                <div style="font-size:11px; color:var(--text-color); opacity:0.7;">
                    Live health index, load trends, and scheduled service dates across campus
                </div>
                """,
                unsafe_allow_html=True
            )

            # Build enriched fleet table data using actual CSV history per lift
            table_rows = []
            service_dates = ["Dec 04, 2026", "Dec 18, 2026", "Jan 12, 2027", "Nov 28, 2026", "Jan 05, 2027", "Dec 22, 2026", "Feb 02, 2027", "Nov 30, 2026", "Dec 15, 2026", "Jan 19, 2027", "Dec 08, 2026", "Jan 25, 2027"]

            history_lookup = {}
            if not df.empty:
                sorted_df = df.sort_values("Timestamp")
                for (blk, lid), grp in sorted_df.groupby(["Block", "Lift_ID"]):
                    history_lookup[(blk, lid)] = [int(v) for v in grp["Passenger_Load_Percent"].tail(8).tolist()]

            for i, lift in enumerate(fleet_state):
                if selected_block != "All Blocks" and lift["Block"] != selected_block:
                    continue

                base_l = int(lift["Passenger_Load_Percent"])
                trend = history_lookup.get((lift["Block"], lift["Lift_ID"]), [base_l])
                if len(trend) < 2:
                    trend = [base_l, base_l]

                table_rows.append({
                    "Lift ID": f"{lift['Block'][:7]} - {lift['Lift_ID']}",
                    "Block": lift["Block"],
                    "Status": lift["Operational_Status"],
                    "Current Floor": f"Floor {lift['Current_Floor']}",
                    "Avg Load": f"{lift['Passenger_Load_Percent']}%",
                    "Load Trend": trend,
                    "Health Score": int(lift["Health_Score"]),
                    "Next Service": service_dates[i % len(service_dates)]
                })

            fleet_table_df = pd.DataFrame(table_rows)

            if not fleet_table_df.empty:
                st.dataframe(
                    fleet_table_df,
                    column_config={
                        "Lift ID": st.column_config.TextColumn("Elevator ID", width="medium"),
                        "Block": st.column_config.TextColumn("Campus Block", width="small"),
                        "Status": st.column_config.TextColumn("Status", width="small"),
                        "Current Floor": st.column_config.TextColumn("Floor", width="small"),
                        "Avg Load": st.column_config.TextColumn("Load", width="small"),
                        "Load Trend": st.column_config.LineChartColumn(
                            "Load Trend (8 ticks)",
                            width="medium",
                            y_min=0,
                            y_max=100
                        ),
                        "Health Score": st.column_config.ProgressColumn(
                            "Health Score",
                            format="%d%%",
                            min_value=0,
                            max_value=100,
                            width="medium"
                        ),
                        "Next Service": st.column_config.TextColumn("Next Service", width="small")
                    },
                    hide_index=True,
                    height=265,
                    **WIDTH_STRETCH
                )


# Render the page
render_overview()
