import streamlit as st
import pandas as pd
import numpy as np
import matplotliv.pyplot as plt

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
    """
    Simulate battery charging/discharging behavior
    
    Args:
        sim_mode (str): "Charging" or "Discharging"
        duration (int): Simulation duration in seconds
        speed (int): Simulation speed multiplier (currently not implemented)
    
    Returns:
        pd.DataFrame: Simulation results with Time, SOC, Current, and Voltage
    """
    # Create time array with proper step size
    time_step = 1.0  # seconds
    time = np.arange(0, duration + time_step, time_step)
    
    # Initialize arrays
    soc = []
    voltage = []
    current = []
    
    # Set initial SOC based on mode
    soc_val = 0 if sim_mode == "Charging" else 100
    
    # Calculate current based on C-rate (1C = full capacity in 1 hour)
    # For realistic simulation, use a reasonable C-rate
    c_rate = 0.5  # 0.5C rate (2 hours for full charge/discharge)
    base_current = total_capacity * c_rate
    
    for t in time:
        # Update SOC based on current and time
        if sim_mode == "Charging":
            # SOC increases during charging
            delta_soc = (base_current * time_step / 3600) / total_capacity * 100  # 3600 converts seconds to hours
            soc_val = min(100, soc_val + delta_soc)
            current_val = base_current if soc_val < 100 else 0  # Stop charging at 100%
        else:  # Discharging
            # SOC decreases during discharging
            delta_soc = (base_current * time_step / 3600) / total_capacity * 100
            soc_val = max(0, soc_val - delta_soc)
            current_val = -base_current if soc_val > 0 else 0  # Stop discharging at 0%
        
        # Calculate voltage based on SOC (more realistic voltage curve)
        if sim_mode == "Charging":
            # Voltage increases non-linearly during charging
            voltage_factor = 0.85 + 0.15 * (soc_val / 100) ** 0.5
        else:
            # Voltage decreases during discharging
            voltage_factor = 0.75 + 0.25 * (soc_val / 100)
        
        voltage_val = total_voltage * voltage_factor
        
        # Store values
        soc.append(soc_val)
        current.append(current_val)
        voltage.append(voltage_val)
    
    return pd.DataFrame({
        "Time (s)": time, 
        "SOC (%)": soc, 
        "Current (A)": current, 
        "Voltage (V)": voltage
    })

# ------------------------ Dashboard ------------------------ #
st.title("🔋 Battery Charging & Discharging Simulator")
st.markdown("""
This simulator allows you to visualize and control the charging or discharging behavior of different battery types 
with customizable series and parallel cell configurations.
""")

# Run Simulation
try:
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
    
    # Create the plots with better styling
    fig, ax = plt.subplots(3, 1, figsize=(12, 10))
    
    # SOC plot
    ax[0].plot(data["Time (s)"], data["SOC (%)"], color="green", linewidth=2, label="SOC")
    ax[0].set_ylabel("SOC (%)", fontsize=12)
    ax[0].set_title(f"State of Charge - {sim_mode} Mode", fontsize=14)
    ax[0].grid(True, alpha=0.3)
    ax[0].set_ylim(0, 105)
    
    # Voltage plot
    ax[1].plot(data["Time (s)"], data["Voltage (V)"], color="blue", linewidth=2, label="Voltage")
    ax[1].set_ylabel("Voltage (V)", fontsize=12)
    ax[1].set_title("Battery Voltage", fontsize=14)
    ax[1].grid(True, alpha=0.3)
    
    # Current plot
    ax[2].plot(data["Time (s)"], data["Current (A)"], color="red", linewidth=2, label="Current")
    ax[2].set_ylabel("Current (A)", fontsize=12)
    ax[2].set_xlabel("Time (s)", fontsize=12)
    ax[2].set_title("Battery Current", fontsize=14)
    ax[2].grid(True, alpha=0.3)
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Display the plot
    st.pyplot(fig)
    
    # Add summary statistics
    st.subheader("📈 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    final_soc = data["SOC (%)"].iloc[-1]
    initial_soc = data["SOC (%)"].iloc[0]
    max_voltage = data["Voltage (V)"].max()
    min_voltage = data["Voltage (V)"].min()
    
    col1.metric("Initial SOC", f"{initial_soc:.1f}%")
    col2.metric("Final SOC", f"{final_soc:.1f}%", f"{final_soc - initial_soc:.1f}%")
    col3.metric("Max Voltage", f"{max_voltage:.2f} V")
    col4.metric("Min Voltage", f"{min_voltage:.2f} V")
    
    # Display data table (optional)
    if st.checkbox("Show Raw Data"):
        st.subheader("📊 Simulation Data")
        st.dataframe(data.round(3))

except Exception as e:
    st.error(f"An error occurred during simulation: {str(e)}")
    st.info("Please check your input parameters and try again.")
