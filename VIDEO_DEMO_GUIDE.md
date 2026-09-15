# 🎥 EarthScape Video Demo Guide

This document outlines the step-by-step workflow for recording a professional project demo video of the EarthScape Climate Agency platform. The goal is to highlight the full-stack architecture, Big Data pipelines, Machine Learning anomaly detection, and the newly implemented GSAP animated dashboard.

---

## 🎬 Prerequisites
1. Ensure MongoDB is running locally.
2. Ensure you have run `python database/seed_db.py`.
3. Ensure you have run `python ml/train_models.py` so the database is fully seeded with ~500k records.
4. Launch the application with `python app.py`.
5. Open your browser to `http://localhost:5000` in Full-Screen mode.
6. Use a screen recording tool (e.g. OBS Studio, Loom).

---

## 📽️ Scene 1: Command Center & Real-Time Animations
* **Action:** Start on the Command Center (`/`).
* **Talking Points:** 
  * "Welcome to the EarthScape Climate Agency dashboard, built with Flask and Python."
  * Highlight the real-time observation feed streaming telemetry data.
  * Point out the fluid GSAP animations as KPI cards and graphs stagger into view.
  * Toggle the Dark/Light theme button to showcase the dynamic CSS variable-based styling.

## 📽️ Scene 2: Geospatial Telemetry & Data Trends
* **Action:** Navigate to Geospatial Telemetry (`/analytics`) via the sidebar.
* **Talking Points:**
  * Show the Heatmap grid mapping event types across months.
  * Mention that the data is queried directly from a MongoDB collection holding processed Big Data outputs.
  * Emphasize the "No Mock Data" rule: everything you see reflects actual aggregations.

## 📽️ Scene 3: ML Anomaly Detection (Isolation Forest)
* **Action:** Navigate to ML Anomaly Detection (`/anomalies`).
* **Talking Points:**
  * "Here we track statistical outliers flagged by an unsupervised Isolation Forest model trained on 500,000 historical records."
  * Highlight the KPI cards showing Contamination Rate (4.0%) and Critical Severity counts.
  * Show the interactive Plotly charts updating based on real DB values.
  * Scroll through the Live Anomaly Detection Log table to show individual anomaly event records.

## 📽️ Scene 4: Predictive Forecasting (Random Forest)
* **Action:** Navigate to Predictive Forecasting (`/predictions`).
* **Talking Points:**
  * "This section showcases our Random Forest regression model predicting weather trajectory distances."
  * Note the Model Error Metrics (R², MAE, RMSE).
  * Show the actual vs predicted trajectory time series graph and the Feature Importances chart.
  * Scroll through the prediction log.

## 📽️ Scene 5: Hadoop Admin & Cluster Health
* **Action:** Navigate to Hadoop Admin (`/admin`).
* **Talking Points:**
  * "EarthScape integrates with underlying infrastructure for data processing."
  * Point out the live telemetry for CPU, RAM, and Disk polling `psutil` metrics.
  * Demonstrate the Hadoop MapReduce job trigger feature (using the 'Trigger Master Node MapReduce Job' button).
  * Conclude the demo by showing the live system logs and overall cluster stability.
