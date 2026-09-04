# 🌍 EarthScape Climate Agency — Big Data, Machine Learning & Climate Analytics Platform

**EarthScape Climate Agency** is an end-to-end Python-native Big Data analytics, machine learning, and interactive dashboard platform designed for large-scale climate and weather event intelligence.

---

## 🛠️ Technology Stack (100% Python Native)

| Domain | Technology / Library |
| :--- | :--- |
| **Data Ingestion & Cleaning** | Pandas, NumPy |
| **Big Data Processing** | Apache PySpark 4.2 |
| **Distributed Storage** | Apache Hadoop HDFS (`/climate/raw/`, `/climate/processed/`, `/climate/ml/`) |
| **MapReduce** | Hadoop Streaming Python (`mapper.py`, `reducer.py`) |
| **Database** | MongoDB v8.2 + PyMongo |
| **Machine Learning** | Scikit-learn (Isolation Forest Anomaly Detection, Random Forest Regressor) |
| **Interactive Dashboard** | Streamlit |
| **Visualizations** | Plotly, Matplotlib, Seaborn, Folium |
| **Authentication & Security**| Streamlit Session State + bcrypt password hashing |
| **Real-Time Simulation** | APScheduler Background Scheduler |
| **System Monitoring** | psutil, Python logging |
| **Business Intelligence** | Tableau |

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed MongoDB Database & Users
Ensure your local MongoDB service is active on `mongodb://localhost:27017/`:
```bash
python database/seed_db.py
```

### 3. Run Big Data & ML Pipeline
Executes data cleaning, feature engineering, Isolation Forest anomaly detection, Random Forest trend forecasting, and seeds MongoDB with analytics:
```bash
python ml/train_models.py
```

### 4. Execute Hadoop MapReduce (Local Streaming & HDFS)
```bash
python hadoop/run_mapreduce.py
```

### 5. Launch Interactive Streamlit Dashboard
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 🔐 Default Credentials & User Roles

| Role | Username | Password | Accessible Modules |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin` | `admin123` | All pages + System Monitoring, Hardware Telemetry, Feedback, Pipeline Trigger |
| **ANALYST** | `analyst` | `analyst123` | Dashboard, Climate Analysis, Geographic Map, Anomalies, Predictions, Alerts |

---

## 📂 Project Directory Structure

```
d:/climate/
├── WeatherEvents_Jan2016-Dec2022.csv   # Raw Primary Dataset (8.6M Rows)
├── data/
│   ├── raw/                            # Raw staging
│   ├── cleaned/                        # Parquet cleaned dataset
│   └── processed/                      # Analytical summaries
├── notebooks/                          # Comprehensive 9-Notebook Suite
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_eda.ipynb
│   ├── 05_pyspark_processing.ipynb
│   ├── 06_hadoop_hdfs_mapreduce.ipynb
│   ├── 07_anomaly_detection.ipynb
│   ├── 08_climate_prediction.ipynb
│   └── 09_mongodb_results.ipynb
├── hadoop/
│   ├── mapper.py                       # Python Hadoop Streaming Mapper
│   ├── reducer.py                      # Python Hadoop Streaming Reducer
│   └── run_mapreduce.py                # Local runner & HDFS cluster commands
├── ml/
│   ├── anomaly_model.py                # Isolation Forest Anomaly Detector
│   ├── prediction_model.py             # Random Forest Trend Predictor
│   └── train_models.py                 # Master ML pipeline & MongoDB seeder
├── database/
│   ├── mongodb.py                      # Connection manager & collection indexes
│   └── seed_db.py                      # Database initializer & default accounts
├── utils/
│   ├── auth.py                         # Bcrypt authentication manager
│   ├── data_utils.py                   # Data cleaning & feature transformations
│   ├── monitoring.py                   # psutil host hardware telemetry
│   ├── alerts.py                       # Climate alert trigger engine
│   └── simulator.py                    # Real-time telemetry streaming simulator
├── pages/
│   ├── 1_🏠_Dashboard.py               # Main Executive KPI Dashboard
│   ├── 2_📊_Climate_Analysis.py        # In-depth seasonal & correlation analysis
│   ├── 3_🗺️_Geographic_Analysis.py    # Interactive geospatial mapping
│   ├── 4_🚨_Anomaly_Detection.py       # ML Anomaly scores & timeline
│   ├── 5_🔮_Predictions.py             # Actual vs Predicted forecast curves
│   ├── 6_⚠️_Alerts.py                  # Live climate alert management feed
│   └── 7_⚙️_Admin_Monitoring.py        # Admin psutil hardware & service metrics
├── models/
│   └── saved_models/                   # Serialized joblib ML models
├── tableau/
│   ├── export_tableau_data.py          # Data export script for Tableau BI
│   ├── earthscape_tableau_dataset.csv  # Cleaned extract for Tableau
│   └── TABLEAU_GUIDE.md                # Tableau worksheet & dashboard guide
├── app.py                              # Main Streamlit Application Entrypoint
├── ARCHITECTURE.md                     # Detailed system architecture document
├── requirements.txt                    # Project dependencies
└── README.md                           # Documentation
```

---

## 📊 Streamlit Dashboard Pages

1. **🏠 Main Dashboard**: Real-time KPI summary cards (Total Events, Severe Events, Anomalies, Top State, Avg Precipitation), dynamic filters, and interactive Plotly trend charts.
2. **📊 Climate Analysis**: In-depth climate trends, precipitation boxplots, event duration distribution, and feature correlation matrix heatmap.
3. **🗺️ Geographic Analysis**: Interactive geospatial maps with event clustering, severity overlays, and bounding box filtering.
4. **🚨 Anomaly Detection**: Isolation Forest metrics, normal vs anomaly scatter plots, timeline of detected anomalies, and tabular inspector.
5. **🔮 Predictions**: Random Forest Regressor metrics ($R^2$, $MAE$, $RMSE$), and Actual vs Predicted trend comparison curves.
6. **⚠️ Alerts**: Automated alert feed for Severe Weather, High Precipitation, and ML Anomalies with acknowledge toggles.
7. **⚙️ Admin & System Monitoring**: Live host hardware metrics via `psutil` (CPU, RAM, Disk), database health checks, collection document counters, and manual pipeline re-execution.
