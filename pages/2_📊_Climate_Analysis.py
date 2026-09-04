"""
Page 2: Climate Analysis
Deep exploratory analysis: Monthly seasonality, Precipitation vs Severity, Duration distributions, and Correlation Heatmaps.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb import get_db

st.set_page_config(page_title="Climate Analysis | EarthScape", page_icon="📊", layout="wide")

if not st.session_state.get('authenticated', False):
    st.warning("Please sign in from the main portal.")
    st.stop()

db = get_db()
if db is None:
    st.error("Cannot connect to MongoDB.")
    st.stop()

st.title("📊 Deep Climate & Statistical Analysis")
st.markdown("Multi-variable exploratory analysis examining precipitation, event durations, temporal patterns, and feature correlations.")

# Fetch Cleaned Sample for Granular Distribution Analysis
sample_docs = list(db['weather_events_cleaned'].find({}, {'_id': 0}).limit(10000))
if not sample_docs:
    st.warning("No sample events found in database.")
    st.stop()

df = pd.DataFrame(sample_docs)

# Section 1: Monthly Event Seasonality Matrix
st.subheader("🗓️ Monthly Event Distribution by Weather Type")
month_type_ct = pd.crosstab(df['Month'], df['Type'])
fig_heatmap = px.imshow(
    month_type_ct.T,
    labels=dict(x="Month (1-12)", y="Weather Type", color="Events Count"),
    color_continuous_scale="Magma",
    aspect="auto",
    template="plotly_white"
)
fig_heatmap.update_layout(height=400)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# Section 2: Precipitation and Duration Boxplots
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌧️ Precipitation (in) Across Severity Levels")
    fig_box_precip = px.box(
        df,
        x="Severity",
        y="Precipitation(in)",
        color="Severity",
        points=False,
        color_discrete_map={'Light': '#38BDF8', 'Moderate': '#FACC15', 'Heavy': '#FB923C', 'Severe': '#F87171'},
        template="plotly_white"
    )
    fig_box_precip.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_box_precip, use_container_width=True)

with col2:
    st.subheader("⏱️ Event Duration (Hours) Distribution")
    # Clip duration for readable histogram
    df['Duration_Capped'] = df['DurationHours'].clip(upper=48)
    fig_hist_duration = px.histogram(
        df,
        x="Duration_Capped",
        nbins=40,
        color="Type",
        template="plotly_white"
    )
    fig_hist_duration.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20), xaxis_title="Duration in Hours (Capped at 48h)")
    st.plotly_chart(fig_hist_duration, use_container_width=True)

st.markdown("---")

# Section 3: Correlation Heatmap
st.subheader("🔥 Feature Correlation Matrix")
num_cols = ['LocationLat', 'LocationLng', 'Precipitation(in)', 'DurationHours', 'SeverityScore', 'Month', 'Year']
valid_num_cols = [c for c in num_cols if c in df.columns]
corr_df = df[valid_num_cols].corr()

fig_corr = px.imshow(
    corr_df,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    template="plotly_white"
)
fig_corr.update_layout(height=450)
st.plotly_chart(fig_corr, use_container_width=True)
