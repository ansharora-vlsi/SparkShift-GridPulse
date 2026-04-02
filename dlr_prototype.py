import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time

# --- Page Config ---
st.set_page_config(page_title="L&T Grid-Pulse | DLR Digital Twin", layout="wide")

st.title("⚡ L&T Grid-Pulse: Dynamic Line Rating (DLR) Optimizer")
st.markdown("### *Transforming Passive Infrastructure into AI-Active Assets*")

# --- Sidebar: Technical Specs (Showcases your L&T knowledge) ---
st.sidebar.header("📡 Live Sensor Feeds (Simulated)")
line_id = st.sidebar.selectbox("Select Transmission Line", ["Line 400kV Delhi-Agra", "Line 765kV Wardha-Aurangabad"])
conductor_type = st.sidebar.selectbox("Conductor Type", ["ACSR (Standard)", "ACCC (L&T Preferred HTLS)"])

st.sidebar.divider()
st.sidebar.subheader("Environmental Parameters")
amb_temp = st.sidebar.slider("Ambient Temperature (°C)", 10, 50, 38)
wind_speed = st.sidebar.slider("Wind Speed (m/s)", 0.5, 15.0, 2.2)
solar_rad = st.sidebar.slider("Solar Radiation (W/m²)", 0, 1000, 800)

# --- Logic: Simplified IEEE 738 Heat Balance ---
# Heat Gain (I^2R + Solar) = Heat Loss (Convective + Radiative)
def calculate_metrics(I, temp, wind, solar, cond_type):
    # Resistance changes with temperature
    base_r = 0.07 if cond_type == "ACSR (Standard)" else 0.045
    r_t = base_r * (1 + 0.004 * (temp - 20))
    
    # Simple convective cooling model (DLR Core)
    cooling = 1 + (wind * 0.15)
    
    # Ampacity (How much current can we safely handle?)
    # Limit is usually based on max conductor temp (75°C for ACSR, 180°C for ACCC)
    max_temp = 75 if cond_type == "ACSR (Standard)" else 150
    static_limit = 800 # Amps
    
    # DLR Calculation
    dlr_limit = static_limit * (cooling * (max_temp/temp)**0.5)
    
    # Losses
    static_loss = (I**2 * r_t) / 1000
    dlr_loss = (I**2 * (r_t/cooling)) / 1000
    
    return dlr_limit, static_loss, dlr_loss

# --- Main Dashboard Layout ---
col1, col2, col3 = st.columns(3)

# Current Load Simulation
load_amps = 950 # Overloading the static limit to show the DLR advantage

dlr_cap, s_loss, d_loss = calculate_metrics(load_amps, amb_temp, wind_speed, solar_rad, conductor_type)

with col1:
    st.metric("Safe Static Capacity", "800 Amps", border=True)
with col2:
    st.metric("Dynamic (DLR) Capacity", f"{int(dlr_cap)} Amps", f"+{int(dlr_cap-800)} Amps Gain", delta_color="normal", border=True)
with col3:
    st.metric("Loss Reduction Potential", f"{((s_loss - d_loss)/s_loss * 100):.1f}%", "- Optimized", border=True)

# --- Visualization: The "Money Shot" for the video ---
st.subheader("Real-Time Capacity vs. Load Analysis")

# Generate simulated time-series data
t_data = pd.DataFrame({
    'Time': pd.date_range(datetime.now(), periods=20, freq='h'),
    'Static_Limit': [800] * 20,
    'DLR_Limit': [dlr_cap + np.random.randint(-50, 50) for _ in range(20)],
    'Actual_Load': [load_amps + np.random.randint(-30, 30) for _ in range(20)]
})

fig = go.Figure()
fig.add_trace(go.Scatter(x=t_data['Time'], y=t_data['Static_Limit'], name="Static Rating (Standard)", line=dict(color='red', dash='dash')))
fig.add_trace(go.Scatter(x=t_data['Time'], y=t_data['DLR_Limit'], name="DLR Rating (AI-Optimized)", fill='tonexty', line=dict(color='green')))
fig.add_trace(go.Scatter(x=t_data['Time'], y=t_data['Actual_Load'], name="Actual Power Flow", line=dict(color='white', width=4)))

fig.update_layout(template="plotly_dark", xaxis_title="Time", yaxis_title="Current (Amps)", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("""
### 🚀 The L&T Edge:
1. **Prevent Asset Aging:** Stop over-insulating conductors based on 'worst-case' weather.
2. **Instant Capacity:** Unlock 20-30% extra grid capacity without building new towers.
3. **Digital Twin Integration:** This prototype can be integrated into L&T's existing SCADA systems.
""")
