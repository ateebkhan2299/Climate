"""
Climate Trend Prediction Module
Uses Scikit-learn RandomForestRegressor to model and forecast monthly weather event frequencies.
"""
import joblib
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

PRED_MODEL_PATH = "d:/climate/models/saved_models/random_forest_regressor.joblib"

class ClimateTrendPredictor:
    def __init__(self, n_estimators: int = 200, random_state: int = 42):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=10,
            random_state=random_state
        )
        self.metrics = {}

    def prepare_time_series_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate weather event counts by Year and Month, and build lag features.
        """
        monthly = df.groupby(['Year', 'Month']).agg(
            EventCount=('EventId', 'count'),
            AvgPrecip=('Precipitation(in)', 'mean'),
            AvgDuration=('DurationHours', 'mean'),
            AvgSeverity=('SeverityScore', 'mean')
        ).reset_index()

        monthly.sort_values(by=['Year', 'Month'], inplace=True)
        monthly['TimeIndex'] = np.arange(len(monthly))

        # Lag features
        monthly['Lag_1'] = monthly['EventCount'].shift(1)
        monthly['Lag_2'] = monthly['EventCount'].shift(2)
        monthly['Lag_12'] = monthly['EventCount'].shift(12)
        monthly['RollingMean_3'] = monthly['EventCount'].shift(1).rolling(window=3).mean()

        # Handle NaNs from shifting
        monthly.bfill(inplace=True)
        monthly.ffill(inplace=True)
        return monthly

    def train_and_evaluate(self, monthly_df: pd.DataFrame):
        """Train model and compute R2, MAE, RMSE."""
        feature_cols = ['Month', 'TimeIndex', 'AvgPrecip', 'AvgDuration', 'AvgSeverity', 'Lag_1', 'Lag_2', 'Lag_12', 'RollingMean_3']
        X = monthly_df[feature_cols]
        y = monthly_df['EventCount']

        # Train/Test Split: Use earlier 80% for train, last 20% for test
        split_idx = int(len(monthly_df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        self.model.fit(X_train, y_train)

        # Predictions
        y_pred = self.model.predict(X_test)
        y_all_pred = self.model.predict(X)

        # Metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        self.metrics = {
            "MAE": round(float(mae), 2),
            "RMSE": round(float(rmse), 2),
            "R2": round(float(r2), 4),
            "Train_Samples": len(X_train),
            "Test_Samples": len(X_test)
        }

        # Save model
        os.makedirs(os.path.dirname(PRED_MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, PRED_MODEL_PATH)

        # Build comparison dataset
        comparison_df = monthly_df.copy()
        comparison_df['PredictedCount'] = np.round(y_all_pred).astype(int)
        comparison_df['IsTestPeriod'] = False
        comparison_df.loc[comparison_df.index[split_idx:], 'IsTestPeriod'] = True

        return comparison_df, self.metrics

    @classmethod
    def load(cls):
        """Load trained regression model."""
        predictor = cls()
        if os.path.exists(PRED_MODEL_PATH):
            predictor.model = joblib.load(PRED_MODEL_PATH)
        return predictor
