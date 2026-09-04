"""
Page 4: Anomaly Detection
Isolation Forest machine learning metrics, anomaly timelines, geospatial anomaly distributions, and granular score inspection.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb import get_db

st.set_page_config(page_title="Anomaly Detection | EarthScape", page_icon="🚨", layout="wide")

if not st.session_state.get('authenticated', False):
    st.warning("Please sign in from the main portal.")
    st.stop()

db = get_db()
if db is None:
    st.error("Cannot connect to MongoDB.")
    st.stop()

st.title("🚨 Machine Learning Anomaly Detection")
st.markdown("Unsupervised detection of multidimensional climate anomalies using **Scikit-learn Isolation Forest**.")

# Fetch Anomalies from MongoDB
anom_docs = list(db['anomalies'].find({}, {'_id': 0}).limit(3000))
summary_doc = db['climate_summary'].find_one() or {}
kpis = summary_doc.get('kpis', {})

if not anom_docs:
    st.warning("No anomalies found in database. Run the pipeline first.")
    st.stop()

anom_df = pd.DataFrame(anom_docs)

# KPI Cards for Anomalies
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total ML Anomalies", f"{kpis.get('total_anomalies', len(anom_df)):,}")
with c2:
    st.metric("Anomaly Rate", f"{kpis.get('anomaly_percentage', 4.0)}%")
with c3:
    top_anom_state = anom_df['State'].value_counts().index[0] if not anom_df.empty else "N/A"
    st.metric("Highest Anomaly State", top_anom_state)
with c4:
    top_anom_type = anom_df['Type'].value_counts().index[0] if not anom_df.empty else "N/A"
    st.metric("Most Common Anomaly Type", top_anom_type)

st.markdown("---")

# Visualizations: Anomaly Timeline, Top States, and Anomaly by Event Type
col1, col2 = st.columns([1.3, 1])

with col1:
    st.subheader("📅 Anomaly Timeline (Monthly Distribution)")
    anom_time = anom_df.groupby(['Year', 'Month']).size().reset_index(name='AnomalyCount')
    anom_time['DateLabel'] = anom_time['Year'].astype(str) + '-' + anom_time['Month'].astype(str).str.zfill(2)
    anom_time.sort_values(by=['Year', 'Month'], inplace=True)
    
    fig_anom_time = px.line(
        anom_time,
        x='DateLabel',
        y='AnomalyCount',
        markers=True,
        color_discrete_sequence=['#DC2626'],
        template='plotly_white'
    )
    fig_anom_time.update_layout(height=350, xaxis_title="Year-Month", yaxis_title="Anomalies Detected")
    st.plotly_chart(fig_anom_time, use_container_width=True)

with col2:
    st.subheader("📍 Top 10 Anomalous States")
    state_anom_counts = anom_df['State'].value_counts().head(10).reset_index()
    state_anom_counts.columns = ['State', 'Count']
    
    fig_anom_states = px.bar(
        state_anom_counts,
        x='State',
        y='Count',
        color='Count',
        color_continuous_scale='Reds',
        template='plotly_white'
    )
    fig_anom_states.update_layout(height=350)
    st.plotly_chart(fig_anom_states, use_container_width=True)

# Additional Row: Anomalies by Event Type & Severity
col3, col4 = st.columns([1, 1])
with col3:
    st.subheader("📊 Anomalies by Weather Event Type")
    type_anom_counts = anom_df['Type'].value_counts().reset_index()
    type_anom_counts.columns = ['Event Type', 'Count']
    fig_anom_type = px.bar(
        type_anom_counts,
        x='Count',
        y='Event Type',
        orientation='h',
        color='Count',
        color_continuous_scale='Magma',
        template='plotly_white'
    )
    fig_anom_type.update_layout(height=320, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_anom_type, use_container_width=True)

with col4:
    st.subheader("🎯 Anomaly Score Distribution")
    fig_score_dist = px.histogram(
        anom_df,
        x='anomaly_score',
        nbins=30,
        color_discrete_sequence=['#EF4444'],
        template='plotly_white'
    )
    fig_score_dist.update_layout(height=320, xaxis_title="Decision Score (Lower = More Anomalous)")
    st.plotly_chart(fig_score_dist, use_container_width=True)

st.markdown("---")

# Geospatial Anomaly Map
st.subheader("🗺️ Geographic Scatter of Detected Anomalies")
fig_anom_map = px.scatter_geo(
    anom_df.head(1500),
    lat='LocationLat',
    lon='LocationLng',
    color='anomaly_score',
    size='Precipitation(in)',
    hover_name='Type',
    hover_data=['State', 'City', 'Severity', 'Precipitation(in)', 'anomaly_score'],
    color_continuous_scale='Turbo',
    scope='usa',
    template='plotly_white'
)
fig_anom_map.update_layout(height=550, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig_anom_map, use_container_width=True)

# Granular Anomaly Table
st.subheader("📋 Granular Anomaly Telemetry Inspector")
st.dataframe(
    anom_df[['EventId', 'Type', 'Severity', 'State', 'City', 'Precipitation(in)', 'DurationHours', 'anomaly_score', 'StartTime(UTC)']].head(200),
    use_container_width=True
)
