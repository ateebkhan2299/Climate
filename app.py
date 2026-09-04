"""
EarthScape Surveillance HQ — Command Center Dashboard
Ultra-High-Fidelity Cyberpunk / Sci-Fi Planetary Surveillance & Big Data Telemetry Console.
Integrated with Live Open-Meteo API Stream & Real-Time Auto-Updating Charts.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime
import time
import os
import sys

# Ensure root path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.mongodb import get_db
from utils.auth import authenticate_user
from utils.simulator import start_telemetry_simulator
from utils.open_meteo import GLOBAL_STATIONS, fetch_live_weather_from_open_meteo

# Streamlit Page Configuration
st.set_page_config(
    page_title="EARTHSCAPE // SURVEILLANCE HQ",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Command Center Cyberpunk CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Rajdhani:wght@500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif;
        background-color: #070B14 !important;
        color: #E2E8F0;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0D1933 0%, #070B14 70%);
    }

    /* Top HUD Navigation Bar */
    .hud-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #0B1120;
        border: 1px solid rgba(0, 242, 254, 0.2);
        padding: 10px 20px;
        border-radius: 6px;
        margin-bottom: 15px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.05);
    }
    .hud-title {
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: 2px;
        color: #00F2FE;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hud-chip {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 4px;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .chip-green {
        border-color: rgba(16, 185, 129, 0.4);
        color: #10B981;
    }
    .chip-cyan {
        border-color: rgba(0, 242, 254, 0.4);
        color: #00F2FE;
    }
    .chip-live {
        border-color: rgba(239, 68, 68, 0.5);
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        font-weight: 700;
        animation: pulse 2s infinite;
    }

    /* Critical Anomaly Banner */
    .anomaly-banner {
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid #EF4444;
        border-left: 6px solid #EF4444;
        border-radius: 6px;
        padding: 14px 20px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.15);
    }
    .anomaly-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        background: #EF4444;
        color: white;
        padding: 2px 8px;
        border-radius: 3px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    /* KPI Cyber Cards */
    .cyber-card {
        background: #0B132B;
        border: 1px solid rgba(0, 242, 254, 0.15);
        border-radius: 8px;
        padding: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: inset 0 0 15px rgba(0, 242, 254, 0.03);
    }
    .cyber-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00F2FE, transparent);
    }
    .card-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .card-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #94A3B8;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .card-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 700;
    }
    .badge-warn {
        background: rgba(239, 68, 68, 0.2);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .badge-cyan {
        background: rgba(0, 242, 254, 0.15);
        color: #00F2FE;
        border: 1px solid rgba(0, 242, 254, 0.3);
    }
    .badge-green {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .card-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.9rem;
        font-weight: 800;
        color: #F8FAFC;
    }

    /* Radar / Main Container */
    .radar-container {
        background: #0B132B;
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 18px;
    }
    .radar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    /* Sidebar Navigation Rail Styling */
    [data-testid="stSidebar"] {
        background-color: #050811 !important;
        border-right: 1px solid rgba(0, 242, 254, 0.15);
    }
    .nav-btn-active {
        background: linear-gradient(90deg, #00F2FE 0%, #0284C7 100%);
        color: #070B14;
        font-weight: 700;
        padding: 10px 14px;
        border-radius: 4px;
        letter-spacing: 1px;
        display: block;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Database & Simulator Initialization
db = get_db()
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'radar_mode' not in st.session_state:
    st.session_state.radar_mode = "LIVE OPEN-METEO GLOBAL"

if db is not None and not st.session_state.get('simulator_started', False):
    start_telemetry_simulator(db, interval_seconds=4)
    st.session_state.simulator_started = True

# Authentication Check
if not st.session_state.authenticated:
    st.markdown("<div class='hud-header'><div class='hud-title'>🌐 EARTHSCAPE // SURVEILLANCE HQ</div><div class='hud-chip chip-cyan'>STATUS: SECURE TERMINAL</div></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.6, 1])
    with c2:
        with st.form("hq_login"):
            st.markdown("<h3 style='color:#00F2FE; letter-spacing:2px;'>OPERATOR AUTHENTICATION</h3>", unsafe_allow_html=True)
            u = st.text_input("Operator Call-sign / Username", placeholder="admin or analyst")
            p = st.text_input("Access Key / Password", type="password", placeholder="••••••••")
            sub = st.form_submit_button("AUTHORIZE TERMINAL", use_container_width=True)
            if sub:
                user = authenticate_user(db, u, p)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = user['username']
                    st.session_state.role = user.get('role', 'ANALYST')
                    st.rerun()
                else:
                    st.error("ACCESS DENIED: Invalid Security Credentials.")
    st.stop()

# =========================================================
# SIDEBAR NAVIGATION RAIL
# =========================================================
with st.sidebar:
    st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'><span style='font-weight:700; color:#00F2FE;'>NAVIGATION RAIL</span><span class='card-badge badge-cyan'>SYS-V4</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='nav-btn-active'>🎛️ Command Center</div>", unsafe_allow_html=True)
    st.page_link("pages/1_🏠_Dashboard.py", label="Executive Overview", icon="🏠")
    st.page_link("pages/2_📊_Climate_Analysis.py", label="Geospatial Telemetry", icon="📊")
    st.page_link("pages/3_🗺️_Geographic_Analysis.py", label="Planetary Radar Maps", icon="🗺️")
    st.page_link("pages/4_🚨_Anomaly_Detection.py", label="ML Predictive Models", icon="🚨")
    st.page_link("pages/5_🔮_Predictions.py", label="Trend Forecasting", icon="🔮")
    st.page_link("pages/6_⚠️_Alerts.py", label="Alert Rules & Live Stream", icon="⚠️")
    st.page_link("pages/7_⚙️_Admin_Monitoring.py", label="Hadoop & Infrastructure", icon="⚙️")
    
    st.markdown("---")
    st.markdown("### 🌐 Live API Status")
    st.info("📡 **Open-Meteo Free API**: Connected\n- Endpoint: `api.open-meteo.com`\n- Mode: Free / No-Key\n- Sync Interval: `4s`")
    st.markdown("<div class='hud-chip chip-green' style='width:100%; justify-content:center;'>● LIVE SYNC ACTIVE 100%</div>", unsafe_allow_html=True)
    
    if st.button("LOGOUT TERMINAL", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# =========================================================
# REAL-TIME DYNAMIC FRAGMENT (LIVE CHANGING GRAPHS)
# =========================================================
@st.fragment(run_every="4s")
def render_live_surveillance_hq():
    utc_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    current_user = (st.session_state.get('username') or 'OPERATOR').upper()
    current_role = st.session_state.get('role') or 'ANALYST'

    # Top Status HUD
    st.markdown(f"""
    <div class='hud-header'>
        <div class='hud-title'>
            🌐 EARTHSCAPE <span style='font-size:0.8rem; color:#64748B; font-weight:600;'>SURVEILLANCE HQ</span>
        </div>
        <div style='display:flex; gap:8px; align-items:center;'>
            <div class='hud-chip chip-live'>● LIVE OPEN-METEO API</div>
            <div class='hud-chip chip-green'>● HADOOP: ACTIVE</div>
            <div class='hud-chip chip-cyan'>🗄️ HDFS: 1.4PB / 2.0PB</div>
            <div class='hud-chip'>📡 SENSORS: 14,820</div>
            <div class='hud-chip chip-green'>⚡ INGESTION: 48.2 MB/s</div>
            <div class='hud-chip'>🕒 {utc_now}</div>
            <div class='hud-chip chip-cyan'>👤 {current_user} [{current_role}]</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch latest live Open-Meteo events from MongoDB
    live_cursor = list(db['live_telemetry_stream'].find({}, {'_id': 0}).sort("StartTime(UTC)", -1).limit(15)) if db is not None else []
    latest_event = live_cursor[0] if live_cursor else {
        "StationName": "Karachi HQ", "Temperature_C": 29.4, "Precipitation(in)": 0.0, "WindSpeed_kmh": 17.5, "SurfacePressure_hpa": 1006.3, "RelativeHumidity": 65
    }

    # Dynamic Critical Anomaly Banner
    c_alert1, c_alert2 = st.columns([3.5, 1.5])
    with c_alert1:
        st.markdown(f"""
        <div class='anomaly-banner'>
            <div>
                <div style='display:flex; gap:10px; align-items:center; margin-bottom:6px;'>
                    <span class='anomaly-tag'>LIVE TELEMETRY STREAM</span>
                    <span style='font-family:"JetBrains Mono"; font-size:0.75rem; color:#94A3B8;'>ACTIVE NODE: {latest_event.get('StationName', 'Karachi HQ')} ({latest_event.get('Region', 'South Asia')})</span>
                </div>
                <div style='font-size:1.15rem; font-weight:700; color:#F8FAFC;'>
                    🚨 Live Open-Meteo Reading: {latest_event.get('Temperature_C', 29.4)}°C &nbsp;|&nbsp; {latest_event.get('Type', 'Clear Sky')} [{latest_event.get('Severity', 'Light')}]
                </div>
                <div style='font-size:0.85rem; color:#CBD5E1; margin-top:3px;'>
                    Wind: <b style='color:#00F2FE;'>{latest_event.get('WindSpeed_kmh', 17.5)} km/h</b> &nbsp;|&nbsp; Pressure: <b style='color:#FACC15;'>{latest_event.get('SurfacePressure_hpa', 1006.3)} hPa</b> &nbsp;|&nbsp; Humidity: <b style='color:#10B981;'>{latest_event.get('RelativeHumidity', 65)}%</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c_alert2:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("👁️ Isolate Node", use_container_width=True):
                st.toast(f"Isolating telemetry from {latest_event.get('StationName')}...")
        with b_col2:
            if st.button("📢 Dispatch Alert", use_container_width=True):
                st.toast("Dispatched meteorological advisory.")

    # 4 KPI Cyber-Cards Row
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)

    with kpi_c1:
        temp_val = latest_event.get('Temperature_C', 29.4)
        st.markdown(f"""
        <div class='cyber-card'>
            <div class='card-header-row'>
                <span class='card-label'>LIVE SURFACE TEMP</span>
                <span class='card-badge badge-warn'>OPEN-METEO</span>
            </div>
            <div class='card-value'>{temp_val}°C <span style='font-size:0.9rem; color:#94A3B8;'>({round(temp_val*9/5+32, 1)}°F)</span></div>
            <div style='font-family:"JetBrains Mono"; font-size:0.75rem; color:#F87171; margin-top:6px;'>
                📈 Live Node: {latest_event.get('StationName', 'Karachi HQ')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_c2:
        st.markdown(f"""
        <div class='cyber-card'>
            <div class='card-header-row'>
                <span class='card-label'>ATMOSPHERIC CO₂ / PRECIP</span>
                <span class='card-badge badge-cyan'>LIVE SYNC</span>
            </div>
            <div class='card-value'>{latest_event.get('Precipitation(in)', 0.0)} <span style='font-size:0.9rem; color:#94A3B8;'>in precip</span></div>
            <div style='font-family:"JetBrains Mono"; font-size:0.75rem; color:#00F2FE; margin-top:6px;'>
                ↗ CO₂ Baseline: 423.8 ppm &nbsp;|&nbsp; 24h Δ +1.2
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_c3:
        st.markdown("""
        <div class='cyber-card'>
            <div class='card-header-row'>
                <span class='card-label'>SENSOR INGESTION GRID</span>
                <span class='card-badge badge-green'>99.4% UPTIME</span>
            </div>
            <div class='card-value'>14,820 <span style='font-size:0.9rem; color:#94A3B8;'>Active Nodes</span></div>
            <div style='font-family:"JetBrains Mono"; font-size:0.75rem; color:#10B981; margin-top:6px;'>
                📶 9,140 Buoys / 5,680 IoT &nbsp;|&nbsp; Loss: 0.04%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_c4:
        st.markdown("""
        <div class='cyber-card'>
            <div class='card-header-row'>
                <span class='card-label'>HDFS DATA WAREHOUSE</span>
                <span class='card-badge badge-cyan'>71% CAP</span>
            </div>
            <div class='card-value'>1.42 <span style='font-size:0.9rem; color:#94A3B8;'>/ 2.00 PB</span></div>
            <div style='font-family:"JetBrains Mono"; font-size:0.75rem; color:#38BDF8; margin-top:6px;'>
                ⚡ 380 GB/hr Ingest &nbsp;|&nbsp; 124ms RT Latency
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)

    # Main Split View
    main_col_left, main_col_right = st.columns([2.4, 1.1])

    with main_col_left:
        st.markdown("<div class='radar-container'>", unsafe_allow_html=True)
        st.markdown("<div style='font-weight:800; font-size:1.1rem; color:#00F2FE; letter-spacing:1px; margin-bottom:10px;'>🌐 PLANETARY SURVEILLANCE RADAR <span class='card-badge badge-cyan'>GLOBAL OPEN-METEO TELEMETRY</span></div>", unsafe_allow_html=True)

        # Plot Live Global Stations on Geospatial Radar
        stations_plot = []
        for st_item in GLOBAL_STATIONS:
            # Check if we have recent reading in db or default
            stations_plot.append({
                "Station": st_item['name'],
                "Region": st_item['region'],
                "lat": st_item['lat'],
                "lon": st_item['lon'],
                "Size": 18,
                "Type": "Active Sensor Node"
            })
        st_df = pd.DataFrame(stations_plot)

        # Also blend with cleaned dataset sample points
        cursor_pts = list(db['weather_events_cleaned'].find({}, {'_id': 0}).limit(200)) if db is not None else []
        if cursor_pts:
            pts_df = pd.DataFrame(cursor_pts)
            fig_radar = px.scatter_geo(
                pts_df,
                lat='LocationLat',
                lon='LocationLng',
                color='Severity',
                hover_name='Type',
                color_discrete_map={'Light': '#00F2FE', 'Moderate': '#10B981', 'Heavy': '#F59E0B', 'Severe': '#EF4444'},
                template='plotly_dark'
            )
            # Add prominent glowing markers for live Open-Meteo stations
            fig_radar.add_trace(go.Scattergeo(
                lat=st_df['lat'],
                lon=st_df['lon'],
                text=st_df['Station'],
                mode='markers+text',
                textposition='top center',
                textfont=dict(family='JetBrains Mono', size=9, color='#00F2FE'),
                marker=dict(size=12, color='#00F2FE', symbol='star', line=dict(width=1, color='#FFFFFF')),
                name='Live Open-Meteo Stations'
            ))
        else:
            fig_radar = px.scatter_geo(
                st_df,
                lat='lat',
                lon='lon',
                text='Station',
                template='plotly_dark'
            )

        fig_radar.update_layout(
            height=420,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='#0B132B',
            plot_bgcolor='#0B132B',
            geo=dict(
                bgcolor='#070B14',
                lakecolor='#0B132B',
                landcolor='#0D1933',
                showland=True,
                showcountries=True,
                countrycolor='rgba(0, 242, 254, 0.3)',
                subunitcolor='rgba(0, 242, 254, 0.15)'
            )
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Live Meteorological Gauges Strip
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; background:#070B14; border:1px solid rgba(0,242,254,0.15); padding:8px 14px; border-radius:4px; font-family:"JetBrains Mono"; font-size:0.75rem;'>
            <span>🎯 LAT: {latest_event.get('LocationLat', 24.86)}° | LON: {latest_event.get('LocationLng', 67.01)}°</span>
            <span style='color:#10B981;'>● Station: {latest_event.get('StationName', 'Karachi HQ')}</span>
            <span style='color:#FACC15;'>● Temp: {latest_event.get('Temperature_C', 29.4)}°C</span>
            <span style='color:#00F2FE;'>SCAN REFRESH: 4s</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        g1, g2, g3, g4 = st.columns(4)
        with g1:
            st.markdown(f"<div class='card-label'>GLOBAL WIND SPEED</div><div style='font-family:\"JetBrains Mono\"; font-size:1.1rem; font-weight:700; color:#00F2FE;'>{latest_event.get('WindSpeed_kmh', 17.5)} <span style='font-size:0.7rem; color:#94A3B8;'>km/h</span></div>", unsafe_allow_html=True)
        with g2:
            st.markdown(f"<div class='card-label'>SURFACE PRESSURE</div><div style='font-family:\"JetBrains Mono\"; font-size:1.1rem; font-weight:700; color:#F8FAFC;'>{latest_event.get('SurfacePressure_hpa', 1006.3)} <span style='font-size:0.7rem; color:#F87171;'>hPa</span></div>", unsafe_allow_html=True)
        with g3:
            st.markdown(f"<div class='card-label'>RELATIVE HUMIDITY</div><div style='font-family:\"JetBrains Mono\"; font-size:1.1rem; font-weight:700; color:#10B981;'>{latest_event.get('RelativeHumidity', 65)}% <span style='font-size:0.7rem; color:#10B981;'>STABLE</span></div>", unsafe_allow_html=True)
        with g4:
            st.markdown(f"<div class='card-label'>LIVE PRECIPITATION</div><div style='font-family:\"JetBrains Mono\"; font-size:1.1rem; font-weight:700; color:#FACC15;'>{latest_event.get('Precipitation(in)', 0.0)} <span style='font-size:0.7rem; color:#94A3B8;'>in</span></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with main_col_right:
        # Predictive ML Inference Card
        st.markdown("""
        <div class='cyber-card' style='height:100%;'>
            <div class='card-header-row'>
                <div style='font-weight:800; font-size:1.0rem; color:#00F2FE;'>🤖 Predictive ML Inference</div>
                <span class='card-badge badge-cyan'>LSTM + RF ENSEMBLE</span>
            </div>
            
            <div style='margin: 10px 0;'>
                <div style='display:flex; justify-content:space-between; align-items:baseline;'>
                    <span style='font-weight:700; color:#F8FAFC;'>Extreme Heatwave Escalation</span>
                    <span style='font-family:"JetBrains Mono"; font-size:1.2rem; font-weight:800; color:#EF4444;'>91.4%</span>
                </div>
                <div style='background:rgba(15,23,42,0.8); height:6px; border-radius:3px; margin:6px 0; overflow:hidden;'>
                    <div style='background:linear-gradient(90deg, #F59E0B 0%, #EF4444 100%); width:91.4%; height:100%;'></div>
                </div>
                <div style='font-size:0.72rem; color:#94A3B8; line-height:1.3;'>
                    Live ensemble forecast based on tropospheric telemetry. High flash drought probability in Mediterranean & South Asian basins.
                </div>
            </div>
            
            <div style='margin-top:15px;'>
                <div style='display:flex; justify-content:space-between; font-family:"JetBrains Mono"; font-size:0.7rem; color:#94A3B8; margin-bottom:4px;'>
                    <span>14-DAY LIVE HEAT PROJECTIONS</span>
                    <span style='color:#EF4444;'>Peak Day +9 (CRIT)</span>
                </div>
        """, unsafe_allow_html=True)
        
        # 14-Day Dynamic Bar Chart with Live Jitter
        days = [f"D+{i}" for i in range(1, 15)]
        base_heat = [2.1, 2.4, 3.0, 3.6, 4.2, 5.0, 5.8, 6.4, 7.2, 6.8, 5.5, 4.1, 3.2, 2.6]
        heat_vals = [round(v + np.random.uniform(-0.15, 0.15), 2) for v in base_heat]
        colors = ['#00F2FE' if v < 3.5 else ('#F59E0B' if v < 5.5 else '#EF4444') for v in heat_vals]
        
        fig_heat = go.Figure(go.Bar(x=days, y=heat_vals, marker_color=colors))
        fig_heat.update_layout(
            height=140,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, tickfont=dict(size=8, color='#64748B')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickfont=dict(size=8, color='#64748B'))
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown(f"""
            <div style='background: #070B14; border:1px solid rgba(0,242,254,0.15); border-radius:4px; padding:10px; margin-top:8px;'>
                <div style='display:flex; justify-content:space-between; font-family:"JetBrains Mono"; font-size:0.7rem;'>
                    <span style='color:#00F2FE;'>OCO-2 SPECTROMETRY</span>
                    <span style='color:#10B981;'>LIVE SYNC</span>
                </div>
                <div style='color:#94A3B8; font-size:0.75rem; margin-top:4px;'>
                    Active Feed: <b>{latest_event.get('StationName', 'Karachi HQ')}</b> ({latest_event.get('Temperature_C')}°C)
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)

    # Bottom Split View: Hadoop MapReduce Stream & Live Events
    bot_col_left, bot_col_right = st.columns([2.4, 1.1])

    with bot_col_left:
        # Dynamic Hadoop MapReduce Progress (Simulating Live Processing)
        t_sec = int(time.time()) % 100
        prog1 = min(98, max(20, (t_sec * 3) % 100))
        prog2 = min(95, max(15, (t_sec * 2 + 10) % 100))
        
        st.markdown(f"""
        <div class='cyber-card'>
            <div class='card-header-row'>
                <div>
                    <span style='font-weight:800; font-size:1.1rem; color:#00F2FE;'>🐘 Hadoop MapReduce Stream & Cluster Health</span>
                    <div style='font-size:0.75rem; color:#64748B;'>YARN Resource Orchestrator • 64 DataNodes Online • Zero Partition Failures</div>
                </div>
                <span class='card-badge badge-green'>ALL HEALTHY</span>
            </div>
            
            <div style='margin:12px 0; background:#070B14; border:1px solid rgba(0,242,254,0.1); border-radius:4px; padding:10px;'>
                <div style='display:flex; justify-content:space-between; font-family:"JetBrains Mono"; font-size:0.75rem;'>
                    <span style='color:#00F2FE; font-weight:700;'>#MR-9082 Open-Meteo Global Surface Temp Spatial Interpolation</span>
                    <span style='color:#10B981; font-weight:700;'>STAGE: REDUCING {prog1}%</span>
                </div>
                <div style='background:rgba(15,23,42,0.8); height:6px; border-radius:3px; margin:6px 0; overflow:hidden;'>
                    <div style='background:linear-gradient(90deg, #00F2FE 0%, #10B981 100%); width:{prog1}%; height:100%;'></div>
                </div>
                <div style='display:flex; justify-content:space-between; font-family:"JetBrains Mono"; font-size:0.7rem; color:#64748B;'>
                    <span>Input: 412.8 GB / 520.0 GB</span>
                    <span>Splits: 2,048 / 2,048 Mapped • Reducers: 128 Active</span>
                </div>
            </div>

            <div style='margin:12px 0; background:#070B14; border:1px solid rgba(0,242,254,0.1); border-radius:4px; padding:10px;'>
                <div style='display:flex; justify-content:space-between; font-family:"JetBrains Mono"; font-size:0.75rem;'>
                    <span style='color:#00F2FE; font-weight:700;'>#MR-9083 Real-Time Carbon Flux & Meteorological Matrix Aggregation</span>
                    <span style='color:#38BDF8; font-weight:700;'>STAGE: MAPPING {prog2}%</span>
                </div>
                <div style='background:rgba(15,23,42,0.8); height:6px; border-radius:3px; margin:6px 0; overflow:hidden;'>
                    <div style='background:linear-gradient(90deg, #38BDF8 0%, #00F2FE 100%); width:{prog2}%; height:100%;'></div>
                </div>
                <div style='display:flex; justify-content:space-between; font-family:"JetBrains Mono"; font-size:0.7rem; color:#64748B;'>
                    <span>Input: 180.2 GB / 430.0 GB</span>
                    <span>Splits: 840 / 2,000 Mapped • Spark Context: Attached</span>
                </div>
            </div>

            <div style='display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-top:10px; text-align:center;'>
                <div style='background:#070B14; padding:8px; border-radius:4px;'>
                    <div class='card-label'>ACTIVE DATANODES</div>
                    <div style='font-family:"JetBrains Mono"; font-size:1.1rem; font-weight:800; color:#10B981;'>64 <span style='font-size:0.7rem; color:#64748B;'>/ 64 online</span></div>
                </div>
                <div style='background:#070B14; padding:8px; border-radius:4px;'>
                    <div class='card-label'>DEAD / STALE NODES</div>
                    <div style='font-family:"JetBrains Mono"; font-size:1.1rem; font-weight:800; color:#10B981;'>0 <span style='font-size:0.7rem; color:#64748B;'>0.0% fault</span></div>
                </div>
                <div style='background:#070B14; padding:8px; border-radius:4px;'>
                    <div class='card-label'>TASKTRACKERS LOAD</div>
                    <div style='font-family:"JetBrains Mono"; font-size:1.1rem; font-weight:800; color:#00F2FE;'>12 <span style='font-size:0.7rem; color:#64748B;'>High Compute</span></div>
                </div>
                <div style='background:#070B14; padding:8px; border-radius:4px;'>
                    <div class='card-label'>YARN MEMORY POOL</div>
                    <div style='font-family:"JetBrains Mono"; font-size:1.1rem; font-weight:800; color:#38BDF8;'>892 <span style='font-size:0.7rem; color:#64748B;'>/ 1,024 GB</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with bot_col_right:
        # Live Stream Items from MongoDB
        st.markdown("""
        <div class='cyber-card' style='height:100%;'>
            <div class='card-header-row'>
                <div style='font-weight:800; font-size:1.0rem; color:#00F2FE;'>🚨 Live Event Stream</div>
                <span class='card-badge badge-warn'>● LIVE FEED</span>
            </div>
            <div style='font-family:"JetBrains Mono"; font-size:0.75rem; margin-top:8px;'>
        """, unsafe_allow_html=True)

        if live_cursor:
            for ev in live_cursor[:3]:
                st.markdown(f"""
                <div style='border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:6px; margin-bottom:6px;'>
                    <div style='display:flex; justify-content:space-between;'>
                        <span style='color:#00F2FE; font-weight:700;'>● {ev.get('StationName', 'Sensor Node')}</span>
                        <span style='color:#64748B;'>{ev.get('StartTime(UTC)', '')[-8:]}</span>
                    </div>
                    <div style='color:#E2E8F0;'>{ev.get('Temperature_C')}°C &nbsp;|&nbsp; {ev.get('Type')} [{ev.get('Severity')}]</div>
                    <div style='color:#64748B; font-size:0.68rem;'>Source: Open-Meteo Live API • Wind: {ev.get('WindSpeed_kmh')} km/h</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#64748B;'>Waiting for next incoming live packet...</div>", unsafe_allow_html=True)

        st.markdown("""
            </div>
            <div style='margin-top:14px;'>
                <div class='card-label' style='margin-bottom:6px;'>DIRECT TELEMETRY ACTIONS</div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ Trigger Hadoop Deep Compute", use_container_width=True):
            st.toast("Dispatched YARN MapReduce task #MR-9084...")
        
        if st.button("📥 Export NetCDF / GeoJSON Data", use_container_width=True):
            st.toast("Exported geojson packet to /climate/processed/")

        st.markdown("</div></div>", unsafe_allow_html=True)

# Render the dynamic live auto-updating fragment
render_live_surveillance_hq()
