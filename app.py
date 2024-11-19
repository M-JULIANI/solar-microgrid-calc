import streamlit as st
import pandas as pd

def calculate_microgrid_size(
    daily_kwh_usage,
    peak_kw_demand,
    backup_hours=24,
    solar_peak_hours=5,
    battery_depth_of_discharge=0.8,
    system_losses=0.15,
    safety_factor=1.2
):
    """Calculate recommended microgrid components size based on business energy needs."""
    # Account for system losses
    adjusted_daily_usage = daily_kwh_usage * (1 + system_losses)
    adjusted_peak_demand = peak_kw_demand * (1 + system_losses)
    
    # Calculate battery storage needs
    required_battery_capacity = (
        (adjusted_daily_usage * backup_hours / 24)
        / battery_depth_of_discharge
        * safety_factor
    )
    
    # Calculate solar PV array size
    required_solar_capacity = (
        adjusted_daily_usage / solar_peak_hours
        * safety_factor
    )
    
    # Calculate inverter size based on peak demand
    required_inverter_size = adjusted_peak_demand * safety_factor
    
    return {
        "battery_capacity_kwh": round(required_battery_capacity, 1),
        "solar_capacity_kw": round(required_solar_capacity, 1),
        "inverter_size_kw": round(required_inverter_size, 1)
    }

# Example business profiles
EXAMPLE_PROFILES = {
    "Small Retail Store": {"daily_kwh": 50, "peak_kw": 8},
    "Restaurant": {"daily_kwh": 200, "peak_kw": 25},
    "Small Office": {"daily_kwh": 75, "peak_kw": 12},
    "Custom": {"daily_kwh": 100, "peak_kw": 15}
}

# Streamlit app
st.set_page_config(page_title="Microgrid Size Calculator", page_icon="☀️")

st.title("Solar Microgrid Size Calculator")
st.write("Calculate recommended sizes for your microgrid components based on your energy needs.")

# Sidebar for advanced parameters
with st.sidebar:
    st.header("Advanced Settings")
    backup_hours = st.slider("Backup Hours", 12, 72, 24, help="How many hours of battery backup needed")
    solar_peak_hours = st.slider("Solar Peak Hours", 3.0, 7.0, 5.0, 0.5, help="Average daily peak sun hours")
    battery_dod = st.slider("Battery Depth of Discharge", 0.5, 0.9, 0.8, 0.1, help="Maximum battery discharge depth")
    system_losses = st.slider("System Losses", 0.1, 0.3, 0.15, 0.05, help="Expected system losses")
    safety_factor = st.slider("Safety Factor", 1.1, 1.5, 1.2, 0.1, help="Additional capacity buffer")

# Main input section
col1, col2 = st.columns(2)
with col1:
    business_type = st.selectbox("Select Business Type", list(EXAMPLE_PROFILES.keys()))

# If custom is selected, show input fields
if business_type == "Custom":
    with col2:
        daily_kwh = st.number_input("Daily Energy Usage (kWh)", 
                                   min_value=1.0, 
                                   value=100.0, 
                                   help="Average daily energy consumption")
        peak_kw = st.number_input("Peak Power Demand (kW)", 
                                 min_value=0.5, 
                                 value=15.0, 
                                 help="Maximum power demand")
else:
    daily_kwh = EXAMPLE_PROFILES[business_type]["daily_kwh"]
    peak_kw = EXAMPLE_PROFILES[business_type]["peak_kw"]
    st.write(f"Daily Usage: {daily_kwh} kWh")
    st.write(f"Peak Demand: {peak_kw} kW")

# Calculate and display results
if st.button("Calculate Microgrid Size"):
    results = calculate_microgrid_size(
        daily_kwh_usage=daily_kwh,
        peak_kw_demand=peak_kw,
        backup_hours=backup_hours,
        solar_peak_hours=solar_peak_hours,
        battery_depth_of_discharge=battery_dod,
        system_losses=system_losses,
        safety_factor=safety_factor
    )
    
    # Display results in cards
    st.subheader("Recommended System Sizes")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Battery Storage",
            value=f"{results['battery_capacity_kwh']} kWh"
        )
    
    with col2:
        st.metric(
            label="Solar PV Array",
            value=f"{results['solar_capacity_kw']} kW"
        )
    
    with col3:
        st.metric(
            label="Inverter Size",
            value=f"{results['inverter_size_kw']} kW"
        )
    
    # Display results explanation
    st.info("""
    💡 **What these results mean:**
    - **Battery Storage**: Total energy storage capacity needed for your backup duration
    - **Solar PV Array**: Solar panel system size needed to generate your daily energy usage
    - **Inverter Size**: Power rating needed to handle your peak demand
    """)
    
    # Create a DataFrame for the detailed breakdown
    details = pd.DataFrame({
        'Parameter': ['Daily Energy Usage', 'Peak Power Demand', 'Backup Duration', 
                     'Solar Peak Hours', 'Battery Depth of Discharge', 'System Losses', 
                     'Safety Factor'],
        'Value': [f"{daily_kwh} kWh", f"{peak_kw} kW", f"{backup_hours} hours",
                 f"{solar_peak_hours} hours", f"{battery_dod*100}%", 
                 f"{system_losses*100}%", f"{safety_factor}x"]
    })
    
    st.subheader("Calculation Details")
    st.dataframe(details, hide_index=True)