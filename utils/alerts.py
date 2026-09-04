"""
Alert Management and Trigger Engine
Monitors weather conditions, ML anomaly tags, and precipitation thresholds to issue alerts.
"""
import datetime
from typing import Dict, Any, List

def evaluate_and_generate_alerts(event: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluate a single weather event or batch of events and generate alerts based on SRS criteria:
    1. Severe Weather Event (Severity == 'Severe' or 'Heavy')
    2. High Precipitation (> 2.0 inches)
    3. Machine Learning Anomaly (is_anomaly == -1)
    """
    alerts = []
    timestamp = event.get('StartTime(UTC)') or datetime.datetime.utcnow().isoformat()
    state = event.get('State', 'Unknown')
    event_type = event.get('Type', 'Weather Event')
    severity = event.get('Severity', 'Moderate')
    precip = float(event.get('Precipitation(in)', 0.0) or 0.0)
    is_anomaly = event.get('is_anomaly', 1)

    # 1. Severe Event Alert
    if severity in ['Severe', 'Heavy']:
        alerts.append({
            "alert_type": "Severe Weather Alert",
            "severity": severity,
            "state": state,
            "event_type": event_type,
            "message": f"🚨 High-severity event detected: {severity} {event_type} in {state}.",
            "timestamp": timestamp,
            "status": "Unread",
            "source": event.get('source', 'Historical Telemetry')
        })

    # 2. Extreme Precipitation Alert
    if precip >= 2.0:
        alerts.append({
            "alert_type": "Extreme Precipitation Warning",
            "severity": "High",
            "state": state,
            "event_type": event_type,
            "message": f"🌧️ Torrential rainfall warning: {precip:.2f} in recorded in {state} ({event_type}).",
            "timestamp": timestamp,
            "status": "Unread",
            "source": event.get('source', 'Historical Telemetry')
        })

    # 3. Machine Learning Anomaly Alert
    if is_anomaly == -1:
        alerts.append({
            "alert_type": "ML Climate Anomaly",
            "severity": "Warning",
            "state": state,
            "event_type": event_type,
            "message": f"🔮 Isolation Forest detected an anomalous pattern in {state} for {event_type} (Score: {event.get('anomaly_score', -0.5):.3f}).",
            "timestamp": timestamp,
            "status": "Unread",
            "source": event.get('source', 'Historical Telemetry')
        })

    return alerts

def save_alerts_to_db(db, alerts: List[Dict[str, Any]]):
    """Insert alerts into MongoDB 'alerts' collection."""
    if db is not None and alerts:
        db['alerts'].insert_many(alerts)
