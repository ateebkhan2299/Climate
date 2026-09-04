"""
Data Utilities Module
Contains robust functions for data cleaning, validation, feature engineering, and aggregation.
"""
import pandas as pd
import numpy as np
from datetime import datetime

# Severity score mapping
SEVERITY_MAP = {
    'Light': 1,
    'Moderate': 2,
    'Heavy': 3,
    'Severe': 4,
    'UNK': 0,
    'Other': 1
}

def get_season(month: int) -> str:
    """Map month number (1-12) to Meteorological Season."""
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

def clean_and_engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean dataset and extract rich temporal, geographic, and domain features.
    """
    # Create copy to prevent modifying original view
    clean_df = df.copy()

    # 1. Deduplication
    clean_df.drop_duplicates(inplace=True)

    # 2. Datetime parsing
    clean_df['StartTime(UTC)'] = pd.to_datetime(clean_df['StartTime(UTC)'], errors='coerce')
    clean_df['EndTime(UTC)'] = pd.to_datetime(clean_df['EndTime(UTC)'], errors='coerce')

    # Drop records with invalid timestamps
    clean_df.dropna(subset=['StartTime(UTC)', 'EndTime(UTC)'], inplace=True)

    # 3. Temporal feature engineering
    clean_df['Year'] = clean_df['StartTime(UTC)'].dt.year
    clean_df['Month'] = clean_df['StartTime(UTC)'].dt.month
    clean_df['Day'] = clean_df['StartTime(UTC)'].dt.day
    clean_df['Hour'] = clean_df['StartTime(UTC)'].dt.hour
    clean_df['DayOfWeek'] = clean_df['StartTime(UTC)'].dt.day_name()
    clean_df['Season'] = clean_df['Month'].apply(get_season)

    # 4. Duration calculation (in hours)
    clean_df['DurationHours'] = (clean_df['EndTime(UTC)'] - clean_df['StartTime(UTC)']).dt.total_seconds() / 3600.0
    # Clean duration anomalies (negative or unrealistically high > 720 hours / 30 days)
    clean_df = clean_df[(clean_df['DurationHours'] >= 0) & (clean_df['DurationHours'] <= 720)]

    # 5. Coordinate validation (US bounds roughly Lat: 20-55, Lng: -130 to -65)
    clean_df.dropna(subset=['LocationLat', 'LocationLng'], inplace=True)
    clean_df = clean_df[
        (clean_df['LocationLat'] >= 18.0) & (clean_df['LocationLat'] <= 72.0) &
        (clean_df['LocationLng'] >= -170.0) & (clean_df['LocationLng'] <= -60.0)
    ]

    # 6. Precipitation cleaning & imputation
    if 'Precipitation(in)' in clean_df.columns:
        clean_df['Precipitation(in)'] = clean_df['Precipitation(in)'].fillna(0.0)
        clean_df['Precipitation(in)'] = clean_df['Precipitation(in)'].clip(lower=0.0, upper=25.0)

    # 7. Categorical cleaning
    clean_df['Type'] = clean_df['Type'].fillna('Unknown')
    clean_df['Severity'] = clean_df['Severity'].fillna('Moderate')
    clean_df['State'] = clean_df['State'].fillna('Unknown')
    clean_df['City'] = clean_df['City'].fillna('Unknown')

    # 8. Domain Features: Severity Score
    clean_df['SeverityScore'] = clean_df['Severity'].map(lambda x: SEVERITY_MAP.get(str(x), 1))

    return clean_df
