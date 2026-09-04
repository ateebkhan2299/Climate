"""
Page 6: Climate Alert Management System
Live feed of automated weather warnings, ML anomaly detections, and severe climate risk alerts with status acknowledge toggles.
"""
import streamlit as st
import pandas as pd
import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb import get_db
from utils.alerts import evaluate_and_generate_alerts

st.set_page_config(page_title="Alerts | EarthScape", page_icon="⚠️", layout="wide")

if not st.session_state.get('authenticated', False):
    st.warning("Please sign in from the main portal.")
    st.stop()

db = get_db()
if db is None:
    st.error("Cannot connect to MongoDB.")
    st.stop()

st.title("⚠️ Automated Climate Alert System")
st.markdown("Automated notifications triggered by **Severe Weather Events**, **High Precipitation**, and **Machine Learning Anomalies**.")

# Fetch Active Alerts
alert_docs = list(db['alerts'].find({}, {'_id': 0}).sort("timestamp", -1).limit(100))
alert_df = pd.DataFrame(alert_docs) if alert_docs else pd.DataFrame()

# Alert KPI Summary
col1, col2, col3, col4 = st.columns(4)
with col1:
    unread_cnt = len(alert_df[alert_df['status'] == 'Unread']) if not alert_df.empty and 'status' in alert_df.columns else 0
    st.metric("🚨 Active Unread", unread_cnt)
with col2:
    ack_cnt = len(alert_df[alert_df['status'] == 'Acknowledged']) if not alert_df.empty and 'status' in alert_df.columns else 0
    st.metric("👁️ Acknowledged", ack_cnt)
with col3:
    resolved_cnt = len(alert_df[alert_df['status'] == 'Resolved']) if not alert_df.empty and 'status' in alert_df.columns else 0
    st.metric("✅ Resolved", resolved_cnt)
with col4:
    severe_alert_cnt = len(alert_df[alert_df['alert_type'] == 'Severe Weather Alert']) if not alert_df.empty and 'alert_type' in alert_df.columns else 0
    st.metric("⛈️ Severe Alerts", severe_alert_cnt)

st.markdown("---")

# Filter Controls
st.sidebar.markdown("### 🔔 Alert Filters")
status_filter = st.sidebar.selectbox("Filter by Status", ["All", "Unread", "Acknowledged", "Resolved"])
type_filter = st.sidebar.selectbox("Filter by Alert Type", ["All Types", "Severe Weather Alert", "Extreme Precipitation Warning", "ML Climate Anomaly"])

filtered_df = alert_df.copy()
if not filtered_df.empty:
    if status_filter != "All" and 'status' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if type_filter != "All Types" and 'alert_type' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['alert_type'] == type_filter]

# Render Alert Cards
st.subheader("📋 Real-Time Alert Telemetry Feed")
if filtered_df.empty:
    st.info("No alerts matching current filters.")
else:
    for idx, row in filtered_df.head(20).iterrows():
        status_val = row.get('status', 'Unread')
        badge_bg = '#EF4444' if status_val == 'Unread' else ('#F59E0B' if status_val == 'Acknowledged' else '#10B981')
        
        with st.container():
            c_msg, c_badge, c_action = st.columns([3.5, 1, 1.2])
            with c_msg:
                st.markdown(f"**[{row.get('alert_type', 'Alert')}]** `{row.get('state', 'US')}` — {row.get('message', '')}")
                st.caption(f"🕒 Timestamp: {row.get('timestamp', 'N/A')} | Source: {row.get('source', 'System Engine')}")
            with c_badge:
                st.markdown(f"<span style='background-color: {badge_bg}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: 600;'>{status_val}</span>", unsafe_allow_html=True)
            with c_action:
                if status_val == 'Unread':
                    if st.button("Acknowledge", key=f"ack_{idx}"):
                        db['alerts'].update_one({"message": row.get('message'), "timestamp": row.get('timestamp')}, {"$set": {"status": "Acknowledged"}})
                        st.rerun()
                elif status_val == 'Acknowledged':
                    if st.button("Resolve", key=f"res_{idx}"):
                        db['alerts'].update_one({"message": row.get('message'), "timestamp": row.get('timestamp')}, {"$set": {"status": "Resolved"}})
                        st.rerun()
            st.markdown("---")

# Manual Alert Test Generator
with st.expander("🛠️ Manual Alert Generator (Testing & Simulation)"):
    st.markdown("Manually inject an alert into the MongoDB system to test notification pipelines.")
    test_state = st.selectbox("State", ["TX", "CA", "FL", "NY", "IL", "OH", "NC"], key="test_state")
    test_type = st.selectbox("Event Type", ["Storm", "Rain", "Snow", "Cold", "Fog"], key="test_type")
    test_sev = st.selectbox("Severity", ["Severe", "Heavy", "Moderate", "Light"], key="test_sev")
    test_precip = st.number_input("Precipitation (in)", min_value=0.0, max_value=15.0, value=3.2, step=0.5)

    if st.button("🚨 Broadcast Test Alert"):
        mock_event = {
            "EventId": f"MANUAL-{int(datetime.datetime.now(datetime.timezone.utc).timestamp())}",
            "Type": test_type,
            "Severity": test_sev,
            "State": test_state,
            "Precipitation(in)": test_precip,
            "StartTime(UTC)": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source": "MANUAL SIMULATION INJECTION",
            "is_anomaly": -1 if test_precip > 2.0 else 1
        }
        new_alerts = evaluate_and_generate_alerts(mock_event)
        if new_alerts:
            db['alerts'].insert_many(new_alerts)
            st.success(f"Generated and broadcasted {len(new_alerts)} alert(s) to MongoDB!")
            st.rerun()
        else:
            st.info("Event parameters did not cross alert threshold.")
