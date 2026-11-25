"""
ChristLift Simulator Engine
Handles 7-day auto-seeding of lift_logs.csv across 6 campus buildings (24 lifts total),
in-memory elevator state transitions respecting each building's floor count,
live tick appending, and VIVA fault injection utilities.
"""

import os
import random
import datetime
import pandas as pd
import streamlit as st

CSV_FILE = "lift_logs.csv"

# Exact Campus Building Specifications (24 Lifts Total)
BUILDING_CONFIG = {
    "Central Block": {"lifts": 10, "max_floor": 10},
    "R&D Block": {"lifts": 4, "max_floor": 8},
    "Block II": {"lifts": 2, "max_floor": 10},
    "Main Auditorium": {"lifts": 4, "max_floor": 5},
    "Block I": {"lifts": 2, "max_floor": 8},
    "Block IV": {"lifts": 2, "max_floor": 8},
}

BLOCKS = list(BUILDING_CONFIG.keys())


def get_lifts_for_block(block):
    """Returns the exact list of Lift IDs for a given campus block."""
    count = BUILDING_CONFIG.get(block, {}).get("lifts", 4)
    return [f"Lift {i}" for i in range(1, count + 1)]


def get_max_floor(block):
    """Returns the top floor number for a given campus block."""
    return BUILDING_CONFIG.get(block, {}).get("max_floor", 10)


def build_default_fleet():
    """Builds the 24 default elevator states across all 6 campus buildings."""
    fleet = []
    rng = random.Random(42)
    for block, cfg in BUILDING_CONFIG.items():
        max_fl = cfg["max_floor"]
        for i in range(1, cfg["lifts"] + 1):
            floor = rng.randint(0, max_fl)
            if floor == 0:
                direction = "Going Up"
            elif floor == max_fl:
                direction = "Going Down"
            else:
                direction = rng.choice(["Going Up", "Going Down", "Idle"])

            load = rng.randint(15, 78) if direction != "Idle" else rng.randint(0, 25)
            health = rng.randint(86, 99)
            wait_sec = max(15, 20 + abs(floor - (max_fl // 2)) * 6 + int(load * 0.4))
            energy = round(0.12 * (1 + load / 100), 2)

            fleet.append({
                "Block": block,
                "Lift_ID": f"Lift {i}",
                "Current_Floor": floor,
                "Direction": direction,
                "Passenger_Load_Percent": load,
                "Est_Wait_Sec": wait_sec,
                "Energy_kWh": energy,
                "Health_Score": health,
                "Operational_Status": "Operational",
                "Max_Floor": max_fl,
            })
    return fleet


def seed_historical_logs(days=7):
    """Generates 7 days of synthetic campus telemetry for all 24 lifts if lift_logs.csv is missing or outdated."""
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 10000:
        try:
            sample_df = pd.read_csv(CSV_FILE, usecols=["Block", "Lift_ID", "Timestamp"])
            required_blocks = set(BLOCKS)
            present_blocks = set(sample_df["Block"].dropna().unique())
            if required_blocks.issubset(present_blocks):
                return
        except Exception:
            pass

    records = []
    now = datetime.datetime.now()
    start_date = now - datetime.timedelta(days=days)

    block_multipliers = {
        "Central Block": 1.08,
        "R&D Block": 0.96,
        "Block II": 0.92,
        "Main Auditorium": 0.85,
        "Block I": 0.90,
        "Block IV": 0.88,
    }

    for d in range(days):
        current_day = start_date + datetime.timedelta(days=d)
        is_weekend = current_day.weekday() >= 5

        for hour in range(24):
            ts = current_day.replace(hour=hour, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

            if 8 <= hour <= 9:
                base_min, base_max = (40, 70) if is_weekend else (70, 96)
            elif 12 <= hour <= 13:
                base_min, base_max = (35, 65) if is_weekend else (65, 92)
            elif 16 <= hour <= 17:
                base_min, base_max = (40, 65) if is_weekend else (70, 95)
            elif 10 <= hour <= 15:
                base_min, base_max = (20, 50) if is_weekend else (30, 65)
            elif 18 <= hour <= 21:
                base_min, base_max = (15, 40) if is_weekend else (25, 55)
            else:
                base_min, base_max = (0, 15)

            for block, cfg in BUILDING_CONFIG.items():
                max_fl = cfg["max_floor"]
                mult = block_multipliers.get(block, 1.0)

                for i in range(1, cfg["lifts"] + 1):
                    lift_id = f"Lift {i}"
                    load = int(min(100, max(0, random.randint(base_min, base_max) * mult)))
                    floor = random.randint(0, max_fl)

                    if load == 0:
                        direction = "Idle"
                    elif floor == 0:
                        direction = "Going Up"
                    elif floor == max_fl:
                        direction = "Going Down"
                    else:
                        direction = random.choice(["Going Up", "Going Down", "Idle"])

                    wait_sec = max(15, min(180, int(18 + abs(floor - (max_fl // 2)) * 7 + (load * 0.45) + random.randint(-4, 6))))
                    energy = round(random.uniform(0.08, 0.32) * (1 + load / 100), 2)
                    health = max(40, min(100, int(98 - random.uniform(0, 8))))

                    if load >= 85:
                        status = "High Load"
                        health = min(health, 82)
                    elif random.random() < 0.015:
                        status = "Temporary Delay"
                        health = min(health, 75)
                    elif random.random() < 0.005:
                        status = "Maintenance"
                        health = min(health, 55)
                    else:
                        status = "Operational"

                    records.append({
                        "Timestamp": ts,
                        "Block": block,
                        "Lift_ID": lift_id,
                        "Current_Floor": floor,
                        "Direction": direction,
                        "Passenger_Load_Percent": load,
                        "Est_Wait_Sec": wait_sec,
                        "Energy_kWh": energy,
                        "Health_Score": health,
                        "Operational_Status": status
                    })

    df = pd.DataFrame(records)
    df.to_csv(CSV_FILE, index=False)


def initialize_session():
    """Ensures in-memory session states are initialized with all 24 lifts on startup."""
    if "fleet" not in st.session_state or len(st.session_state["fleet"]) != 24:
        st.session_state["fleet"] = build_default_fleet()
    if "live_feed" not in st.session_state:
        st.session_state["live_feed"] = True
    if "time_window" not in st.session_state:
        st.session_state["time_window"] = "24H"
    if "selected_block" not in st.session_state:
        st.session_state["selected_block"] = "All Blocks"
    if "incident_log" not in st.session_state:
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state["incident_log"] = [
            {"time": now_str, "block": "Central Block", "lift": "Lift 2", "severity": "Warning", "msg": "High passenger capacity spike (88%) on Floor 5"},
            {"time": (datetime.datetime.now() - datetime.timedelta(minutes=4)).strftime("%H:%M:%S"), "block": "R&D Block", "lift": "Lift 4", "severity": "Info", "msg": "Scheduled optical sensor auto-calibration completed"},
            {"time": (datetime.datetime.now() - datetime.timedelta(minutes=11)).strftime("%H:%M:%S"), "block": "Block II", "lift": "Lift 2", "severity": "Warning", "msg": "Door clearance delay detected at Ground Floor (+18s)"},
            {"time": (datetime.datetime.now() - datetime.timedelta(minutes=24)).strftime("%H:%M:%S"), "block": "Main Auditorium", "lift": "Lift 1", "severity": "Info", "msg": "Auditorium dispersal dispatch profile activated"},
        ]


def simulate_tick():
    """Performs one 3-second simulation step for all 24 elevators and appends to CSV."""
    if "fleet" not in st.session_state or len(st.session_state["fleet"]) != 24:
        initialize_session()

    if not st.session_state.get("live_feed", True):
        return

    now_dt = datetime.datetime.now()
    now_ts = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    now_time = now_dt.strftime("%H:%M:%S")
    telemetry_batch = []

    for lift in st.session_state["fleet"]:
        cur_status = lift["Operational_Status"]
        cur_floor = int(lift["Current_Floor"])
        cur_dir = lift["Direction"]
        cur_load = int(lift["Passenger_Load_Percent"])
        cur_health = int(lift["Health_Score"])
        max_fl = int(lift.get("Max_Floor", get_max_floor(lift["Block"])))

        if cur_status == "Maintenance":
            if random.random() < 0.15:
                lift["Operational_Status"] = "Operational"
                lift["Direction"] = "Idle"
                lift["Health_Score"] = 92
            else:
                telemetry_batch.append(dict(lift, Timestamp=now_ts))
                continue

        if cur_dir == "Idle":
            if random.random() < 0.40:
                if cur_floor <= 0:
                    lift["Direction"] = "Going Up"
                elif cur_floor >= max_fl:
                    lift["Direction"] = "Going Down"
                else:
                    lift["Direction"] = random.choice(["Going Up", "Going Down"])
            lift["Passenger_Load_Percent"] = max(0, min(100, cur_load + random.randint(-15, 18)))
        else:
            step = random.choice([1, 1, 2])
            if cur_dir == "Going Up":
                next_fl = cur_floor + step
                if next_fl >= max_fl:
                    lift["Current_Floor"] = max_fl
                    lift["Direction"] = "Going Down"
                else:
                    lift["Current_Floor"] = next_fl
            elif cur_dir == "Going Down":
                next_fl = cur_floor - step
                if next_fl <= 0:
                    lift["Current_Floor"] = 0
                    lift["Direction"] = "Going Up"
                else:
                    lift["Current_Floor"] = next_fl

            if random.random() < 0.15:
                lift["Direction"] = "Idle"

            lift["Passenger_Load_Percent"] = max(0, min(100, cur_load + random.randint(-12, 15)))

        lift["Est_Wait_Sec"] = max(15, min(180, int(18 + abs(lift["Current_Floor"] - (max_fl // 2)) * 6 + (lift["Passenger_Load_Percent"] * 0.45) + random.randint(-3, 4))))
        lift["Energy_kWh"] = round(random.uniform(0.08, 0.32) * (1 + lift["Passenger_Load_Percent"] / 100), 2)

        if lift["Passenger_Load_Percent"] >= 85:
            lift["Operational_Status"] = "High Load"
            lift["Health_Score"] = max(60, cur_health - 2)
            if random.random() < 0.20:
                st.session_state["incident_log"].insert(0, {
                    "time": now_time,
                    "block": lift["Block"],
                    "lift": lift["Lift_ID"],
                    "severity": "Warning",
                    "msg": f"High Passenger Load ({lift['Passenger_Load_Percent']}%) on Floor {lift['Current_Floor']}"
                })
                st.session_state["incident_log"] = st.session_state["incident_log"][:20]
        elif random.random() < 0.015:
            lift["Operational_Status"] = "Temporary Delay"
            lift["Health_Score"] = max(55, cur_health - 5)
            st.session_state["incident_log"].insert(0, {
                "time": now_time,
                "block": lift["Block"],
                "lift": lift["Lift_ID"],
                "severity": "Warning",
                "msg": f"Door sensor cycle delay at Floor {lift['Current_Floor']}"
            })
            st.session_state["incident_log"] = st.session_state["incident_log"][:20]
        else:
            lift["Operational_Status"] = "Operational"
            lift["Health_Score"] = min(100, cur_health + 1)

        telemetry_batch.append(dict(lift, Timestamp=now_ts))

    new_df = pd.DataFrame(telemetry_batch)
    cols = ["Timestamp", "Block", "Lift_ID", "Current_Floor", "Direction", "Passenger_Load_Percent", "Est_Wait_Sec", "Energy_kWh", "Health_Score", "Operational_Status"]
    valid_cols = [c for c in cols if c in new_df.columns]
    new_df[valid_cols].to_csv(CSV_FILE, mode="a", header=not os.path.exists(CSV_FILE), index=False)


def trigger_fault(block, lift_id, fault_type):
    """VIVA Demonstration helper to inject a fault into a specific elevator."""
    if "fleet" not in st.session_state:
        initialize_session()
    now_time = datetime.datetime.now().strftime("%H:%M:%S")
    for lift in st.session_state["fleet"]:
        if lift["Block"] == block and lift["Lift_ID"] == lift_id:
            if fault_type == "Overload":
                lift["Passenger_Load_Percent"] = 96
                lift["Operational_Status"] = "High Load"
                lift["Health_Score"] = 72
                st.session_state["incident_log"].insert(0, {
                    "time": now_time,
                    "block": block,
                    "lift": lift_id,
                    "severity": "Critical",
                    "msg": f"Simulated Passenger Overload (96%) at Floor {lift['Current_Floor']}"
                })
            elif fault_type == "Door Fault":
                lift["Direction"] = "Idle"
                lift["Operational_Status"] = "Temporary Delay"
                lift["Health_Score"] = 65
                st.session_state["incident_log"].insert(0, {
                    "time": now_time,
                    "block": block,
                    "lift": lift_id,
                    "severity": "Warning",
                    "msg": f"Simulated Door Sensor Interruption at Floor {lift['Current_Floor']}"
                })
            elif fault_type == "Maintenance":
                lift["Direction"] = "Idle"
                lift["Operational_Status"] = "Maintenance"
                lift["Health_Score"] = 40
                st.session_state["incident_log"].insert(0, {
                    "time": now_time,
                    "block": block,
                    "lift": lift_id,
                    "severity": "Critical",
                    "msg": f"Simulated Emergency Maintenance Lock at Floor {lift['Current_Floor']}"
                })
            break


def restore_all_lifts():
    """Restores all 24 elevators to full operational readiness."""
    if "fleet" not in st.session_state:
        initialize_session()
    now_time = datetime.datetime.now().strftime("%H:%M:%S")
    for lift in st.session_state["fleet"]:
        lift["Operational_Status"] = "Operational"
        lift["Passenger_Load_Percent"] = random.randint(25, 60)
        lift["Health_Score"] = 98
        lift["Direction"] = random.choice(["Going Up", "Going Down", "Idle"])

    st.session_state["incident_log"].insert(0, {
        "time": now_time,
        "block": "All Blocks",
        "lift": "Fleet",
        "severity": "Info",
        "msg": "Manual Fleet System Restore triggered: All 24 elevators returned to Operational readiness"
    })
    st.session_state["incident_log"] = st.session_state["incident_log"][:20]
