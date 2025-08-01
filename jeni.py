import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------------ Configuration ------------------------ #
battery_types = {
    "Lithium-Ion": {"voltage": 3.7, "capacity": 2.5, "efficiency": 0.95},
    "Lead-Acid": {"voltage": 2.0, "capacity": 5.0, "efficiency": 0.85},
    "NiMH": {"voltage": 1.2, "capacity": 2.0, "efficiency": 0.75},
    "Solid-State": {"voltage": 3.8, "capacity": 3.0, "efficiency": 0.98},
}

# ------------------------ Sidebar Controls ------------------------ #
st.sidebar.title("🔋 Battery Configuration")
battery_type = st.sidebar.selectbox("Select Battery Type", list(battery_types.keys()))
series_cells = st.sidebar.slider("Number of Cells in Series", 1, 10, 3)
parallel_cells = st.sidebar.slider("Number of Cells in Parallel", 1, 5, 2)
sim_mode = st.sidebar.radio("Simulation Mode", ["Charging", "Discharging"])
simulation_time = st.sidebar.slider("Simulation Duration (seconds)", 10, 100, 60)
sim_speed = st.sidebar.slider("Simulation Speed (1x to 10x)", 1, 10, 1)

# ------------------------ Battery Parameters ------------------------ #
b_config = battery_types[battery_type]
total_voltage = b_config["voltage"] * series_cells
total_capacity = b_config["capacity"] * parallel_cells

def simulate_battery(sim_mode, duration, speed):
    time = np.arange(0, duration, 1)
    soc = []
    voltage = []
    current = []

    soc_val = 0 if sim_mode == "Charging" else 100

    for t in time:
        if sim_mode == "Charging":
            soc_val = min(100, soc_val + 100 / duration)
        else:
            soc_val = max(0, soc_val - 100 / duration)

        current_val = (total_capacity / duration) * (1 if sim_mode == "Charging" else -1)
        voltage_val = total_voltage * (soc_val / 100)

        soc.append(soc_val)
        current.append(current_val)
        voltage.append(voltage_val)

    return pd.DataFrame({"Time (s)": time, "SOC (%)": soc, "Current (A)": current, "Voltage (V)": voltage})

# ------------------------ Dashboard ------------------------ #
st.title("🔋 Battery Charging & Discharging Simulator")
st.markdown("""
This simulator allows you to visualize and control the charging or discharging behavior of different battery types 
with customizable series and parallel cell configurations.
""")

# Run Simulation
data = simulate_battery(sim_mode, simulation_time, sim_speed)

# Display Info Cards
st.subheader("📊 Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Battery Type", battery_type)
col2.metric("Voltage", f"{total_voltage:.2f} V")
col3.metric("Capacity", f"{total_capacity:.2f} Ah")
col4.metric("Efficiency", f"{b_config['efficiency'] * 100:.0f}%")

# ------------------------ Plotting ------------------------ #
st.subheader("📈 Live Graphs")

fig, ax = plt.subplots(3, 1, figsize=(10, 6))

ax[0].plot(data["Time (s)"], data["SOC (%)"], color="green")
ax[0].set_ylabel("SOC (%)")
ax[0].grid(True)

ax[1].plot(data["Time (s)"], data["Voltage (V)"], color="blue")
ax[1].set_ylabel("Voltage (V)")
ax[1].grid(True)

ax[2].plot(data["Time (s)"], data["Current (A)"], color="red")
ax[2].set_ylabel("Current (A)")
ax[2].set_xlabel("Time (s)")
ax[2].grid(True)

st.pyplot(fig)
