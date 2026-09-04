"""
Page 1: Main Dashboard
Displays global KPIs, interactive trend charts, event distributions, and multi-variable filters.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb import get_db

st.set_page_config(page_title="Main Dashboard | EarthScape", page_icon="🏠", layout="wide")

if not st.session_state.get('authenticated', False):
    st.warning("Please sign in from the main portal.")
    st.stop()

db = get_db()
if db is None:
    st.error("Cannot connect to MongoDB.")
    st.stop()

# Retrieve precalculated climate summary
summary_doc = db['climate_summary'].find_one() or {}
kpis = summary_doc.get('kpis', {})
yearly_data = pd.DataFrame(summary_doc.get('yearly_summary', []))
monthly_data = pd.DataFrame(summary_doc.get('monthly_summary', []))
state_data = pd.DataFrame(summary_doc.get('state_summary', []))
type_data = pd.DataFrame(summary_doc.get('type_summary', []))
sev_data = pd.DataFrame(summary_doc.get('severity_summary', []))
seasonal_data = pd.DataFrame(summary_doc.get('seasonal_summary', []))

st.title("🏠 EarthScape Executive Climate Dashboard")
st.markdown("Real-time telemetry and aggregated insights across millions of historical and live weather events.")

# Top KPI Summary Cards
st.markdown("### 📌 Key Performance Indicators")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Events", f"{kpis.get('total_events', 0):,}")
with col2:
    st.metric("Severe Events", f"{kpis.get('total_severe_events', 0):,}")
with col3:
    st.metric("ML Anomalies", f"{kpis.get('total_anomalies', 0):,}")
with col4:
    st.metric("Anomaly Rate", f"{kpis.get('anomaly_percentage', 0)}%")
with col5:
    st.metric("Top State", str(kpis.get('most_affected_state', 'N/A')))
with col6:
    st.metric("Avg Precip (in)", f"{kpis.get('average_precipitation', 0.0)}")

st.markdown("---")

# Interactive Global Filters
st.sidebar.markdown("### 🔍 Global Filters")
selected_severity = st.sidebar.multiselect("Severity Levels", ["Light", "Moderate", "Heavy", "Severe"], default=["Light", "Moderate", "Heavy", "Severe"])
selected_season = st.sidebar.multiselect("Seasons", ["Winter", "Spring", "Summer", "Fall"], default=["Winter", "Spring", "Summer", "Fall"])

# Main Chart Grid
row1_col1, row1_col2 = st.columns([1.5, 1])

with row1_col1:
    st.subheader("📈 Yearly Weather Event Trend (2016 - 2022)")
    if not yearly_data.empty:
        # Melt yearly data for plotly
        id_vars = ['Year']
        val_vars = [c for c in yearly_data.columns if c != 'Year']
        yearly_melted = pd.melt(yearly_data, id_vars=id_vars, value_vars=val_vars, var_name='Severity', value_name='Count')
        yearly_filtered = yearly_melted[yearly_melted['Severity'].isin(selected_severity)]
        
        fig_yearly = px.bar(
            yearly_filtered, 
            x='Year', 
            y='Count', 
            color='Severity',
            barmode='stack',
            color_discrete_map={'Light': '#38BDF8', 'Moderate': '#FACC15', 'Heavy': '#FB923C', 'Severe': '#F87171'},
            template='plotly_white'
        )
        fig_yearly.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_yearly, use_container_width=True)
    else:
        st.info("No yearly data available.")

with row1_col2:
    st.subheader("🥧 Event Severity Breakdown")
    if not sev_data.empty:
        filtered_sev = sev_data[sev_data['Severity'].isin(selected_severity)]
        fig_pie = px.pie(
            filtered_sev,
            names='Severity',
            values='Count',
            color='Severity',
            color_discrete_map={'Light': '#38BDF8', 'Moderate': '#FACC15', 'Heavy': '#FB923C', 'Severe': '#F87171'},
            hole=0.4,
            template='plotly_white'
        )
        fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No severity data available.")

st.markdown("---")

row2_col1, row2_col2 = st.columns([1.2, 1.2])

with row2_col1:
    st.subheader("📍 Top 10 States with Highest Weather Activity")
    if not state_data.empty:
        top_10 = state_data.head(10)
        fig_state = px.bar(
            top_10,
            x='State',
            y='TotalEvents',
            color='SevereEvents',
            color_continuous_scale='Reds',
            labels={'TotalEvents': 'Total Events', 'SevereEvents': 'Severe Events'},
            template='plotly_white'
        )
        fig_state.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_state, use_container_width=True)
    else:
        st.info("No state data available.")

with row2_col2:
    st.subheader("📊 Weather Event Type Frequency")
    if not type_data.empty:
        fig_type = px.bar(
            type_data,
            x='Count',
            y='Type',
            orientation='h',
            color='Count',
            color_continuous_scale='Viridis',
            template='plotly_white'
        )
        fig_type.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20), yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_type, use_container_width=True)
    else:
        st.info("No event type data available.")
