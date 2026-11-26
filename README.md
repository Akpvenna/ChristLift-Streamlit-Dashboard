# 🛗 ChristLift: Real-Time Campus Elevator Traffic & Maintenance Monitor

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://christlift-app-dashboard.streamlit.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-ChristLift--Streamlit--Dashboard-181717?logo=github)](https://github.com/Akpvenna/ChristLift-Streamlit-Dashboard)

> 🚀 **Live Deployed App:** [christlift-app-dashboard.streamlit.app](https://christlift-app-dashboard.streamlit.app/)  
> 💻 **GitHub Repository:** [Akpvenna/ChristLift-Streamlit-Dashboard](https://github.com/Akpvenna/ChristLift-Streamlit-Dashboard)

---

## 🌟 1. Project Overview

**ChristLift** is a clean, SaaS-inspired, multi-page real-time smart campus elevator analytics dashboard built with **Python, Streamlit, Pandas, and Plotly**. It serves as a simulated **Digital Twin & Analytics Hub** monitoring **24 elevators across 6 multi-story campus blocks** with real-time telemetry, smooth animated visualizations, and automatic CSV persistence.

### 🏢 Campus Fleet Configuration (24 Lifts Total)

| Campus Building | Lifts | Floor Range | Notes |
| :--- | :---: | :---: | :--- |
| **Central Block** | 10 (`Lift 1`–`Lift 10`) | `G – 10th` (`0` to `10`) | Highest campus traffic |
| **R&D Block** | 4 (`Lift 1`–`Lift 4`) | `G – 8th` (`0` to `8`) | Research & lab wing |
| **Block II** | 2 (`Lift 1`–`Lift 2`) | `G – 4th` (`0` to `4`) | Academic wing |
| **Main Auditorium** | 4 (`Lift 1`–`Lift 4`) | `B1 – 6th` (`-1` to `6`) | Includes Basement (`B1`) |
| **Block I** | 2 (`Lift 1`–`Lift 2`) | `G – 3rd` (`0` to `3`) | Low-rise academic block |
| **Block IV** | 2 (`Lift 1`–`Lift 2`) | `G – 8th` (`0` to `8`) | Multi-story block |

---

## 🛠️ 2. Tech Stack & Libraries

* ⚡ **Framework:** `streamlit` (`st.navigation(..., position="sidebar")`, `@st.fragment(run_every=30)`, `st.metric` sparklines, `st.popover`, and `st.dataframe` `column_config`)
* 🐼 **Data Handling:** `pandas`
* 📊 **Visualizations:** `plotly` (`plotly.graph_objects` & `plotly.express` with smooth spline curves, rounded bar corners, load-in entrance animations, and interactive hover-pop effects)
* 🔄 **Simulation & Persistence:** Python built-ins (`random`, `datetime`, `collections.deque`, `os`)

---

## ⚙️ 3. Core Architecture: Hybrid Real-Time + Auto-Seeded CSV

1. **📅 Auto-Seeded Historical Dataset (`lift_logs.csv`):**
   * Automatically generates **7 days of realistic synthetic campus telemetry** up to the current timestamp (with **15-minute density** for the last 24 hours and hourly data for the prior 6 days).
   * Models campus rush hours (`08:30–09:30`, `12:30–14:00`, `16:00–17:30`) and lighter weekend traffic so `1H`, `6H`, `24H`, and `7D` views are always populated.
2. **⏱️ Live Telemetry Engine (`@st.fragment(run_every=30)`):**
   * Ticks every **30 seconds** when **Live Tick** is enabled (and stops completely when paused).
   * Moves elevators realistically within each building's exact floor bounds (`min_floor` to `max_floor`), updates passenger load %, estimated wait times, energy draw, and health scores, and appends new rows to `lift_logs.csv`.

---

## 📑 4. Multi-Page Dashboard Features

### 📈 Page 1: `Overview` (Executive Analytics)
* 🎛️ **Top Control Bar:** Time Window (`1H`, `6H`, `24H`, `7D`), Building Filter (`All Blocks` or any of the 6 blocks), Live toggle, and CSV Export.
* 💡 **4 Interactive KPI Cards:** Active Elevators, Avg Traffic Load, Avg Waiting Time, and Simulated Fleet Energy with inline sparklines and `🔍 Inspect` breakdown popovers.
* 📊 **Visualizations:**
  * Smooth Spline **Stacked Area Chart** (`Trips` vs `% Share` toggle)
  * **Daily Fleet Capacity Bridge** (`go.Waterfall`)
  * Theme-adaptive **Weekday × Hour Heatmap** (`Mon–Sun` × `00:00–23:00`)
  * **Floor Zone Donut Chart** (including `Basement (B1)`)
  * **Elevator Fleet Performance Table** with inline `LineChartColumn` trends & `ProgressColumn` health bars.

### 🏢 Page 2: `Live Digital Twin` (Real-Time Shaft & Telemetry Monitor)
* 🛗 **Dynamic Vertical Elevator Shafts:** Scales automatically to each building's exact lift count (`2`, `4`, or `10`) and floor height (`B1–6`, `G–3`, `G–4`, `G–8`, `G–10`) with live hover tooltips.
* 📋 **Live Telemetry Feed:** Auto-appending scrollable table synced to `lift_logs.csv`.
* 📈 **Live Traffic Load % Over Time:** Smooth spline multi-line chart tracking active lifts.
* ⏰ **Busy Hour Analysis:** Hourly demand bar chart (`08:00–20:00`).
* 🎯 **Lift Performance Radar:** Interactive polar chart comparing Health Score, Capacity Load, Dispatch Speed, and Floor Coverage.

### 🔔 Page 3: `Maintenance & Logs` (Diagnostics & Fault Simulator)
* 🚨 **4 Maintenance KPI Cards:** Active Alerts, Lifts Operational, Overload Events Today, and Avg Fleet Health Score.
* 🗂️ **Scrollable Live Incident & Maintenance Log:** Filterable by severity (`All`, `Critical`, `Warning`, `Info`) alongside an **Incident Breakdown** horizontal bar chart.
* ⚡ **Interactive Fault Simulator:** Inject `Overload (96%)`, `Door Fault`, or `Emergency Maintenance` on any lift, or click **Restore All Lifts** to reset the fleet.
* 🔍 **Searchable `lift_logs.csv` Explorer:** Filter historical records and download as CSV.

---

## 🎨 5. Theme & Animation Polish

* 🌗 **Native Light, Dark & System Themes:** Switch seamlessly anytime via the top-right `⋮ → Settings → Theme` menu.
* ✨ **Smooth Animations:** Charts animate smoothly from `0` on load (including clockwise sweep for the Donut chart) and feature interactive **hover-pop** effects on slices, bars, and data points.

---

## 📁 6. Project Structure

```text
Dashboard/
├── .streamlit/
│   └── config.toml          # Server & browser configuration
├── utils/
│   ├── __init__.py
│   ├── simulator.py         # 24-lift fleet state, 7-day auto-seeding & live tick engine
│   └── charts.py            # Reusable Plotly chart builders
├── views/
│   ├── overview.py          # 📈 Page 1: Executive Campus Analytics
│   ├── digital_twin.py      # 🏢 Page 2: Live Shaft Twin & Telemetry
│   └── maintenance.py       # 🔔 Page 3: Diagnostics, Fault Simulator & Logs
├── app.py                   # Entry point with sidebar navigation, CSS & animations
├── lift_logs.csv            # Auto-generated & appended telemetry dataset
├── requirements.txt         # streamlit, pandas, plotly
└── README.md                # Project documentation
```

---

## 🚀 7. Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
