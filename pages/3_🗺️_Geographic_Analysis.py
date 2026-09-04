"""
Page 3: Geographic Analysis
Interactive geospatial maps using Plotly & Folium with coordinate clustering, severity heatmaps, and event drill-downs.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb import get_db

st.set_page_config(page_title="Geographic Analysis | EarthScape", page_icon="🗺️", layout="wide")

if not st.session_state.get('authenticated', False):
    st.warning("Please sign in from the main portal.")
    st.stop()

db = get_db()
if db is None:
    st.error("Cannot connect to MongoDB.")
    st.stop()

st.title("🗺️ Interactive Geospatial Climate Map")
st.markdown("Geographic mapping of telemetry events across the contiguous United States with severity indicators and precipitation intensities.")

# Sidebar Map Filters
st.sidebar.markdown("### 🗺️ Map Controls")
all_states = sorted(db['weather_events_cleaned'].distinct('State'))
selected_state = st.sidebar.selectbox("Filter by State", ["All States"] + [s for s in all_states if s != "Unknown"])
selected_type = st.sidebar.selectbox("Filter by Weather Type", ["All Types", "Rain", "Snow", "Fog", "Cold", "Storm", "Precipitation", "Hail"])
max_points = st.sidebar.slider("Number of Points to Render", min_value=500, max_value=5000, value=2500, step=500)

query = {}
if selected_state != "All States":
    query['State'] = selected_state
if selected_type != "All Types":
    query['Type'] = selected_type

cursor = db['weather_events_cleaned'].find(query, {'_id': 0}).limit(max_points)
map_data = list(cursor)

if not map_data:
    st.warning("No events match your current filter parameters.")
    st.stop()

map_df = pd.DataFrame(map_data)

# Summary Info Bar
c1, c2, c3 = st.columns(3)
with c1:
    st.info(f"📍 **Displayed Points**: {len(map_df):,} events")
with c2:
    severe_pts = (map_df['Severity'].isin(['Severe', 'Heavy'])).sum()
    st.warning(f"⚠️ **Severe Events**: {severe_pts:,}")
with c3:
    anom_pts = (map_df.get('is_anomaly', 1) == -1).sum()
    st.error(f"🚨 **Anomalous Events**: {anom_pts:,}")

# Interactive Geospatial Map (Plotly Mapbox / Geo Scatter)
fig_map = px.scatter_geo(
    map_df,
    lat='LocationLat',
    lon='LocationLng',
    color='Severity',
    size='Precipitation(in)',
    hover_name='Type',
    hover_data=['City', 'State', 'Severity', 'Precipitation(in)', 'DurationHours'],
    color_discrete_map={'Light': '#38BDF8', 'Moderate': '#FACC15', 'Heavy': '#FB923C', 'Severe': '#EF4444'},
    scope='usa',
    title="Geographic Weather Event Scatter (Interactive)",
    template='plotly_white'
)
fig_map.update_layout(height=650, margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig_map, use_container_width=True)

# Granular Table Viewer
with st.expander("🔍 View Tabular Telemetry of Displayed Points"):
    st.dataframe(
        map_df[['EventId', 'Type', 'Severity', 'City', 'State', 'LocationLat', 'LocationLng', 'Precipitation(in)', 'DurationHours']].head(100),
        use_container_width=True
    )
