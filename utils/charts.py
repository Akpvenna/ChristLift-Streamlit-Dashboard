"""
ChristLift Reusable Plotly Visualizations
All charts feature smooth edges/vertices (spline smoothing & rounded bar corners),
crisp outlines, interactive hover modes, and theme-adaptive styling.
"""

import inspect
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

WIDTH_STRETCH = {"width": "stretch"} if "width" in inspect.signature(st.dataframe).parameters else {"use_container_width": True}
CHART_CONFIG = {"displayModeBar": "hover", "displaylogo": False}

# Common styling constants
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
HOVER_LABEL = dict(
    bgcolor="rgba(15, 23, 42, 0.94)",
    bordercolor="#4F46E5",
    font=dict(family=FONT_FAMILY, size=12, color="#F8FAFC")
)
TRANSITION_CFG = dict(duration=650, easing="cubic-in-out")
COLOR_PRIMARY = "#4F46E5"   # Deep Indigo
COLOR_SUCCESS = "#10B981"   # Emerald Green
COLOR_WARNING = "#F59E0B"   # Amber
COLOR_DANGER = "#EF4444"    # Coral Red
COLOR_INFO = "#3B82F6"      # Royal Blue
COLOR_SLATE = "#64748B"     # Slate 500
COLOR_GRID = "rgba(148, 163, 184, 0.16)"
BG_TRANSPARENT = "rgba(0,0,0,0)"

ALL_BLOCKS = ["Central Block", "R&D Block", "Block II", "Main Auditorium", "Block I", "Block IV"]
BLOCK_PALETTE = {
    "Central Block": ("#4F46E5", "rgba(79, 70, 229, 0.25)"),
    "R&D Block": ("#06B6D4", "rgba(6, 182, 212, 0.25)"),
    "Block II": ("#10B981", "rgba(16, 185, 129, 0.25)"),
    "Main Auditorium": ("#F59E0B", "rgba(245, 158, 11, 0.25)"),
    "Block I": ("#8B5CF6", "rgba(139, 92, 246, 0.25)"),
    "Block IV": ("#EC4899", "rgba(236, 72, 153, 0.25)"),
}


# ==========================================
# 1. PAGE 1 (OVERVIEW) VISUALIZATIONS
# ==========================================
def build_stacked_area_chart(df, view_mode="Trips"):
    """
    Smooth spline Stacked Area Chart showing elevator traffic over time across all 6 campus blocks.
    """
    if df.empty or "Timestamp" not in df.columns:
        return go.Figure()

    data = df.copy()
    data["Timestamp"] = pd.to_datetime(data["Timestamp"], format="mixed", errors="coerce")
    data = data.dropna(subset=["Timestamp"])
    if data.empty:
        return go.Figure()

    span_hours = max(0.0, (data["Timestamp"].max() - data["Timestamp"].min()).total_seconds() / 3600.0)
    if span_hours <= 2:
        freq = "15min"
    elif span_hours <= 12:
        freq = "30min"
    elif span_hours <= 48:
        freq = "1h"
    else:
        freq = "4h"

    resampled = data.groupby([pd.Grouper(key="Timestamp", freq=freq), "Block"])["Passenger_Load_Percent"].mean().reset_index()
    pivot_df = resampled.pivot(index="Timestamp", columns="Block", values="Passenger_Load_Percent").fillna(0)

    active_blocks = [b for b in ALL_BLOCKS if b in pivot_df.columns]
    if not active_blocks:
        return go.Figure()

    if view_mode == "% Share":
        row_sums = pivot_df[active_blocks].sum(axis=1).replace(0, 1)
        plot_df = pivot_df[active_blocks].div(row_sums, axis=0) * 100
        y_title = "Traffic Share (%)"
        y_range = [0, 100]
    else:
        plot_df = pivot_df[active_blocks]
        y_title = "Elevator Trip Volume"
        y_range = None

    fig = go.Figure()
    for block in active_blocks:
        stroke_col, fill_col = BLOCK_PALETTE.get(block, ("#64748B", "rgba(100,116,139,0.2)"))
        fig.add_trace(go.Scatter(
            x=plot_df.index,
            y=plot_df[block],
            mode="lines",
            name=block,
            stackgroup="one",
            line=dict(width=2.0, color=stroke_col, shape="spline", smoothing=1.15),
            fillcolor=fill_col,
            hovertemplate=f"<b>{block}</b>: %{{y:.1f}}<extra></extra>"
        ))

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        hovermode="x unified",
        hoverlabel=HOVER_LABEL,
        transition=TRANSITION_CFG,
        margin=dict(l=10, r=10, t=20, b=10),
        height=265,
        font=dict(family=FONT_FAMILY),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=COLOR_SLATE)
        ),
        yaxis=dict(
            title=y_title,
            title_font=dict(size=10, color=COLOR_SLATE),
            range=y_range,
            gridcolor=COLOR_GRID,
            tickfont=dict(size=9, color=COLOR_SLATE)
        ),
        xaxis=dict(
            gridcolor=COLOR_GRID,
            tickfont=dict(size=9, color=COLOR_SLATE)
        )
    )
    return fig


def build_waterfall_bridge_chart(df):
    """
    Outlined Daily Fleet Capacity & Efficiency Bridge Chart (go.Waterfall).
    """
    total_trips = len(df) if not df.empty else 1200
    base = int(total_trips * 0.78)
    surge = int(total_trips * 0.22)
    dispatch_gain = int(total_trips * 0.08)
    overload_loss = -int(total_trips * 0.06)
    maint_loss = -int(total_trips * 0.03)

    fig = go.Figure(go.Waterfall(
        name="Fleet Capacity Bridge",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=["Base Capacity", "Rush Surge", "Smart Dispatch", "Overload Delay", "Maint. Downtime", "Net Capacity"],
        textposition="outside",
        text=[f"+{base}", f"+{surge}", f"+{dispatch_gain}", f"{overload_loss}", f"{maint_loss}", "Net"],
        y=[base, surge, dispatch_gain, overload_loss, maint_loss, 0],
        connector={"line": {"color": "rgba(148, 163, 184, 0.55)", "width": 1.6, "dash": "dot"}},
        decreasing={"marker": {"color": "#EF4444", "line": {"color": "#991B1B", "width": 1.5}}},
        increasing={"marker": {"color": "#10B981", "line": {"color": "#065F46", "width": 1.5}}},
        totals={"marker": {"color": "#4F46E5", "line": {"color": "#312E81", "width": 1.5}}},
        hovertemplate="<b>%{x}</b><br>Impact: <b>%{y:,}</b><extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        hoverlabel=HOVER_LABEL,
        transition=TRANSITION_CFG,
        barcornerradius=6,
        margin=dict(l=10, r=10, t=20, b=10),
        height=265,
        font=dict(family=FONT_FAMILY),
        yaxis=dict(
            title="Capacity Index (Trips)",
            title_font=dict(size=10, color=COLOR_SLATE),
            gridcolor=COLOR_GRID,
            tickfont=dict(size=9, color=COLOR_SLATE)
        ),
        xaxis=dict(
            tickfont=dict(size=9, color=COLOR_SLATE)
        )
    )
    return fig


def build_weekday_hour_heatmap(df):
    """
    Outlined Weekday x Hour Heatmap (Mon-Sun vs 00:00-23:00) with cell gaps for smooth visual separation.
    """
    if df.empty or "Timestamp" not in df.columns:
        return go.Figure()

    data = df.copy()
    data["Timestamp"] = pd.to_datetime(data["Timestamp"], format="mixed", errors="coerce")
    data = data.dropna(subset=["Timestamp"])
    if data.empty:
        return go.Figure()

    data["Weekday"] = data["Timestamp"].dt.day_name()
    data["Hour"] = data["Timestamp"].dt.hour

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours_order = list(range(24))

    grouped = data.groupby(["Weekday", "Hour"])["Passenger_Load_Percent"].mean().reset_index()
    heatmap_matrix = grouped.pivot(index="Weekday", columns="Hour", values="Passenger_Load_Percent").reindex(index=days_order, columns=hours_order).fillna(0)

    try:
        is_dark = (st.context.theme.type == "dark")
    except Exception:
        is_dark = False

    if is_dark:
        colorscale = [
            [0.0, "#1E293B"],   # Idle / No Data (dark slate)
            [0.25, "#0F766E"],  # Light (deep teal)
            [0.50, "#0284C7"],  # Moderate (ocean blue)
            [0.75, "#F59E0B"],  # Busy (amber)
            [1.0, "#EF4444"],   # Peak / Overload (coral red)
        ]
    else:
        colorscale = [
            [0.0, "#F1F5F9"],   # Idle / No Data (soft slate)
            [0.25, "#5EEAD4"],  # Light (mint teal)
            [0.50, "#38BDF8"],  # Moderate (sky blue)
            [0.75, "#F59E0B"],  # Busy (amber)
            [1.0, "#EF4444"],   # Peak / Overload (coral red)
        ]

    fig = go.Figure(go.Heatmap(
        z=heatmap_matrix.values,
        x=[f"{h:02d}:00" for h in hours_order],
        y=[d[:3] for d in days_order],
        zmin=0,
        zmax=100,
        xgap=3,
        ygap=3,
        colorscale=colorscale,
        colorbar=dict(
            title="Load %",
            title_font=dict(size=9, color=COLOR_SLATE),
            tickvals=[10, 50, 90],
            ticktext=["Low", "Mid", "Peak"],
            tickfont=dict(size=8, color=COLOR_SLATE),
            len=0.8,
            thickness=12
        ),
        hovertemplate="Day: <b>%{y}</b><br>Hour: <b>%{x}</b><br>Avg Load: <b>%{z:.1f}%</b><extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        hoverlabel=HOVER_LABEL,
        transition=TRANSITION_CFG,
        margin=dict(l=10, r=10, t=10, b=10),
        height=205,
        font=dict(family=FONT_FAMILY),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=9, color=COLOR_SLATE)
        ),
        xaxis=dict(
            tickfont=dict(size=8, color=COLOR_SLATE),
            tickangle=-45
        )
    )
    return fig


def build_floor_zone_donut(df):
    """
    Outlined Donut Chart (hole=0.62) with separated slices and center KPI text.
    """
    if df.empty or "Current_Floor" not in df.columns:
        return go.Figure()

    def categorize_zone(floor):
        if floor < 0:
            return "Basement (B1)"
        elif floor <= 2:
            return "Ground–2nd Floor"
        elif floor <= 5:
            return "3rd–5th Floor"
        elif floor <= 8:
            return "6th–8th Floor"
        return "9th–10th Floor"

    data = df.copy()
    data["Floor_Zone"] = data["Current_Floor"].apply(categorize_zone)
    zone_counts = data["Floor_Zone"].value_counts().reset_index()
    zone_counts.columns = ["Zone", "Count"]

    total_records = zone_counts["Count"].sum()

    fig = go.Figure(go.Pie(
        labels=zone_counts["Zone"],
        values=zone_counts["Count"],
        hole=0.62,
        pull=[0.025] * len(zone_counts),
        marker=dict(
            colors=["#4F46E5", "#06B6D4", "#10B981", "#F59E0B"],
            line=dict(color="rgba(255, 255, 255, 0.85)", width=2.5)
        ),
        textinfo="percent",
        textfont=dict(size=10, color="#FFFFFF"),
        hovertemplate="Zone: <b>%{label}</b><br>Trips: <b>%{value:,}</b> (%{percent})<extra></extra>"
    ))

    fig.add_annotation(
        text=f"<b>{total_records:,}</b><br><span style='font-size:10px; color:#64748B;'>Total Trips</span>",
        x=0.5, y=0.5,
        font=dict(family=FONT_FAMILY, size=14, color=COLOR_SLATE),
        showarrow=False
    )

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        hoverlabel=HOVER_LABEL,
        transition=TRANSITION_CFG,
        margin=dict(l=10, r=10, t=10, b=10),
        height=265,
        font=dict(family=FONT_FAMILY),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=9, color=COLOR_SLATE)
        )
    )
    return fig


# ==========================================
# 2. PAGE 2 (LIVE DIGITAL TWIN) VISUALIZATIONS
# ==========================================
def build_elevator_shafts_chart(fleet_df, max_floor=10, min_floor=0):
    """
    Dynamic visual elevator shafts (min_floor to max_floor, supporting Basement B1 = -1)
    adapting cleanly to 2, 4, or 10 lifts.
    """
    fig = go.Figure()
    if fleet_df.empty:
        return fig

    lifts = fleet_df["Lift_ID"].tolist()
    n_lifts = len(lifts)
    is_dense = n_lifts >= 6  # Central Block has 10 lifts

    shaft_half_w = 0.34 if is_dense else 0.32
    car_half_w = 0.31 if is_dense else 0.29

    hover_x, hover_y, hover_texts = [], [], []

    for idx, row in fleet_df.reset_index(drop=True).iterrows():
        lift_id = str(row["Lift_ID"])
        floor = min(max_floor, max(min_floor, int(row["Current_Floor"])))
        direction = str(row["Direction"])
        load = int(row["Passenger_Load_Percent"])
        status = str(row["Operational_Status"])
        wait_sec = int(row.get("Est_Wait_Sec", 30))

        # Outer shaft border
        fig.add_shape(
            type="rect",
            x0=idx - shaft_half_w, x1=idx + shaft_half_w,
            y0=min_floor - 0.5, y1=max_floor + 0.5,
            line=dict(color="rgba(100, 116, 139, 0.65)", width=1.8),
            fillcolor="rgba(148, 163, 184, 0.08)"
        )

        # Floor divider lines (min_floor to max_floor)
        for fl in range(min_floor, max_floor + 1):
            fig.add_shape(
                type="line",
                x0=idx - shaft_half_w, x1=idx + shaft_half_w,
                y0=fl - 0.5, y1=fl - 0.5,
                line=dict(color="rgba(148, 163, 184, 0.25)", width=1)
            )

        if status in ["Maintenance", "Temporary Delay"] or load >= 85:
            car_color = "#EF4444"
            car_border = "#991B1B"
        elif load >= 60:
            car_color = "#3B82F6"
            car_border = "#1D4ED8"
        else:
            car_color = "#10B981"
            car_border = "#047857"

        # Active car block with crisp outline
        fig.add_shape(
            type="rect",
            x0=idx - car_half_w, x1=idx + car_half_w,
            y0=floor - 0.42, y1=floor + 0.42,
            line=dict(color=car_border, width=2),
            fillcolor=car_color
        )

        dir_symbol = "▲" if "Up" in direction else ("▼" if "Down" in direction else "●")
        dir_short = "Going Up" if "Up" in direction else ("Going Down" if "Down" in direction else "Idle")
        ordinal = "B1" if floor == -1 else ("Ground" if floor == 0 else f"F{floor}")
        floor_short = "B1" if floor == -1 else ("G" if floor == 0 else str(floor))

        # Floor + Direction inside car
        car_label = f"<b>{floor_short} {dir_symbol}</b>"
        fig.add_annotation(
            x=idx, y=floor,
            text=car_label,
            showarrow=False,
            font=dict(color="#FFFFFF", size=10 if is_dense else 11, family=FONT_FAMILY)
        )

        # Clean load % tag below every shaft (no white callout boxes; full details appear on hover)
        fig.add_annotation(
            x=idx,
            y=min_floor - 0.85,
            text=f"<b>{load}%</b>",
            showarrow=False,
            font=dict(color=car_color, size=9 if is_dense else 10, family=FONT_FAMILY)
        )

        hover_x.append(idx)
        hover_y.append(floor)
        hover_texts.append(
            f"<b>{lift_id}</b><br>"
            f"Floor: <b>{ordinal}</b> ({dir_short})<br>"
            f"Load: <b>{load}%</b><br>"
            f"Est. Wait: <b>{wait_sec}s</b><br>"
            f"Status: <b>{status}</b><extra></extra>"
        )

    # Interactive hover markers on every elevator car
    fig.add_trace(go.Scatter(
        x=hover_x,
        y=hover_y,
        mode="markers",
        marker=dict(size=24 if is_dense else 32, opacity=0.01),
        hovertemplate=hover_texts,
        showlegend=False
    ))

    x_right = n_lifts - 0.3
    y_bottom = min_floor - 1.25
    floor_vals = list(range(min_floor, max_floor + 1))
    floor_labels = ["B1" if i == -1 else ("Ground" if i == 0 else str(i)) for i in floor_vals]

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        hoverlabel=HOVER_LABEL,
        transition=TRANSITION_CFG,
        uirevision=f"shafts_{n_lifts}_{min_floor}_{max_floor}",
        margin=dict(l=10, r=20, t=30, b=15),
        height=375,
        font=dict(family=FONT_FAMILY),
        yaxis=dict(
            title="Floor",
            title_font=dict(size=11, color=COLOR_SLATE),
            range=[y_bottom, max_floor + 0.75],
            tickmode="array",
            tickvals=floor_vals,
            ticktext=floor_labels,
            tickfont=dict(size=10, color=COLOR_SLATE),
            showgrid=False,
            zeroline=False
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(n_lifts)),
            ticktext=[l.replace("Lift ", "L") if is_dense else l for l in lifts],
            tickfont=dict(size=10 if is_dense else 11, color=COLOR_SLATE, family=FONT_FAMILY),
            range=[-0.55, x_right],
            showgrid=False,
            side="top"
        )
    )
    return fig


def build_live_traffic_line_chart(logs_df, selected_block):
    """
    Smooth spline Multi-Line Live Chart tracking Live Traffic Load % Over Time with outlined markers.
    """
    df = logs_df[logs_df["Block"] == selected_block].copy() if not logs_df.empty else pd.DataFrame()
    if df.empty:
        return go.Figure()

    unique_times = df["Timestamp"].drop_duplicates().tail(20)
    plot_df = df[df["Timestamp"].isin(unique_times)].copy()
    plot_df["Time"] = plot_df["Timestamp"].apply(lambda t: str(t).split()[-1] if len(str(t).split()) > 1 else str(t))

    palette = ["#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6", "#3B82F6", "#14B8A6", "#F97316", "#EF4444"]
    lifts = sorted(plot_df["Lift_ID"].unique(), key=lambda x: int(x.split()[-1]) if x.split()[-1].isdigit() else 99)

    fig = go.Figure()
    for i, lift_id in enumerate(lifts):
        sub = plot_df[plot_df["Lift_ID"] == lift_id]
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=sub["Time"],
            y=sub["Passenger_Load_Percent"],
            mode="lines+markers",
            name=lift_id,
            line=dict(color=color, width=2.2, shape="spline", smoothing=1.15),
            marker=dict(size=5, color=color, line=dict(width=1.2, color="#FFFFFF")),
            hovertemplate=f"<b>{lift_id}</b>: %{{y}}%<extra></extra>"
        ))

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        hovermode="x unified",
        hoverlabel=HOVER_LABEL,
        transition=TRANSITION_CFG,
        uirevision=selected_block,
        margin=dict(l=10, r=10, t=15, b=10),
        height=240,
        font=dict(family=FONT_FAMILY),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=8, color=COLOR_SLATE)
        ),
        yaxis=dict(
            title="Load (%)",
            title_font=dict(size=9, color=COLOR_SLATE),
            range=[0, 108],
            tickvals=[0, 25, 50, 75, 100],
            tickfont=dict(size=8, color=COLOR_SLATE),
            gridcolor=COLOR_GRID
        ),
        xaxis=dict(
            title="Time",
            title_font=dict(size=9, color=COLOR_SLATE),
            tickfont=dict(size=8, color=COLOR_SLATE),
            showgrid=False
        )
    )
    return fig


def build_busy_hour_chart(logs_df, selected_block):
    """
    Rounded-corner, outlined Busy Hour Bar Chart (08:00 to 20:00).
    """
    if logs_df.empty or "Timestamp" not in logs_df.columns:
        return go.Figure()

    df = logs_df[logs_df["Block"] == selected_block].copy() if selected_block != "All Blocks" else logs_df.copy()
    if df.empty:
        df = logs_df.copy()

    df["Hour"] = pd.to_datetime(df["Timestamp"], format="mixed", errors="coerce").dt.hour
    df = df.dropna(subset=["Hour"])
    filtered = df[(df["Hour"] >= 8) & (df["Hour"] <= 20)]

    hourly = filtered.groupby("Hour")["Passenger_Load_Percent"].mean().reset_index()
    colors = ["#4F46E5" if v >= 65 else "#38BDF8" for v in hourly["Passenger_Load_Percent"]]
    borders = ["#312E81" if v >= 65 else "#0284C7" for v in hourly["Passenger_Load_Percent"]]

    fig = go.Figure(go.Bar(
        x=[f"{int(h):02d}:00" for h in hourly["Hour"]],
        y=hourly["Passenger_Load_Percent"],
        marker=dict(color=colors, line=dict(color=borders, width=1.4)),
        hovertemplate="Hour: <b>%{x}</b><br>Average Demand: <b>%{y:.1f}%</b><extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        hoverlabel=HOVER_LABEL,
        transition=TRANSITION_CFG,
        barcornerradius=6,
        margin=dict(l=10, r=10, t=15, b=10),
        height=240,
        font=dict(family=FONT_FAMILY),
        yaxis=dict(
            title="Demand Load (%)",
            title_font=dict(size=9, color=COLOR_SLATE),
            range=[0, 105],
            tickfont=dict(size=8, color=COLOR_SLATE),
            gridcolor=COLOR_GRID
        ),
        xaxis=dict(
            title="Hour",
            title_font=dict(size=9, color=COLOR_SLATE),
            tickvals=["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"],
            tickfont=dict(size=9, color=COLOR_SLATE),
            gridcolor=BG_TRANSPARENT
        )
    )
    return fig


def build_lift_performance_radar(fleet_df, selected_block):
    """
    Experimental Replacement for Blueprint:
    Interactive Smooth Polar Radar Chart comparing Health Score, Capacity Load,
    Dispatch Efficiency, and Floor Coverage across lifts in the selected block.
    """
    fig = go.Figure()
    if fleet_df.empty:
        return fig

    categories = ["Health Score", "Capacity Load", "Dispatch Speed", "Floor Coverage", "Health Score"]
    palette = [
        ("#4F46E5", "rgba(79, 70, 229, 0.16)"),
        ("#10B981", "rgba(16, 185, 129, 0.16)"),
        ("#06B6D4", "rgba(6, 182, 212, 0.16)"),
        ("#F59E0B", "rgba(245, 158, 11, 0.16)"),
    ]

    # Show up to 4 representative lifts so radar stays uncluttered and readable
    sample_df = fleet_df.head(4)
    for idx, (_, row) in enumerate(sample_df.iterrows()):
        health = int(row.get("Health_Score", 90))
        load = int(row.get("Passenger_Load_Percent", 50))
        wait_sec = int(row.get("Est_Wait_Sec", 35))
        dispatch_speed = max(15, min(100, int(115 - wait_sec * 0.6)))
        min_fl = int(row.get("Min_Floor", 0))
        max_fl = max(min_fl + 1, int(row.get("Max_Floor", 10)))
        cur_fl = int(row.get("Current_Floor", min_fl))
        coverage = max(20, min(100, int(((cur_fl - min_fl) / (max_fl - min_fl)) * 70 + 30)))

        vals = [health, load, dispatch_speed, coverage, health]
        stroke, fill = palette[idx % len(palette)]

        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories,
            fill="toself",
            fillcolor=fill,
            line=dict(color=stroke, width=2.2, shape="spline"),
            marker=dict(size=5, color=stroke, line=dict(width=1, color="#FFFFFF")),
            name=str(row["Lift_ID"]),
            hovertemplate=f"<b>{selected_block} - {row['Lift_ID']}</b><br>%{{theta}}: <b>%{{r}}%</b><extra></extra>"
        ))

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        hoverlabel=HOVER_LABEL,
        transition=TRANSITION_CFG,
        uirevision=f"radar_{selected_block}",
        margin=dict(l=60, r=60, t=22, b=30),
        height=240,
        font=dict(family=FONT_FAMILY, size=10, color=COLOR_SLATE),
        polar=dict(
            bgcolor="rgba(148, 163, 184, 0.05)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=7, color=COLOR_SLATE),
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID
            ),
            angularaxis=dict(
                tickfont=dict(size=9, color=COLOR_SLATE),
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID
            )
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=8, color=COLOR_SLATE)
        )
    )
    return fig


# ==========================================
# 3. PAGE 3 (MAINTENANCE) VISUALIZATIONS
# ==========================================
def build_incident_breakdown_chart(incidents):
    """
    Rounded-corner, outlined Horizontal Bar Chart categorizing maintenance and incident alerts.
    """
    if not incidents:
        types = ["Overload Warning", "Temporary Delay", "Door Malfunction", "Scheduled Check"]
        counts = [6, 3, 2, 8]
    else:
        counts_dict = {"Overload Warning": 0, "Temporary Delay": 0, "Door Malfunction": 0, "Scheduled Check": 0}
        for inc in incidents:
            msg = inc.get("msg", "")
            if "Overload" in msg:
                counts_dict["Overload Warning"] += 1
            elif "Door" in msg:
                counts_dict["Door Malfunction"] += 1
            elif "delay" in msg.lower():
                counts_dict["Temporary Delay"] += 1
            else:
                counts_dict["Scheduled Check"] += 1
        types = list(counts_dict.keys())
        counts = list(counts_dict.values())

    fig = go.Figure(go.Bar(
        x=counts,
        y=types,
        orientation="h",
        marker=dict(
            color=["#EF4444", "#F59E0B", "#F97316", "#10B981"],
            line=dict(color=["#991B1B", "#B45309", "#C2410C", "#065F46"], width=1.4)
        ),
        text=[str(c) for c in counts],
        textposition="outside",
        textfont=dict(size=10, color=COLOR_SLATE, family=FONT_FAMILY),
        hovertemplate="Incident Type: <b>%{y}</b><br>Logged Count: <b>%{x}</b><extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor=BG_TRANSPARENT,
        plot_bgcolor=BG_TRANSPARENT,
        hoverlabel=HOVER_LABEL,
        transition=TRANSITION_CFG,
        barcornerradius=6,
        margin=dict(l=10, r=25, t=10, b=10),
        height=245,
        font=dict(family=FONT_FAMILY),
        xaxis=dict(
            title="Event Occurrences",
            title_font=dict(size=10, color=COLOR_SLATE),
            gridcolor=COLOR_GRID,
            tickfont=dict(size=9, color=COLOR_SLATE)
        ),
        yaxis=dict(
            tickfont=dict(size=10, color=COLOR_SLATE, family=FONT_FAMILY),
            gridcolor=BG_TRANSPARENT
        )
    )
    return fig
