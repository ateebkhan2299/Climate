"""
Isolation Forest Anomaly Detection Module
Uses Scikit-learn's IsolationForest to identify anomalous weather patterns.
"""
import joblib
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

MODEL_PATH = "d:/climate/models/saved_models/isolation_forest.joblib"
SCALER_PATH = "d:/climate/models/saved_models/scaler.joblib"

class ClimateAnomalyDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=150,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.feature_columns = ['LocationLat', 'LocationLng', 'Precipitation(in)', 'DurationHours', 'SeverityScore']

    def preprocess_features(self, df: pd.DataFrame, fit_scaler: bool = False) -> np.ndarray:
        """Extract and scale feature vectors."""
        X = df[self.feature_columns].copy()
        X['Precipitation(in)'] = X['Precipitation(in)'].fillna(0.0)
        X['DurationHours'] = X['DurationHours'].fillna(1.0)
        X['SeverityScore'] = X['SeverityScore'].fillna(1)
        
        # Replace infinities
        X.replace([np.inf, -np.inf], 0, inplace=True)
        
        if fit_scaler:
            return self.scaler.fit_transform(X)
        return self.scaler.transform(X)

    def fit(self, df: pd.DataFrame):
        """Fit Isolation Forest model on cleaned weather records."""
        X_scaled = self.preprocess_features(df, fit_scaler=True)
        self.model.fit(X_scaled)
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        joblib.dump(self.scaler, SCALER_PATH)

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict anomaly labels (-1 = Anomaly, 1 = Normal) and anomaly scores."""
        X_scaled = self.preprocess_features(df, fit_scaler=False)
        preds = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        result_df = df.copy()
        result_df['is_anomaly'] = preds
        result_df['anomaly_score'] = scores
        return result_df

    @classmethod
    def load(cls):
        """Load trained model and scaler from disk if exists."""
        detector = cls()
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            detector.model = joblib.load(MODEL_PATH)
            detector.scaler = joblib.load(SCALER_PATH)
        return detector
