# Installation & Setup Guide — EarthScape Climate Agency

This document provides step-by-step instructions to set up, configure, and run the **EarthScape Climate Agency** Big Data, Machine Learning, and Analytics platform.

---

## 1. Prerequisites & System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+)
- **Python Version**: Python 3.10 to 3.14 (64-bit)
- **Database**: MongoDB Community Server v6.0+ (running locally on port 27017 or remote cluster)
- **RAM**: Minimum 8 GB (16 GB recommended for PySpark and full CSV processing)
- **Storage**: Minimum 5 GB free disk space

---

## 2. Environment Setup & Dependency Installation

### Step 1: Clone or Navigate to Project Root
```bash
cd d:/climate
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

Verify installed packages:
```bash
python -c "import pandas, numpy, pyspark, pymongo, sklearn, streamlit, plotly, psutil, apscheduler, bcrypt; print('All core libraries installed successfully!')"
```

---

## 3. MongoDB Configuration & Initialization

Ensure the local MongoDB service is started:
- On Windows: Check Windows Services for `MongoDB Server` or run `mongod --dbpath <data_dir>`.
- On Linux/macOS: `sudo systemctl start mongod` or `brew services start mongodb-community`.

### Initialize Collections & Seed Default Credentials
```bash
python database/seed_db.py
```
This initializes MongoDB indexes and seeds the following default accounts:
- **Admin**: `admin` / `admin123` (Full administrative & system monitoring access)
- **Analyst**: `analyst` / `analyst123` (Analytical dashboard & ML exploration access)

---

## 4. Execute the Big Data & ML Pipeline

Run the master data ingestion, cleaning, feature engineering, Isolation Forest, and Random Forest training pipeline:
```bash
python ml/train_models.py
```
This generates:
- Cleaned parquet file: `data/cleaned/cleaned_weather_events.parquet`
- Saved models: `models/saved_models/isolation_forest.joblib` and `models/saved_models/random_forest_regressor.joblib`
- Populated MongoDB collections: `climate_summary`, `anomalies`, `predictions`, `alerts`, `weather_events_cleaned`.

---

## 5. Execute Hadoop MapReduce

### Local Streaming Simulation Pipe:
```bash
python hadoop/run_mapreduce.py
```

### Production Hadoop HDFS Cluster Commands (Optional for Cluster Deployment):
```bash
# 1. Create HDFS directories
hdfs dfs -mkdir -p /climate/raw /climate/processed /climate/ml /climate/output

# 2. Upload dataset
hdfs dfs -put WeatherEvents_Jan2016-Dec2022.csv /climate/raw/

# 3. Submit Hadoop Streaming Job
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files d:/climate/hadoop/mapper.py,d:/climate/hadoop/reducer.py \
  -input /climate/raw/WeatherEvents_Jan2016-Dec2022.csv \
  -output /climate/output/state_events_summary \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py"
```

---

## 6. Launch the Streamlit Dashboard

Start the application server:
```bash
streamlit run app.py
```
The application will open automatically in your default browser at `http://localhost:8501`.

---

## 7. Interactive Jupyter Laboratory

To launch and run the 9 laboratory notebooks:
```bash
jupyter lab
# Or: jupyter notebook
```
Navigate to the `notebooks/` folder and execute notebooks `01` through `09` in sequential order.
