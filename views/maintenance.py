"""
ChristLift - Page 3: Maintenance & Logs (Alerts, Diagnostics & Fault Simulator)
Features:
- 4 Maintenance KPI metric cards
- Filterable Live Incident & Maintenance Log (All / Critical / Warning / Info)
- Incident Breakdown Chart
- Interactive Fault Simulator Panel (Overload, Door Fault, Maintenance, Restore All)
- Searchable lift_logs.csv table explorer with CSV export
"""

import os
import pandas as pd
import streamlit as st

from utils.charts import build_incident_breakdown_chart
from utils.simulator import (
    CSV_FILE,
    BLOCKS,
    get_lifts_for_block,
    trigger_fault,
    restore_all_lifts,
    initialize_session
)

WIDTH_STRETCH = {"width": "stretch"}
CHART_CONFIG = {"displayModeBar": "hover", "displaylogo": False}


def load_raw_logs():
    """Loads CSV logs for the explorer table."""
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 100:
        try:
            return pd.read_csv(CSV_FILE)
        except Exception:
            pass
    return pd.DataFrame()


def render_maintenance():
    initialize_session()
    # Top Header
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:22px;">🔔</span>
            <span style="font-size:20px; font-weight:700; color:var(--text-color); letter-spacing:-0.02em;">Maintenance &amp; Diagnostics</span>
        </div>
        <div style="font-size:12px; color:var(--text-color); opacity:0.7; margin-top:-2px;">
            Hardware health diagnostics, incident logs, fault injection controls, and historical CSV telemetry
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    fleet = st.session_state.get("fleet", [])
    incidents = st.session_state.get("incident_log", [])

    total_lifts = len(fleet)
    operational_lifts = sum(1 for l in fleet if l.get("Operational_Status") == "Operational")
    alert_lifts = total_lifts - operational_lifts
    avg_health = int(sum(l.get("Health_Score", 90) for l in fleet) / max(1, total_lifts))
    overloads_today = sum(1 for inc in incidents if "Overload" in inc.get("msg", "") or "88%" in inc.get("msg", ""))

    # ==========================================
    # 1. ROW 1: 4 MAINTENANCE KPI METRICS
    # ==========================================
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            label="Active Alerts",
            value=f"{alert_lifts} Warnings" if alert_lifts > 0 else "0 Alerts",
            delta="High Attention" if alert_lifts > 0 else "All Clear",
            delta_color="inverse" if alert_lifts > 0 else "normal",
            chart_data=[0, 1, 1, 2, 1, alert_lifts],
            chart_type="line",
            border=True
        )

    with kpi2:
        st.metric(
            label="Lifts Operational",
            value=f"{operational_lifts} / {total_lifts}",
            delta=f"{int((operational_lifts/max(1, total_lifts))*100)}% Fleet Uptime",
            delta_color="normal",
            chart_data=[11, 11, 12, 12, 11, operational_lifts],
            chart_type="area",
            border=True
        )

    with kpi3:
        st.metric(
            label="Overload Events Today",
            value=f"{overloads_today} Logged",
            delta="Peak Transition Hour",
            delta_color="off",
            chart_data=[2, 4, 7, 5, 6, overloads_today],
            chart_type="bar",
            border=True
        )

    with kpi4:
        st.metric(
            label="Avg Fleet Health Score",
            value=f"{avg_health}%",
            delta="Optimum Mechanical Index",
            delta_color="normal",
            chart_data=[92, 94, 96, 95, 93, avg_health],
            chart_type="line",
            border=True
        )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 2. ROW 2: 2-COLUMN DIAGNOSTICS & ALERTS
    # ==========================================
    diag_col1, diag_col2 = st.columns([1.0, 1.15])

    with diag_col1:
        with st.container(border=True, height=350):
            log_head1, log_head2 = st.columns([1.5, 1.3], vertical_alignment="center")
            with log_head1:
                st.markdown(
                    """
                    <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                        Live Incident &amp; Maintenance Log
                    </div>
                    <div style="font-size:11px; color:var(--text-color); opacity:0.7;">
                        Real-time alerts, sensor interrupts, and door cycle delays
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with log_head2:
                try:
                    severity_filter = st.segmented_control(
                        "Severity",
                        options=["All", "Critical", "Warning", "Info"],
                        default="All",
                        label_visibility="collapsed"
                    )
                except AttributeError:
                    severity_filter = st.radio(
                        "Severity",
                        options=["All", "Critical", "Warning", "Info"],
                        index=0,
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                severity_filter = severity_filter or "All"

            # Render incident list items
            display_incidents = [
                inc for inc in incidents
                if severity_filter == "All" or inc.get("severity") == severity_filter
            ]

            if display_incidents:
                with st.container(height=230, border=False):
                    for inc in display_incidents:
                        sev = inc.get("severity", "Info")
                        if sev == "Critical":
                            badge_bg = "#FEE2E2"
                            badge_color = "#991B1B"
                            border_color = "rgba(239, 68, 68, 0.5)"
                            icon = "🔴"
                        elif sev == "Warning":
                            badge_bg = "#FEF3C7"
                            badge_color = "#92400E"
                            border_color = "rgba(245, 158, 11, 0.5)"
                            icon = "⚠️"
                        else:
                            badge_bg = "#E0E7FF"
                            badge_color = "#3730A3"
                            border_color = "rgba(99, 102, 241, 0.45)"
                            icon = "ℹ️"

                        st.markdown(
                            f"""
                            <div style="display:flex; justify-content:space-between; align-items:center; background-color:#FFFFFF; border:1px solid {border_color}; border-radius:6px; padding:7px 10px; margin-bottom:5px; font-size:12px;">
                                <div style="display:flex; align-items:center; gap:8px;">
                                    <span>{icon}</span>
                                    <div>
                                        <span style="font-weight:600; color:#0F172A;">[{inc.get('time')}] {inc.get('block')} &bull; {inc.get('lift')}:</span>
                                        <span style="color:#475569; margin-left:4px;">{inc.get('msg')}</span>
                                    </div>
                                </div>
                                <span style="background-color:{badge_bg}; color:{badge_color}; font-size:10px; font-weight:700; padding:2px 7px; border-radius:4px;">
                                    {sev.upper()}
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                with st.container(height=230, border=False):
                    st.info(f"No incidents currently matching severity '{severity_filter}'.")

    with diag_col2:
        with st.container(border=True, height=350):
            st.markdown(
                """
                <div style="font-size:14px; font-weight:600; color:var(--text-color);">
                    Incident Breakdown
                </div>
                <div style="font-size:11px; color:var(--text-color); opacity:0.7;">
                    Categorized breakdown of logged alerts &amp; anomalies
                </div>
                """,
                unsafe_allow_html=True
            )
            fig_incidents = build_incident_breakdown_chart(incidents)
            st.plotly_chart(fig_incidents, **WIDTH_STRETCH, config=CHART_CONFIG)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 3. ROW 3: INTERACTIVE FAULT SIMULATOR & RAW CSV
    # ==========================================
    sim_col, csv_col = st.columns([1.1, 1.2])

    with sim_col:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display:flex; align-items:center; gap:6px;">
                    <span style="font-size:16px;">⚡</span>
                    <span style="font-size:14px; font-weight:700; color:var(--text-color);">Interactive Fault Simulator</span>
                </div>
                <div style="font-size:11px; color:var(--text-color); opacity:0.7; margin-bottom:10px;">
                    Inject live operational anomalies into the Digital Twin to demonstrate real-time alert dispatch
                </div>
                """,
                unsafe_allow_html=True
            )

            v_c1, v_c2 = st.columns(2)
            with v_c1:
                target_block = st.selectbox("Target Block", options=BLOCKS, key="sim_target_block")
            with v_c2:
                target_lift = st.selectbox("Target Lift", options=get_lifts_for_block(target_block), key="sim_target_lift")

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🚨 Trigger Overload (96%)", **WIDTH_STRETCH):
                    trigger_fault(target_block, target_lift, "Overload")
                    st.toast(f"Triggered Overload on {target_block} - {target_lift}!", icon="🚨")
                    st.rerun()

                if st.button("🚪 Simulate Door Fault", **WIDTH_STRETCH):
                    trigger_fault(target_block, target_lift, "Door Fault")
                    st.toast(f"Simulated Door Fault on {target_block} - {target_lift}!", icon="⚠️")
                    st.rerun()

            with btn_col2:
                if st.button("🛠️ Emergency Maintenance", **WIDTH_STRETCH):
                    trigger_fault(target_block, target_lift, "Maintenance")
                    st.toast(f"Set Emergency Maintenance for {target_block} - {target_lift}!", icon="🔧")
                    st.rerun()

                if st.button("✅ Restore All Lifts", type="primary", **WIDTH_STRETCH):
                    restore_all_lifts()
                    st.toast("Restored all 24 elevators to full operational readiness!", icon="✅")
                    st.rerun()

    with csv_col:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display:flex; align-items:center; gap:6px;">
                    <span style="font-size:16px;">📁</span>
                    <span style="font-size:14px; font-weight:700; color:var(--text-color);">Searchable lift_logs.csv Explorer</span>
                </div>
                <div style="font-size:11px; color:var(--text-color); opacity:0.7; margin-bottom:6px;">
                    Query background CSV telemetry records generated by simulation ticks
                </div>
                """,
                unsafe_allow_html=True
            )

            raw_df = load_raw_logs()

            search_c1, search_c2 = st.columns([2.0, 1.0], vertical_alignment="center")
            with search_c1:
                search_query = st.text_input(
                    "Search Logs",
                    placeholder="Search by Block, Lift ID, or Status...",
                    label_visibility="collapsed"
                )
            with search_c2:
                if not raw_df.empty:
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=raw_df.to_csv(index=False).encode("utf-8"),
                        file_name="christlift_logs_full.csv",
                        mime="text/csv",
                        **WIDTH_STRETCH
                    )

            if not raw_df.empty:
                filtered_raw = raw_df.copy()
                if search_query:
                    mask = (
                        filtered_raw["Block"].astype(str).str.contains(search_query, case=False, na=False) |
                        filtered_raw["Lift_ID"].astype(str).str.contains(search_query, case=False, na=False) |
                        filtered_raw["Operational_Status"].astype(str).str.contains(search_query, case=False, na=False)
                    )
                    filtered_raw = filtered_raw[mask]

                st.dataframe(
                    filtered_raw.tail(30).iloc[::-1],
                    hide_index=True,
                    height=180,
                    **WIDTH_STRETCH
                )
            else:
                st.info("No CSV telemetry data logged yet.")


# Render page
render_maintenance()
