# EarthScape Climate Agency — System Architecture & Diagrams

## 1. High-Level Architecture Overview

EarthScape Climate Agency is a unified Big Data, Machine Learning, and Climate Analytics platform built 100% on the Python data science stack without any JavaScript frontend frameworks.

```mermaid
graph TD
    A[Raw Weather Events CSV - 8.6M Rows] --> B[Data Ingestion Engine]
    B --> C[Data Cleaning & Validation Layer]
    C --> D[Feature Engineering Engine]
    D --> E[Big Data Processing: PySpark & Hadoop HDFS]
    E --> F[Hadoop Streaming MapReduce]
    D --> G[Machine Learning Layer]
    G --> G1[Isolation Forest Anomaly Detector]
    G --> G2[Random Forest Trend Regressor]
    G1 --> H[(MongoDB Database)]
    G2 --> H
    F --> H
    E --> H
    H --> I[Streamlit Enterprise Dashboard]
    I --> I1[🏠 Executive Dashboard]
    I --> I2[📊 Climate Analysis]
    I --> I3[🗺️ Geospatial Maps]
    I --> I4[🚨 Anomaly Explorer]
    I --> I5[🔮 Forecasts]
    I --> I6[⚠️ Live Alert Feed]
    I --> I7[⚙️ Admin System Monitoring]
    H --> J[Tableau BI Analytics Export]
```

---

## 2. Comprehensive System Architecture Diagrams

### Diagram 1: Data Flow Diagram (DFD) — Level 0 (Context Diagram)

```mermaid
graph LR
    User[Analyst / Admin User] <-->|Interactive Query / Auth| ES[EarthScape Climate System]
    RawData[Weather Telemetry Source] -->|Historical CSV Stream| ES
    ES <-->|Indexed CRUD & Aggregations| Mongo[(MongoDB)]
    ES -->|Export Processed Extracts| Tableau[Tableau BI Platform]
```

---

### Diagram 2: Data Flow Diagram (DFD) — Level 1 (Detailed Flow)

```mermaid
graph TD
    DS[WeatherEvents_Jan2016-Dec2022.csv] --> P1[1.0 Data Ingestion & Memory Profiling]
    P1 --> D1[(HDFS: /climate/raw)]
    P1 --> P2[2.0 Data Cleaning & Outlier Imputation]
    P2 --> P3[3.0 Feature Engineering]
    P3 --> D2[(HDFS: /climate/processed)]
    P3 --> P4[4.0 PySpark Distributed Processing]
    P3 --> P5[5.0 Hadoop MapReduce Aggregations]
    P3 --> P6[6.0 ML Anomaly Detection - Isolation Forest]
    P3 --> P7[7.0 ML Trend Prediction - Random Forest]
    P4 --> D3[(MongoDB Collections)]
    P5 --> D3
    P6 --> D3
    P7 --> D3
    D3 --> P8[8.0 Streamlit Multi-Page UI Engine]
    P8 --> UI[Interactive Charts, Maps & Alerts]
```

---

### Diagram 3: Data Processing Workflow

```mermaid
flowchart LR
    A[Raw Ingest] --> B[Deduplication]
    B --> C[Timestamp Parsing]
    C --> D[Coordinate Validation]
    D --> E[Precipitation Cleaning]
    E --> F[Temporal Feature Extraction]
    F --> G[Duration & Severity Scoring]
    G --> H[Cleaned Columnar Parquet]
```

---

### Diagram 4: Machine Learning Workflow

```mermaid
flowchart TD
    subgraph Isolation_Forest_Pipeline
        A1[Clean Feature Vector: Lat, Lng, Precip, Duration, SeverityScore] --> A2[StandardScaler Normalization]
        A2 --> A3[IsolationForest 150 Estimators]
        A3 --> A4[Output: is_anomaly -1 vs 1, Decision Score]
        A4 --> A5[MongoDB 'anomalies' Collection]
    end
    
    subgraph Random_Forest_Forecasting_Pipeline
        B1[Monthly Event Count Aggregations] --> B2[Lag Feature Generation: Lag1, Lag2, Lag12, RollingMean]
        B2 --> B3[80/20 Chronological Train/Test Split]
        B3 --> B4[RandomForestRegressor Training]
        B4 --> B5[Evaluation: R2, MAE, RMSE]
        B5 --> B6[MongoDB 'predictions' Collection]
    end
```

---

### Diagram 5: MongoDB Schema & Collection Architecture

```mermaid
classDiagram
    class users {
        +String username (Unique Index)
        +String email
        +String password_hash (bcrypt)
        +String role (ADMIN / ANALYST)
        +String created_at
    }
    class weather_events_cleaned {
        +String EventId
        +String Type
        +String Severity
        +Float Precipitation(in)
        +Float LocationLat
        +Float LocationLng
        +String State
        +Int Year
        +Int Month
        +Float DurationHours
        +Int SeverityScore
    }
    class climate_summary {
        +Object kpis
        +Array yearly_summary
        +Array monthly_summary
        +Array state_summary
        +Array type_summary
        +Array severity_summary
        +Array seasonal_summary
    }
    class anomalies {
        +String EventId
        +Float anomaly_score
        +Int is_anomaly (-1)
        +String State
        +String Type
    }
    class predictions {
        +Object metrics (R2, MAE, RMSE)
        +Array series (Actual vs Predicted)
    }
    class alerts {
        +String alert_type
        +String severity
        +String state
        +String message
        +String status (Unread / Acknowledged / Resolved)
    }
```

---

### Diagram 6: Hadoop HDFS Directory Architecture

```
/climate/
├── raw/
│   └── WeatherEvents_Jan2016-Dec2022.csv      # Unmodified primary historical dataset
├── processed/
│   ├── cleaned_weather_events.parquet         # Columnar cleaned telemetry
│   └── pyspark_climate_summary.parquet        # Distributed Spark aggregations
├── ml/
│   ├── isolation_forest.joblib                # Trained anomaly detection model
│   └── random_forest_regressor.joblib         # Trained climate trend regressor
└── output/
    └── state_events_summary/                  # MapReduce state event counts
        ├── _SUCCESS
        └── part-00000
```

---

### Diagram 7: Streamlit Dashboard Navigation & Role Workflow

```mermaid
flowchart TD
    Start[User Opens Dashboard] --> Login[Secure bcrypt Login]
    Login --> RoleCheck{User Role?}
    
    RoleCheck -->|ANALYST| AnalystViews
    RoleCheck -->|ADMIN| AdminViews
    
    subgraph AnalystViews [Analyst Accessible Modules]
        P1[🏠 Main Dashboard]
        P2[📊 Climate Analysis]
        P3[🗺️ Geographic Analysis]
        P4[🚨 Anomaly Detection]
        P5[🔮 Predictions]
        P6[⚠️ Live Alert Feed]
    end
    
    subgraph AdminViews [Admin Exclusive Modules]
        P7[⚙️ Host Hardware Metrics - psutil]
        P8[🌐 MongoDB, HDFS, Spark Health]
        P9[🔄 Pipeline Re-Execution Trigger]
        P10[💬 User Feedback & Audit Logs]
    end
    
    AdminViews --> AnalystViews
```

---

### Diagram 8: Real-Time Telemetry Simulation Stream

```mermaid
flowchart LR
    A[APScheduler Trigger - Every 15s] --> B[Generate Realistic Weather Telemetry]
    B --> C[Validate Bounds & Format]
    C --> D[Evaluate Isolation Forest Anomaly Score]
    D --> E[Check Alert Rules: Severe / High Precip / Anomaly]
    E --> F[Persist to MongoDB Collections]
    F --> G[Streamlit UI Reactive Refresh (DEMO/SIMULATED)]
```
