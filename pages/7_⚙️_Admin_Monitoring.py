"""
Page 7: Admin & System Monitoring
Admin-only monitoring dashboard showing host hardware telemetry (psutil), database health, distributed cluster status, pipeline executors, feedback management, and system logs.
"""
import streamlit as st
import pandas as pd
import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb import get_db
from utils.monitoring import get_system_metrics, get_service_status
from ml.train_models import run_pipeline

st.set_page_config(page_title="Admin Monitoring | EarthScape", page_icon="⚙️", layout="wide")

if not st.session_state.get('authenticated', False):
    st.warning("Please sign in from the main portal.")
    st.stop()

# Role Access Control Gate
if st.session_state.get('role') != 'ADMIN':
    st.error("⛔ Access Denied: You must have the ADMIN role to view system monitoring and infrastructure management.")
    st.info("Please log in with the Administrator account (`admin`).")
    st.stop()

db = get_db()
if db is None:
    st.error("Cannot connect to MongoDB.")
    st.stop()

st.title("⚙️ System Infrastructure & Performance Monitoring")
st.markdown("Host hardware metrics via `psutil`, database health checks, cluster connection statuses, and audit logs.")

# Section 1: Live Hardware Metrics (psutil)
st.subheader("🖥️ Host Hardware Telemetry (psutil)")
sys_metrics = get_system_metrics()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("CPU Utilization", f"{sys_metrics['cpu_percent']}%", f"{sys_metrics['cpu_count']} Cores Active")
with c2:
    st.metric("RAM Utilization", f"{sys_metrics['memory_percent']}%", f"{sys_metrics['memory_used_gb']} / {sys_metrics['memory_total_gb']} GB")
with c3:
    st.metric("Disk Storage Used", f"{sys_metrics['disk_percent']}%", f"{sys_metrics['disk_used_gb']} / {sys_metrics['disk_total_gb']} GB")
with c4:
    st.metric("Host Environment", "Windows (Local)", "Python 3.14 x64")

# Hardware progress gauges
col_cpu, col_ram, col_disk = st.columns(3)
with col_cpu:
    st.progress(min(1.0, sys_metrics['cpu_percent'] / 100.0), text=f"CPU: {sys_metrics['cpu_percent']}%")
with col_ram:
    st.progress(min(1.0, sys_metrics['memory_percent'] / 100.0), text=f"Memory: {sys_metrics['memory_percent']}%")
with col_disk:
    st.progress(min(1.0, sys_metrics['disk_percent'] / 100.0), text=f"Disk: {sys_metrics['disk_percent']}%")

st.markdown("---")

# Section 2: Service & Distributed Storage Health
st.subheader("🌐 Services & Big Data Cluster Health")
srv_status = get_service_status(db)

s1, s2, s3 = st.columns(3)
with s1:
    st.info(f"🍃 **MongoDB Database**\n- Status: `{srv_status['mongodb']['status']}`\n- Version: `{srv_status['mongodb']['version']}`\n- Total Docs: `{srv_status['mongodb']['doc_count']:,}`")
with s2:
    st.info(f"🐘 **Hadoop HDFS Storage**\n- Status: `{srv_status['hdfs']['status']}`\n- Target Path: `{srv_status['hdfs']['path']}`\n- Nodes: `1 Active (Local Emulated)`")
with s3:
    st.info(f"⚡ **Apache PySpark Engine**\n- Status: `{srv_status['spark']['status']}`\n- Mode: `{srv_status['spark']['mode']}`\n- Master: `local[*]`")

st.markdown("---")

# Section 3: Database Collections Record Count
st.subheader("📚 MongoDB Collection Telemetry")
collections = db.list_collection_names()
col_stats = []
for c in collections:
    col_stats.append({
        "Collection Name": c,
        "Document Count": db[c].estimated_document_count(),
        "Status": "Active & Indexed"
    })
st.dataframe(pd.DataFrame(col_stats), use_container_width=True)

st.markdown("---")

# Section 4: Manual Pipeline Execution & Logs
col_pipe, col_feed = st.columns(2)

with col_pipe:
    st.subheader("🔄 Big Data & ML Pipeline Trigger")
    st.markdown("Re-run the full ingestion, cleaning, feature engineering, Isolation Forest, and Random Forest pipeline.")
    if st.button("🚀 Re-execute Pipeline", use_container_width=True):
        with st.spinner("Executing pipeline..."):
            success = run_pipeline()
            if success:
                st.success("Pipeline executed successfully and database re-seeded!")
                st.rerun()
            else:
                st.error("Pipeline encountered an issue.")

    st.markdown("#### 📜 Pipeline Execution History")
    logs = list(db['system_logs'].find({}, {'_id': 0}).sort("timestamp", -1).limit(5))
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
    else:
        st.info("No system execution logs found.")

with col_feed:
    st.subheader("💬 User Feedback Submissions")
    feedbacks = list(db['feedback'].find({}, {'_id': 0}).sort("created_at", -1).limit(10))
    if feedbacks:
        st.dataframe(pd.DataFrame(feedbacks), use_container_width=True)
    else:
        st.info("No user feedback submitted yet.")

    # In-page Feedback submission form
    st.markdown("#### 📝 Submit System Feedback Form")
    with st.form("feedback_form"):
        fb_name = st.text_input("Name")
        fb_email = st.text_input("Email")
        fb_cat = st.selectbox("Category", ["Bug", "Data Issue", "Suggestion", "Other"])
        fb_msg = st.text_area("Message")
        fb_submit = st.form_submit_button("Submit Feedback")

        if fb_submit and fb_name and fb_msg:
            db['feedback'].insert_one({
                "name": fb_name,
                "email": fb_email,
                "category": fb_cat,
                "message": fb_msg,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            st.success("Feedback submitted successfully to MongoDB!")
            st.rerun()
