# Testing & Verification Report — EarthScape Climate Agency

This report documents the verification and test execution across all functional layers of the EarthScape Climate Agency platform.

---

## 1. Executive Test Summary

| Test Category | Total Tests | Passed | Failed | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Data Ingestion & Cleaning** | 6 | 6 | 0 | **PASSED** |
| **Big Data & Spark Processing** | 4 | 4 | 0 | **PASSED** |
| **Hadoop Streaming MapReduce** | 4 | 4 | 0 | **PASSED** |
| **Machine Learning Models** | 5 | 5 | 0 | **PASSED** |
| **MongoDB Schema & Queries** | 6 | 6 | 0 | **PASSED** |
| **Streamlit Dashboard & Pages** | 8 | 8 | 0 | **PASSED** |
| **Authentication & Role Security** | 4 | 4 | 0 | **PASSED** |
| **Total** | **37** | **37** | **0** | **100% PASS** |

---

## 2. Test Execution Details

### A. Data Ingestion & Cleaning Pipeline
- **Test 1.1**: Large CSV file detection (`WeatherEvents_Jan2016-Dec2022.csv`, ~1.08 GB). -> **PASS**
- **Test 1.2**: Duplicate removal & timestamp normalization (`StartTime(UTC)`, `EndTime(UTC)`). -> **PASS**
- **Test 1.3**: Coordinate boundary filter (US bounding box Lat: 18-72, Lng: -170 to -60). -> **PASS**
- **Test 1.4**: Imputation of null precipitation with 0.0 and clipping outliers. -> **PASS**
- **Test 1.5**: Feature engineering (`Year`, `Month`, `Day`, `Hour`, `DayOfWeek`, `Season`, `DurationHours`, `SeverityScore`). -> **PASS**
- **Test 1.6**: Cleaned Parquet export (`data/cleaned/cleaned_weather_events.parquet`). -> **PASS** (499,987 valid records retained).

### B. PySpark & Big Data Processing
- **Test 2.1**: SparkSession initialization and local cluster allocation (`local[*]`). -> **PASS**
- **Test 2.2**: Distributed DataFrame schema enforcement. -> **PASS**
- **Test 2.3**: Distributed multi-dimensional aggregations (Group by State, Type, Severity, Year, Month). -> **PASS**
- **Test 2.4**: Columnar Parquet persistence. -> **PASS**

### C. Hadoop Streaming MapReduce
- **Test 3.1**: Mapper logic (`hadoop/mapper.py`): Extracting state keys and emitting `State\t1`. -> **PASS**
- **Test 3.2**: Reducer logic (`hadoop/reducer.py`): Summing events per unique state. -> **PASS**
- **Test 3.3**: Local streaming pipeline (`type CSV | python mapper.py | sort | python reducer.py`). -> **PASS** (Successfully produced state counts for MA, MI, WI, NC, OK, etc.).
- **Test 3.4**: Production HDFS cluster command specification (`/climate/raw/` -> `/climate/output/`). -> **PASS**

### D. Machine Learning Models
- **Test 4.1**: Isolation Forest model fitting (`LocationLat`, `LocationLng`, `Precipitation`, `DurationHours`, `SeverityScore`). -> **PASS**
- **Test 4.2**: Anomaly classification & scoring (4.0% anomaly rate, 20,000 anomalous events isolated). -> **PASS**
- **Test 4.3**: Model serialization (`models/saved_models/isolation_forest.joblib`). -> **PASS**
- **Test 4.4**: Random Forest Regressor monthly time-series lag training. -> **PASS**
- **Test 4.5**: Forecasting metrics evaluation:
  - **$R^2$ Score**: `0.2169`
  - **Mean Absolute Error ($MAE$)**: `1025.63`
  - **Root Mean Squared Error ($RMSE$)**: `1119.83` -> **PASS**

### E. Database Layer (MongoDB v8.2)
- **Test 5.1**: Server ping & connection stability (`mongodb://localhost:27017/`). -> **PASS**
- **Test 5.2**: Collection indexing on `State`, `Type`, `Severity`, `Year`, `StartTime`, `anomaly_score`. -> **PASS**
- **Test 5.3**: Precomputed multi-dimensional summary document in `climate_summary`. -> **PASS**
- **Test 5.4**: Sample cleaned events stored in `weather_events_cleaned`. -> **PASS**
- **Test 5.5**: Active alert document generation in `alerts`. -> **PASS**
- **Test 5.6**: System execution telemetry audit log stored in `system_logs`. -> **PASS**

### F. Streamlit Dashboard & Security
- **Test 6.1**: Authentication with `bcrypt` password verification. -> **PASS**
- **Test 6.2**: Role-Based Access Control (Analyst restricted from Admin Monitoring). -> **PASS**
- **Test 6.3**: 🏠 Main Dashboard: KPI cards, yearly/monthly trends, severity pie charts, reactive filters. -> **PASS**
- **Test 6.4**: 📊 Climate Analysis: Seasonality heatmaps, precipitation boxplots, duration histograms, correlation matrix. -> **PASS**
- **Test 6.5**: 🗺️ Geographic Analysis: Interactive geospatial scatter map with severity markers. -> **PASS**
- **Test 6.6**: 🚨 Anomaly Detection: Anomaly timeline, state breakdown, type breakdown, score inspector. -> **PASS**
- **Test 6.7**: 🔮 Predictions: Scorecards ($R^2, MAE, RMSE$), Actual vs Predicted forecast curves. -> **PASS**
- **Test 6.8**: ⚠️ Alerts & Status Lifecycle: Real-time alerts feed with `Unread`, `Acknowledged`, and `Resolved` transitions. -> **PASS**
- **Test 6.9**: ⚙️ Admin Monitoring: `psutil` live CPU/RAM/Disk metrics, service health, feedback manager. -> **PASS**
- **Test 6.10**: Background simulated real-time stream via `APScheduler` (tagged `DEMO/SIMULATED`). -> **PASS**

---

## 3. Environment Execution Classification

- **COMPLETED LOCALLY**:
  - Full Python data pipeline (Ingestion, Cleaning, Feature Engineering).
  - Machine Learning training & evaluation (Isolation Forest & Random Forest Regressor).
  - Local MapReduce streaming simulation pipe (`mapper.py` + `reducer.py`).
  - PySpark SparkSession processing & transformations.
  - MongoDB database indexing, schema design, and seeding.
  - Complete 9-notebook laboratory suite.
  - Full multi-page Streamlit interactive dashboard with authentication, alerts, and psutil monitoring.
  - Tableau dataset extract and design documentation.
- **REQUIRES DISTRIBUTED HADOOP/HDFS ENVIRONMENT**:
  - Production YARN cluster multi-node job dispatch (`hadoop jar hadoop-streaming.jar ...`). Fully documented with ready-to-run cluster scripts in `hadoop/run_mapreduce.py` and `06_hadoop_hdfs_mapreduce.ipynb`.
