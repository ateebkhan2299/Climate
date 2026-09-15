# 🌍 EarthScape Climate Agency — Big Data, Machine Learning & Climate Analytics Platform

**EarthScape Climate Agency** is an end-to-end Python-native Big Data analytics, machine learning, and interactive dashboard platform designed for large-scale climate and weather event intelligence.

---

## 🛠️ Technology Stack

| Domain | Technology / Library |
| :--- | :--- |
| **Data Ingestion & Cleaning** | Pandas, NumPy |
| **Big Data Processing** | Apache PySpark 4.2 |
| **Distributed Storage** | Apache Hadoop HDFS (`/climate/raw/`, `/climate/processed/`, `/climate/ml/`) |
| **MapReduce** | Hadoop Streaming Python (`mapper.py`, `reducer.py`) |
| **Database** | MongoDB v8.2 + PyMongo |
| **Machine Learning** | Scikit-learn (Isolation Forest Anomaly Detection, Random Forest Regressor) |
| **Interactive Dashboard** | Flask, HTML5, Vanilla CSS (Monochrome Theme) |
| **Frontend Animations** | GSAP 3.12.5 |
| **Visualizations** | Plotly.js |
| **Authentication & Security**| Flask Session + bcrypt password hashing |
| **System Monitoring** | psutil |

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Big Data & ML Pipeline
Executes data cleaning, feature engineering, Isolation Forest anomaly detection, Random Forest trend forecasting, and seeds MongoDB with analytics:
```bash
python ml/train_models.py
```

### 3. Launch Interactive Flask Dashboard
```bash
flask run
# OR
python app.py
```
Open `http://localhost:5000` in your browser.

---

## 🔐 Default Credentials & User Roles

| Role | Username | Password | Accessible Modules |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin` | `admin123` | All pages + System Monitoring, Hardware Telemetry, Feedback, Pipeline Trigger |
| **ANALYST** | `analyst` | `analyst123` | Dashboard, Climate Analysis, Geographic Map, Anomalies, Predictions, Alerts |

---

## 📊 Dashboard Modules

1. **🏠 Command Center (`/`)**: Real-time KPI summary cards, live observation feed, event distributions, and high-level anomaly/prediction stats.
2. **📊 Geospatial Telemetry (`/analytics`)**: Heatmap matrix showing historical climate trends by event type and month, alongside geographic distributions.
3. **🚨 ML Anomaly Detection (`/anomalies`)**: Isolation Forest model metrics, severity distributions, and a detailed chronological log of detected statistical outliers.
4. **🔮 Predictive Forecasting (`/predictions`)**: Random Forest regression outputs displaying actual vs predicted weather distances with comprehensive model error metrics (R², MAE, RMSE).
5. **⚙️ Hadoop Admin (`/admin`)**: Real-time server and cluster telemetry (CPU, RAM, Disk), Hadoop node status, and MongoDB collection metrics.
