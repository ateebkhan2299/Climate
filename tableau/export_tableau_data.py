"""
Tableau Dataset Export Engine
Generates optimized flat CSV / Parquet extracts for Tableau BI dashboards.
"""
import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.mongodb import get_db

EXPORT_DIR = "d:/climate/tableau"
OUTPUT_CSV = os.path.join(EXPORT_DIR, "earthscape_tableau_dataset.csv")

def export_for_tableau():
    print("[INFO] Exporting dataset for Tableau BI...")
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    # Try reading from cleaned parquet first
    cleaned_parquet = "d:/climate/data/cleaned/cleaned_weather_events.parquet"
    if os.path.exists(cleaned_parquet):
        df = pd.read_parquet(cleaned_parquet)
    else:
        print("[INFO] Reading from raw CSV...")
        df = pd.read_csv("d:/climate/WeatherEvents_Jan2016-Dec2022.csv", nrows=100000)
    
    # Select key analytical columns
    cols = ['EventId', 'Type', 'Severity', 'StartTime(UTC)', 'EndTime(UTC)', 
            'Precipitation(in)', 'LocationLat', 'LocationLng', 'City', 'State', 
            'Year', 'Month', 'DayOfWeek', 'Season', 'DurationHours', 'SeverityScore']
    
    available_cols = [c for c in cols if c in df.columns]
    tableau_df = df[available_cols].copy()
    
    # Export to CSV
    tableau_df.to_csv(OUTPUT_CSV, index=False)
    print(f"[SUCCESS] Exported {len(tableau_df):,} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    export_for_tableau()
