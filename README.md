# ChristLift: Real-Time Campus Elevator Traffic & Maintenance Monitor

> **Course:** 2MCA-A&B Python Programming (MCA411-2) – Component 3 Assignment  
> **Developer:** Reg No: 2647202  
> **Target Environment:** CHRIST (Deemed to be University) – Multi-story Campus Blocks  

---

## 1. Project Overview

**ChristLift** is a clean, SaaS-inspired, multi-page real-time smart campus dashboard built with **Python, Streamlit, Pandas, and Plotly**. It acts as a simulated **Digital Twin & Analytics Hub** for elevators across CHRIST University's multi-story buildings (`Central Block`, `R&D Block`, and `Block II`).

The UI combines a crisp, modern BI aesthetic (inspired by executive SaaS dashboards with white cards, soft borders, top navigation, and rich inline table visuals) with a live, auto-updating elevator telemetry simulation.

> **Scope Note for AI Assistant (Antigravity):**  
> Keep the codebase modular, clean, and lightweight so it runs effortlessly on **Streamlit Community Cloud** and is easy to explain during a 5-minute VIVA. Use only standard, reliable libraries (`streamlit`, `pandas`, `numpy`, `plotly`).

---

## 2. Tech Stack & Libraries

* **Framework:** `streamlit` (using `st.navigation(..., position="top")`, `@st.fragment(run_every=3)`, `st.metric` sparklines, and `st.dataframe` `column_config`)
* **Data Handling:** `pandas`, `numpy`
* **Visualizations:** `plotly` (`plotly.graph_objects` and `plotly.express`)
* **Simulation & Storage:** Python built-ins (`random`, `time`, `datetime`, `os`)

---

## 3. Core Architecture: Hybrid Real-Time + Auto-Seeded CSV

Because there are no physical IoT sensors wired to the elevators, **ChristLift** uses a **Hybrid Simulation Architecture**:

1. **Auto-Seeded Historical Dataset (`lift_logs.csv`):**
   * On first launch (if `lift_logs.csv` does not exist), a helper module (`utils/simulator.py`) automatically generates **7 days of realistic synthetic campus telemetry** (covering Mon–Sun, 00:00–23:00, with realistic campus rush hours at 08:30–09:30, 12:30–14:00, and 16:00–17:30).
   * This ensures heatmaps, stacked area charts, donut charts, and bridge charts are immediately populated and never look empty on Streamlit Cloud.
2. **Live Telemetry Engine (`@st.fragment(run_every=3)`):**
   * Every **3 seconds** (when Live Feed is enabled), the simulation ticks forward for all lifts across all blocks.
   * Lifts move realistically (`±1` to `±3` floors within `0–10`), passenger load fluctuates smoothly (`0–100%`), estimated wait time updates, and occasional overload (`>85%`) or maintenance alerts trigger.
   * Each tick appends new rows to `lift_logs.csv` in the background and updates `st.session_state` so the Digital Twin and live charts update without freezing filters or dropdowns.

### Data Schema (`lift_logs.csv`)

| Column | Type | Example / Range | Description |
| :--- | :--- | :--- | :--- |
| `Timestamp` | Datetime String | `2026-11-23 14:05:12` | Exact time the telemetry packet was logged |
| `Block` | String | `Central Block`, `R&D Block`, `Block II` | Campus building name |
| `Lift_ID` | String | `Lift 1`, `Lift 2`, `Lift 3`, `Lift 4` | Elevator identifier within the block |
| `Current_Floor` | Integer | `0` (Ground) to `10` | Current elevator floor position |
| `Direction` | String | `Going Up`, `Going Down`, `Idle` | Current movement state |
| `Passenger_Load_Percent` | Integer | `0` to `100` | Simulated capacity load (%) |
| `Est_Wait_Sec` | Integer | `15` to `180` | Estimated wait time in seconds |
| `Energy_kWh` | Float | `0.05` to `0.45` | Simulated energy consumed in interval |
| `Health_Score` | Integer | `35` to `100` | Mechanical health index of the lift |
| `Operational_Status` | String | `Operational`, `High Load`, `Temporary Delay`, `Maintenance` | Current operational state |

---

## 4. Multi-Page Navigation & Dashboard Specification

Use Streamlit's modern **top navigation bar** (`st.navigation` with `position="top"`) featuring **3 dedicated pages** plus a persistent header badge (`CHRIST (Deemed to be University) – ChristLift | Reg No: 2647202`).

---

### Page 1: `Overview` (Executive Campus Analytics)
*Clean BI overview layout with high-level KPIs, trend charts, heatmap, and fleet health table.*

* **Top Control Bar:**
  * Time Window Segmented Pills (`1H`, `6H`, `24H`, `7D`) via `st.segmented_control`
  * Campus Block Filter (`st.popover` or `st.selectbox`: All Blocks, Central Block, R&D Block, Block II)
  * `🟢 Live` simulation status toggle, `Reset Filters`, and `Export CSV` (`st.download_button`)
* **Row 1 — 4 KPI Metric Cards with Inline Sparklines** (styled inside clean bordered cards):
  1. **Active Elevators** (e.g., `11 / 12` | `+100% Operational` | Green Area Sparkline)
  2. **Avg Traffic Load** (e.g., `68%` | `+5.2% vs. peak hour` | Amber/Coral Bar Sparkline)
  3. **Avg Waiting Time** (e.g., `1.8 mins` | `-0.4 mins today` | Green Line Sparkline)
  4. **Simulated Fleet Energy** (e.g., `12.4 kWh` | `Normal Consumption` | Teal Bar Sparkline)
* **Row 2 — 2-Column Analytical Charts:**
  * **Left: Stacked Area Chart — *Elevator Traffic Volume by Campus Block***
    * Stacked area chart showing trips/load over time split by `Central Block`, `R&D Block`, and `Block II`.
    * Includes a segmented toggle (`Trips` vs `% Share`) right above/beside the chart.
  * **Right: Waterfall (Bridge) Chart — *Daily Fleet Capacity Bridge***
    * Plotly `go.Waterfall` showing how net effective capacity moves from `Base Capacity` → `+Peak Rush Surge` → `+Smart Dispatch Gain` → `-Overload Delays` → `-Maintenance Downtime` → `Net Effective Capacity`.
* **Row 3 — Full-Width Heatmap:**
  * **Weekday × Hour Heatmap — *When Students Use Campus Elevators***
    * Plotly heatmap with `Mon–Sun` on the Y-axis and `00:00–23:00` on the X-axis using a clean soft-indigo/blue color scale (`Fewer` → `More`), dynamically reacting to the Block filter.
* **Row 4 — 1:2 Split (Donut + Rich Fleet Table):**
  * **Left: Donut Chart — *Traffic Share by Floor Zone***
    * Plotly Pie/Donut chart (`hole=0.6`) with total trips displayed in the center, broken down by floor zones (`Ground–2nd`, `3rd–5th`, `6th–8th`, `9th–10th`) or by Campus Block.
  * **Right: Rich Fleet Health Table — *Elevator Fleet Performance***
    * `st.dataframe` enhanced with `st.column_config`:
      * `Lift ID` & `Block`
      * `Status` (clean label)
      * `Avg Load (%)`
      * `Load Trend` using **`st.column_config.LineChartColumn`** (inline mini sparkline per row!)
      * `Health Score` using **`st.column_config.ProgressColumn`** (visual progress bar `0–100`)
      * `Next Service Date`

---

### Page 2: `Live Digital Twin` (Real-Time Shaft & Telemetry Monitor)
*Real-time operational command view updating every 3 seconds via `@st.fragment(run_every=3)`.*

* **Top Controls:** Block Selector (`Central Block`, `R&D Block`, `Block II`), Live Simulation Toggle (`🟢 LIVE - SIMULATION RUNNING`), and manual `Step Tick` button.
* **Left Column — Live Infrastructure Twin:**
  1. **Visual Elevator Shafts (Ground to 10th Floor):**
     * Custom Plotly visualization rendering 4 vertical elevator shafts (`Lift 1` to `Lift 4`) from `Ground (0)` to `10th Floor`.
     * Displays each elevator car as a colored block positioned at its exact current floor, annotated with floor label, direction arrow (`▲` / `▼` / `●`), and current passenger load `%`.
     * Color-coded by state: Emerald Green (`Normal <60%`), Royal Blue (`Moderate 60–84%`), Amber/Red (`High Load ≥85%` or `Maintenance`).
  2. **Real-Time Telemetry Feed (Auto-CSV Appended):**
     * Clean scrollable table displaying the latest 15–20 live rows from `lift_logs.csv` (`Timestamp`, `Lift_ID`, `Current_Floor`, `Direction`, `Passenger_Load_Percent`, `Operational_Status`).
* **Right Column — Live Trends & Spatial Blueprint:**
  1. **Multi-Line Live Chart — *Live Traffic Load % Over Time (L1–L4)***
     * Rolling window of the last 25 timestamps plotting `Passenger_Load_Percent` for each lift (`Lift 1`–`Lift 4`).
  2. **Busy Hour Bar Chart — *Hourly Capacity % Analysis (08:00–20:00)***
     * Clean vertical bar chart highlighting peak campus transition hours.
  3. **Digital Blueprint — *Campus Elevator Locations***
     * Clean Plotly 2D architectural schematic floor plan of the selected campus block (corridors, central courtyard, staircases) with live interactive scatter nodes marking each elevator's location, colored by live load/status with hover tooltips showing floor, wait time, and load %.

---

### Page 3: `Maintenance & Logs` (Alerts, Diagnostics & VIVA Simulator)
*Operational diagnostics, incident tracking, and interactive controls for live VIVA demonstrations.*

* **Row 1 — 4 Maintenance KPI Cards:** Active Alerts, Lifts Operational, Overload Events Today, Avg Fleet Health Score.
* **Row 2 — 2-Column Diagnostics:**
  * **Left: Live Incident & Maintenance Log**
    * Filterable by severity (`All`, `Critical`, `Warning`, `Info`), showing timestamped alerts (e.g., `[18:54:12] Lift 2 – High Passenger Load Alert (92%)`, `[18:50:04] Lift 4 – Door Sensor Delay on 7th Floor`).
  * **Right: Incident Breakdown Chart**
    * Clean horizontal bar chart or grouped bar chart categorizing incidents by type (`Overload Warning`, `Temporary Delay`, `Door Malfunction`, `Scheduled Check`).
* **Row 3 — Interactive VIVA Fault Simulator & Raw Data Explorer:**
  * **VIVA Demo Control Panel:** Allows the presenter to select any Block & Lift and click buttons like `Trigger Overload (95%)`, `Simulate Door Fault`, or `Restore All Lifts`—immediately updating the Digital Twin, KPIs, and Incident Log during the VIVA presentation.
  * **Searchable `lift_logs.csv` Explorer** with filter and CSV download button.

---

## 5. UI/UX & Styling Guidelines

* **Theme:** Crisp, Clean **Light SaaS Mode** (configured via `.streamlit/config.toml` + minimal custom CSS).
* **Color Palette:**
  * **App Background:** Soft off-white / slate tint (`#F8FAFC`)
  * **Card Containers:** Pure white (`#FFFFFF`) with `1px solid #E2E8F0` border and subtle `10px` border-radius
  * **Primary Brand Accent:** Deep Indigo / CHRIST Navy (`#1E3A8A` / `#4F46E5`)
  * **Status Colors:** Emerald Green (`#10B981`), Sky/Royal Blue (`#3B82F6`), Amber (`#F59E0B`), Coral Red (`#EF4444`)
* **Chart Polish:** Transparent plot/paper backgrounds, clean sans-serif typography, minimal gridlines (`#F1F5F9`), no cluttered Plotly modebars (`config={"displayModeBar": False}`).

---

## 6. Project Folder Structure

```text
ChristLift/
├── .streamlit/
│   └── config.toml          # Clean light SaaS theme configuration
├── utils/
│   ├── __init__.py
│   ├── simulator.py         # Auto-seeding + live tick + CSV append logic
│   └── charts.py            # Reusable Plotly chart builders (shafts, heatmap, waterfall, blueprint, etc.)
├── views/
│   ├── overview.py          # Page 1: Executive Analytics (Nimbus BI style)
│   ├── digital_twin.py      # Page 2: Live Shaft Twin & Telemetry
│   └── maintenance.py       # Page 3: Alerts, Diagnostics & VIVA Fault Simulator
├── app.py                   # Entry point with top st.navigation & shared CSS
├── lift_logs.csv            # Auto-generated & appended at runtime
├── requirements.txt         # streamlit, pandas, numpy, plotly
└── README.md                # Full project blueprint
```

---

## 7. Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
