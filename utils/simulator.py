"""
Real-Time Stream Telemetry Simulator & Live Open-Meteo API Ingestion Engine
Continuously pulls live global weather telemetry from Open-Meteo free API,
evaluates ML anomalies and alerts, and streams updates into MongoDB collections.
"""
import random
import datetime
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from utils.alerts import evaluate_and_generate_alerts
from utils.open_meteo import GLOBAL_STATIONS, ingest_open_meteo_live_event

logger = logging.getLogger("EarthScapeSimulator")

_scheduler = None
_station_index = 0

def stream_next_live_event(db=None):
    """Fetch real-time data from Open-Meteo for next global station."""
    global _station_index
    station = GLOBAL_STATIONS[_station_index % len(GLOBAL_STATIONS)]
    _station_index += 1
    
    try:
        event = ingest_open_meteo_live_event(station, db=db)
        logger.info(f"Ingested live event from {station['name']}: Temp={event.get('Temperature_C')}°C")
        return event
    except Exception as e:
        logger.error(f"Error streaming live Open-Meteo event: {e}")
        return None

def start_telemetry_simulator(db, interval_seconds: int = 5):
    """Start background APScheduler job for streaming live Open-Meteo telemetry."""
    global _scheduler
    if _scheduler is None or not _scheduler.running:
        _scheduler = BackgroundScheduler()
        _scheduler.add_job(
            stream_next_live_event,
            'interval',
            seconds=interval_seconds,
            args=[db],
            id='open_meteo_live_stream',
            replace_existing=True
        )
        _scheduler.start()
        logger.info(f"Started live Open-Meteo streaming engine (interval={interval_seconds}s).")

def stop_telemetry_simulator():
    """Stop background scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Stopped live telemetry stream.")

