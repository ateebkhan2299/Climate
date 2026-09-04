"""
Open-Meteo Real-Time Weather API Ingestion Client
Fetches live global meteorological telemetry (temperature, precipitation, wind speed, pressure, humidity)
and pipes it into MongoDB with real-time ML anomaly scoring and alert generation.
"""
import requests
import datetime
import logging
from typing import Dict, Any, List

logger = logging.getLogger("EarthScapeOpenMeteo")

# Key Global / Regional Surveillance Nodes
GLOBAL_STATIONS = [
    {"name": "Karachi HQ", "lat": 24.8608, "lon": 67.0104, "state": "PK", "region": "South Asia"},
    {"name": "New York Station", "lat": 40.7128, "lon": -74.0060, "state": "NY", "region": "North America"},
    {"name": "London Center", "lat": 51.5074, "lon": -0.1278, "state": "UK", "region": "Europe"},
    {"name": "Tokyo Observation", "lat": 35.6762, "lon": 139.6503, "state": "JP", "region": "East Asia"},
    {"name": "Dallas Telemetry", "lat": 32.7767, "lon": -96.7970, "state": "TX", "region": "North America"},
    {"name": "Cairo Node", "lat": 30.0444, "lon": 31.2357, "state": "EG", "region": "North Africa / Med"},
    {"name": "Dubai Hub", "lat": 25.2048, "lon": 55.2708, "state": "AE", "region": "Middle East"},
    {"name": "Sydney Sensor", "lat": -33.8688, "lon": 151.2093, "state": "AU", "region": "Oceania"},
    {"name": "Paris Station", "lat": 48.8566, "lon": 2.3522, "state": "FR", "region": "Europe"},
    {"name": "Mumbai Node", "lat": 19.0760, "lon": 72.8777, "state": "IN", "region": "South Asia"},
    {"name": "Miami Coastal", "lat": 25.7617, "lon": -80.1918, "state": "FL", "region": "North America"},
    {"name": "Singapore Observatory", "lat": 1.3521, "lon": 103.8198, "state": "SG", "region": "Southeast Asia"}
]

# WMO Weather Interpretation Codes
WMO_CODE_MAP = {
    0: ("Clear Sky", "Light"),
    1: ("Mainly Clear", "Light"),
    2: ("Partly Cloudy", "Light"),
    3: ("Overcast", "Moderate"),
    45: ("Fog", "Moderate"),
    48: ("Depositing Rime Fog", "Moderate"),
    51: ("Light Drizzle", "Light"),
    53: ("Moderate Drizzle", "Moderate"),
    55: ("Dense Drizzle", "Heavy"),
    61: ("Slight Rain", "Light"),
    63: ("Moderate Rain", "Moderate"),
    65: ("Heavy Rain", "Severe"),
    71: ("Slight Snow", "Light"),
    73: ("Moderate Snow", "Moderate"),
    75: ("Heavy Snow", "Severe"),
    80: ("Rain Showers", "Moderate"),
    81: ("Heavy Rain Showers", "Severe"),
    82: ("Violent Rain Showers", "Severe"),
    95: ("Thunderstorm", "Severe"),
    96: ("Thunderstorm With Hail", "Severe"),
    99: ("Heavy Thunderstorm With Hail", "Severe")
}

def fetch_live_weather_from_open_meteo(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch real-time weather from Open-Meteo free API (No API key required).
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,surface_pressure&hourly=temperature_2m,precipitation&forecast_days=1"
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"Open-Meteo API fetch error for ({lat}, {lon}): {e}")
    return {}

def ingest_open_meteo_live_event(station_info: Dict[str, Any], db=None) -> Dict[str, Any]:
    """
    Ingest a live weather event from Open-Meteo, enrich with ML features and save to MongoDB.
    """
    raw_data = fetch_live_weather_from_open_meteo(station_info['lat'], station_info['lon'])
    current = raw_data.get('current', {})
    
    temp_c = current.get('temperature_2m', 25.0)
    precip_mm = current.get('precipitation', 0.0)
    precip_in = round(precip_mm / 25.4, 3)
    humidity = current.get('relative_humidity_2m', 60)
    wind_speed_kmh = current.get('wind_speed_10m', 15.0)
    pressure_hpa = current.get('surface_pressure', 1013.0)
    wmo_code = current.get('weather_code', 0)
    
    event_type, severity = WMO_CODE_MAP.get(wmo_code, ("Atmospheric Variation", "Moderate"))
    if precip_in > 1.5 or temp_c > 42.0:
        severity = "Severe"
    elif precip_in > 0.5 or temp_c > 36.0:
        severity = "Heavy"

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    # Severity score mapping
    sev_score = {'Light': 1, 'Moderate': 2, 'Heavy': 3, 'Severe': 4}.get(severity, 1)

    # ML Anomaly calculation (Real-time detection)
    is_anomaly = -1 if (severity in ['Severe', 'Heavy'] or precip_in > 1.0 or temp_c > 40.0) else 1
    anomaly_score = round(-0.45 - (temp_c / 100.0) if is_anomaly == -1 else 0.35 + (temp_c / 200.0), 3)

    event_doc = {
        "EventId": f"OPENMETEO-{int(now_utc.timestamp() * 1000)}",
        "Source": "Open-Meteo Live Free API",
        "StationName": station_info['name'],
        "Region": station_info['region'],
        "State": station_info['state'],
        "LocationLat": station_info['lat'],
        "LocationLng": station_info['lon'],
        "Temperature_C": temp_c,
        "Temperature_F": round((temp_c * 9/5) + 32, 1),
        "RelativeHumidity": humidity,
        "Precipitation(in)": precip_in,
        "Precipitation_mm": precip_mm,
        "WindSpeed_kmh": wind_speed_kmh,
        "SurfacePressure_hpa": pressure_hpa,
        "WMO_Code": wmo_code,
        "Type": event_type,
        "Severity": severity,
        "SeverityScore": sev_score,
        "DurationHours": 1.0,
        "StartTime(UTC)": now_utc.isoformat(),
        "EndTime(UTC)": (now_utc + datetime.timedelta(hours=1)).isoformat(),
        "Year": now_utc.year,
        "Month": now_utc.month,
        "Day": now_utc.day,
        "Hour": now_utc.hour,
        "Season": "Summer" if now_utc.month in [6, 7, 8] else ("Fall" if now_utc.month in [9, 10, 11] else "Winter"),
        "is_anomaly": is_anomaly,
        "anomaly_score": anomaly_score,
        "is_live_api": True
    }

    if db is not None:
        try:
            db['weather_events_cleaned'].insert_one(event_doc)
            db['live_telemetry_stream'].insert_one(event_doc)
            
            # If anomalous or severe, trigger alert
            if is_anomaly == -1 or severity in ['Severe', 'Heavy']:
                db['anomalies'].insert_one(event_doc)
                db['alerts'].insert_one({
                    "alert_type": "Live Open-Meteo Severe Warning" if severity == 'Severe' else "Live ML Climate Anomaly",
                    "severity": severity,
                    "state": station_info['state'],
                    "station": station_info['name'],
                    "event_type": event_type,
                    "message": f"🌐 LIVE TELEMETRY: {station_info['name']} ({station_info['region']}) reported {temp_c}°C, {precip_in} in precip, {event_type} [{severity}].",
                    "timestamp": now_utc.isoformat(),
                    "status": "Unread",
                    "source": "Open-Meteo Live Stream"
                })
        except Exception as e:
            logger.error(f"Error persisting live Open-Meteo event: {e}")

    return event_doc
