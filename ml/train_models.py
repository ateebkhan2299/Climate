"""
Master Data Pipeline and Model Training Engine
Executes end-to-end: Ingestion -> Cleaning -> Feature Engineering -> ML (IsolationForest + RandomForest) -> Summary Aggregations -> MongoDB Seeding.
"""
import os
import sys
import time
import pandas as pd
import numpy as np
import datetime

# Ensure project root is in path and stdout handles utf-8
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database.mongodb import get_db, create_indexes
from utils.data_utils import clean_and_engineer_features
from ml.anomaly_model import ClimateAnomalyDetector
from ml.prediction_model import ClimateTrendPredictor
from utils.alerts import evaluate_and_generate_alerts

DATA_PATH = "d:/climate/WeatherEvents_Jan2016-Dec2022.csv"
CLEANED_DATA_PATH = "d:/climate/data/cleaned/cleaned_weather_events.parquet"
PROCESSED_DATA_PATH = "d:/climate/data/processed/climate_summary.parquet"

def run_pipeline():
    start_time = time.time()
    print("[INFO] Starting EarthScape Big Data & ML Pipeline...")

    # Ensure output directories
    os.makedirs("d:/climate/data/raw", exist_ok=True)
    os.makedirs("d:/climate/data/cleaned", exist_ok=True)
    os.makedirs("d:/climate/data/processed", exist_ok=True)
    os.makedirs("d:/climate/models/saved_models", exist_ok=True)

    # 1. Load Dataset
    print(f"📖 Ingesting dataset from {DATA_PATH}...")
    # Load representative sample or full set (e.g. 500k rows for fast high-accuracy training or full)
    # To balance speed and deep coverage for a 8.6M dataset, load 400,000 diverse rows
    df_raw = pd.read_csv(DATA_PATH, nrows=500000)
    print(f"Loaded {len(df_raw):,} raw records with {len(df_raw.columns)} columns.")

    # 2. Clean & Feature Engineering
    print("🧹 Cleaning data and engineering temporal/domain features...")
    df_clean = clean_and_engineer_features(df_raw)
    print(f"Dataset after cleaning: {len(df_clean):,} valid records.")

    # Save cleaned sample to parquet
    df_clean.to_parquet(CLEANED_DATA_PATH, index=False)
    print(f"[SUCCESS] Saved cleaned dataset to {CLEANED_DATA_PATH}")

    # 3. Anomaly Detection (Isolation Forest)
    print("[INFO] Training Isolation Forest Anomaly Detection Model...")
    anomaly_detector = ClimateAnomalyDetector(contamination=0.04, random_state=42)
    anomaly_detector.fit(df_clean)
    df_with_anomalies = anomaly_detector.predict(df_clean)

    total_anomalies = int((df_with_anomalies['is_anomaly'] == -1).sum())
    anomaly_pct = round((total_anomalies / len(df_with_anomalies)) * 100, 2)
    print(f"[SUCCESS] Anomaly Detection Completed: {total_anomalies:,} anomalies identified ({anomaly_pct}%).")

    # 4. Climate Trend Prediction (Random Forest Regressor)
    print("[INFO] Training Climate Trend Prediction Model (Random Forest)...")
    trend_predictor = ClimateTrendPredictor(n_estimators=150, random_state=42)
    monthly_ts = trend_predictor.prepare_time_series_data(df_with_anomalies)
    comparison_df, metrics = trend_predictor.train_and_evaluate(monthly_ts)
    print(f"[SUCCESS] Trend Prediction Trained. R2: {metrics['R2']}, MAE: {metrics['MAE']}, RMSE: {metrics['RMSE']}.")

    # 5. Precalculate Analytics & Multi-Dimensional Summaries
    print("[INFO] Generating Multi-Dimensional Climate Summaries...")
    
    # Yearly Summary
    yearly_summary = df_with_anomalies.groupby(['Year', 'Severity']).size().unstack(fill_value=0).reset_index().to_dict(orient='records')
    
    # Monthly Summary
    monthly_summary = df_with_anomalies.groupby(['Month', 'Type']).size().unstack(fill_value=0).reset_index().to_dict(orient='records')
    
    # State Summary
    state_summary = df_with_anomalies.groupby('State').agg(
        TotalEvents=('EventId', 'count'),
        SevereEvents=('Severity', lambda s: (s.isin(['Severe', 'Heavy'])).sum()),
        TotalPrecip=('Precipitation(in)', 'sum'),
        AvgPrecip=('Precipitation(in)', 'mean'),
        Anomalies=('is_anomaly', lambda a: (a == -1).sum()),
        AvgDuration=('DurationHours', 'mean')
    ).reset_index().sort_values(by='TotalEvents', ascending=False).to_dict(orient='records')

    # Event Type Summary
    type_summary = df_with_anomalies.groupby('Type').agg(
        Count=('EventId', 'count'),
        AvgPrecip=('Precipitation(in)', 'mean'),
        AvgDuration=('DurationHours', 'mean')
    ).reset_index().sort_values(by='Count', ascending=False).to_dict(orient='records')

    # Severity Summary
    severity_summary = df_with_anomalies.groupby('Severity').size().reset_index(name='Count').to_dict(orient='records')

    # Seasonal Summary
    seasonal_summary = df_with_anomalies.groupby(['Season', 'Type']).size().unstack(fill_value=0).reset_index().to_dict(orient='records')

    # Global KPI Card Stats
    top_state = df_with_anomalies['State'].value_counts().index[0]
    top_event = df_with_anomalies['Type'].value_counts().index[0]
    severe_count = int(df_with_anomalies['Severity'].isin(['Severe', 'Heavy']).sum())

    kpis = {
        "summary_id": "global_kpis",
        "total_events": len(df_with_anomalies),
        "total_severe_events": severe_count,
        "total_anomalies": total_anomalies,
        "anomaly_percentage": anomaly_pct,
        "most_affected_state": top_state,
        "most_common_event": top_event,
        "average_precipitation": round(float(df_with_anomalies['Precipitation(in)'].mean()), 2),
        "last_updated": datetime.datetime.utcnow().isoformat()
    }

    # 6. Extract Anomalies & Alerts
    print("[INFO] Generating Initial Alerts from Telemetry...")
    anomalies_df = df_with_anomalies[df_with_anomalies['is_anomaly'] == -1].copy()
    
    # Convert datetime objects to string before MongoDB insertion
    for col in ['StartTime(UTC)', 'EndTime(UTC)']:
        if col in anomalies_df.columns:
            anomalies_df[col] = anomalies_df[col].astype(str)
        if col in df_with_anomalies.columns:
            df_with_anomalies[col] = df_with_anomalies[col].astype(str)

    # Generate alerts for high-priority anomalous / severe events
    alert_sample = anomalies_df.head(200).to_dict(orient='records')
    alerts_list = []
    for evt in alert_sample:
        alerts_list.extend(evaluate_and_generate_alerts(evt))

    # 7. Seed to MongoDB
    print("[INFO] Persisting Processed Results to MongoDB...")
    db = get_db()
    if db is not None:
        create_indexes(db)

        # Store climate_summary
        db['climate_summary'].delete_many({})
        db['climate_summary'].insert_one({
            "kpis": kpis,
            "yearly_summary": yearly_summary,
            "monthly_summary": monthly_summary,
            "state_summary": state_summary,
            "type_summary": type_summary,
            "severity_summary": severity_summary,
            "seasonal_summary": seasonal_summary,
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })

        # Store anomalies (sampled to 5000 for responsive UI)
        db['anomalies'].delete_many({})
        anomaly_records = anomalies_df.head(5000).to_dict(orient='records')
        if anomaly_records:
            db['anomalies'].insert_many(anomaly_records)

        # Store predictions
        db['predictions'].delete_many({})
        pred_records = comparison_df.to_dict(orient='records')
        db['predictions'].insert_one({
            "metrics": metrics,
            "series": pred_records,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })

        # Store alerts
        if alerts_list:
            db['alerts'].delete_many({})
            db['alerts'].insert_many(alerts_list[:100])

        # Store clean records sample in weather_events_cleaned
        db['weather_events_cleaned'].delete_many({})
        sample_records = df_with_anomalies.head(20000).to_dict(orient='records')
        db['weather_events_cleaned'].insert_many(sample_records)

        # Store pipeline execution log
        elapsed = round(time.time() - start_time, 2)
        db['system_logs'].insert_one({
            "event": "Pipeline Execution",
            "status": "SUCCESS",
            "records_processed": len(df_with_anomalies),
            "anomalies_found": total_anomalies,
            "duration_seconds": elapsed,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        print("[SUCCESS] MongoDB successfully seeded!")

    elapsed = round(time.time() - start_time, 2)
    print(f"[DONE] Pipeline completed successfully in {elapsed} seconds.")
    return True

if __name__ == "__main__":
    run_pipeline()
