import streamlit as st
import pandas as pd
import time
import smu_utils
from gui_logic import MeasurementLogic
import plotly.express as px
import serial.tools.list_ports

# Custom Style
st.set_page_config(page_title="GU Lab Sheet Resistance", page_icon="⚡", layout="wide")

# Initialize Session State
if 'data' not in st.session_state:
    st.session_state['data'] = []
    
logic = MeasurementLogic()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/laboratory.png", width=60)
    st.title("Settings")
    
    # 1. Connection
    st.header("Connection")
    
    # Dynamic Port List
    ports = serial.tools.list_ports.comports()
    port_list = [p.device for p in ports]
    # Add defaults if missing
    if "/dev/ttyACM0" not in port_list: port_list.append("/dev/ttyACM0")
    if "/dev/ttyUSB0" not in port_list: port_list.append("/dev/ttyUSB0")
    
    selected_port = st.selectbox("Select Port", port_list, index=0 if port_list else None)
    
    if st.button("Refresh Ports"):
        st.rerun()

    st.divider()

    # 2. Geometry
    st.header("Geometry")
    geom_type = st.selectbox("Sample Shape", ["Rectangular", "Circular"])
    
    if geom_type == "Rectangular":
        length = st.number_input("Length (mm)", value=60.0)
        width = st.number_input("Width (mm)", value=60.0)
        diameter = 0.0
    else:
        length = 0.0
        width = 0.0
        diameter = st.number_input("Diameter (mm)", value=14.0)
        
    thickness = st.number_input("Thickness (μm)", value=0.0, format="%.3f")

    st.divider()
    
    # 3. Advanced Settings
    with st.expander("Advanced Settings", expanded=False):
        spacing = st.number_input("Probe Spacing (mm)", value=1.270, format="%.3f")
        samples = st.selectbox("Samples per Point", [64, 256, 1024, 4096, 8192], index=4)
        
        polarity_txt = st.selectbox("Polarity", ["Positive", "Negative"])
        polarity = 1.0 if polarity_txt == "Positive" else -1.0
        
        v_limit = st.number_input("Voltage Limit (V)", value=10.50)
        i_limit_ma = st.number_input("Current Limit (mA)", value=220.00)
        
        drive_v = st.number_input("Drive Voltage (V)", value=0.50)

# --- MAIN AREA ---
st.title("GU Lab Sheet Resistance Lite")
st.markdown("*Web Interface Edition*")

# Control Row
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    measure_btn = st.button("🔴 MEASURE", type="primary", use_container_width=True)

with col2:
    if st.button("Clear Data", use_container_width=True):
        st.session_state['data'] = []
        st.rerun()

# MEASUREMENT LOGIC
if measure_btn:
    status = st.status(f"Connecting to {selected_port}...", expanded=True)
    try:
        # 1. Connect
        device = smu_utils.get_session(selected_port)
        if not device:
            status.error("Failed to connect.")
            st.stop()
            
        status.write("Configuring SMU...")
        # 2. Configure
        device.smu1.set.enabled(True, response=0)
        device.smu1.set.limitv(v_limit, response=0)
        device.smu1.set.limiti(i_limit_ma * 1e-3, response=0)
        device.smu1.set.filter(samples, response=0)
        device.vsense1.set.enabled(True, response=0)
        device.vsense1.set.filter(samples, response=0)
        
        # 3. Measure
        target_v = drive_v * polarity
        status.write(f"Sourcing {target_v} V...")
        device.smu1.set.voltage(target_v, response=0)
        time.sleep(0.5) # Settling time
        
        status.write("Reading sensors...")
        v_data = device.vsense1.measure()
        smu_data = device.smu1.measure()
        
        # 4. Cleanup
        device.smu1.set.voltage(0, response=0)
        device.smu1.set.enabled(False, response=0)
        device.vsense1.set.enabled(False, response=0)
        device.close()
        status.update(label="Measurement Complete", state="complete", expanded=False)
        
        # 5. Parse
        import numpy as np
        v_inner = 0.0
        i_outer = 0.0
        v_outer = 0.0
        
        if v_data is not None:
             arr = np.array(v_data).flatten()
             if len(arr) > 0: v_inner = float(arr[0])
             
        if smu_data is not None:
             arr = np.array(smu_data).flatten()
             if len(arr) >= 2:
                 v_outer = float(arr[0])
                 i_outer = float(arr[1])
                 
        # 6. Calculate
        metrics = logic.calculate_metrics(
            v_inner, i_outer, geom_type, thickness,
            length=length, width=width, diameter=diameter, spacing=spacing
        )
        
        # 7. Store
        timestamp = time.strftime("%H:%M:%S")
        record = {
            "Time": timestamp,
            "Current (A)": i_outer,
            "Voltage (V)": v_inner,
            "Sheet Res (Ω/sq)": metrics["sheet_resistance"],
            "Resistivity (Ω.m)": metrics["resistivity"],
            "Conductivity (S/m)": metrics["conductivity"]
        }
        st.session_state['data'].insert(0, record) # Prepend
        
    except Exception as e:
        status.update(label="Error", state="error")
        st.error(f"Measurement Failed: {e}")

# --- DISPLAY ---

# Metrics (Latest)
if st.session_state['data']:
    latest = st.session_state['data'][0]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Sheet Resistance", f"{latest['Sheet Res (Ω/sq)']:.3f} Ω/sq")
    m2.metric("Resistivity", f"{latest['Resistivity (Ω.m)']*1e6:.2f} μΩ.m") # Display as uOhm for readability? Or follow GUI
    # Using format from GUI: 0.00 Ohm.m
    m2.metric("Resistivity", f"{latest['Resistivity (Ω.m)']:.4f} Ω.m")
    m3.metric("Conductivity", f"{latest['Conductivity (S/m)']:.4f} S/m")
    
    st.divider()
    
    # Charts & Table
    tab1, tab2 = st.tabs(["📊 Charts", "📄 Data"])
    
    df = pd.DataFrame(st.session_state['data'])
    
    with tab1:
        # Plot Sheet Res over time
        fig = px.line(df, x="Time", y="Sheet Res (Ω/sq)", title="Sheet Resistance Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.dataframe(df, use_container_width=True)
        
        # Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download CSV",
            csv,
            "measurement_web.csv",
            "text/csv",
            key='download-csv'
        )

else:
    st.info("Click 'MEASURE' to start.")
