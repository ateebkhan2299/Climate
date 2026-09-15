"""
EarthScape Climate Agency - Flask Web Application
Full Python Flask Backend with Live Open-Meteo API + MongoDB real data.
Complete SRS-compliant implementation: Dashboard, Analytics, Anomalies,
Predictions, Alerts, Data, Admin, Support pages.
Vercel serverless deployment compatible (with static fallback if no Mongo).
"""
from flask import Flask, render_template, jsonify, request, Response, session, redirect, url_for
import os, sys, json, datetime, requests
from functools import wraps

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.open_meteo import GLOBAL_STATIONS, fetch_live_weather_from_open_meteo, ingest_open_meteo_live_event
from database.mongodb import get_db

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "earthscape_super_secret_cyber_key")
app.permanent_session_lifetime = datetime.timedelta(hours=8)  # Session timeout 8 hours
handler = app   # Vercel requires top-level "handler"

# Lazy DB connection — do NOT connect at module import time (causes Vercel timeout)
_db_instance = None
_station_index = 0

def get_db_conn():
    """Get DB connection, connecting lazily on first use."""
    global _db_instance
    if _db_instance is None:
        _db_instance = get_db()
    return _db_instance

def get_fallback_data(filename):
    """Vercel Fallback: Returns real ML data from static JSON if MongoDB is not connected."""
    filepath = os.path.join(app.static_folder, "fallback_data", filename)
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# =========================================================
# AUTH ROUTES
# =========================================================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        db = get_db_conn()
        # Check against MongoDB users collection
        try:
            import bcrypt
            if db is not None:
                user_doc = db["users"].find_one({"username": username})
                if user_doc:
                    stored_hash = user_doc.get("password_hash","")
                    if isinstance(stored_hash, str):
                        stored_hash = stored_hash.encode()
                    if bcrypt.checkpw(password.encode(), stored_hash):
                        session.permanent = True
                        session["username"] = username
                        session["role"] = user_doc.get("role","ANALYST")
                        return redirect(url_for("index"))
        except Exception:
            pass
        # Fallback: demo credentials
        demo = {"admin":"admin123","analyst":"analyst123"}
        if username in demo and demo[username] == password:
            session.permanent = True
            session["username"] = username
            session["role"] = "ADMIN" if username=="admin" else "ANALYST"
            return redirect(url_for("index"))
        return render_template("login.html", error="ACCESS DENIED — Invalid credentials.")
    return render_template("login.html", error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =========================================================
# PAGE ROUTES
# =========================================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analytics")
def analytics_view():
    return render_template("analytics.html")

@app.route("/anomalies")
def anomalies_view():
    return render_template("anomalies.html")

@app.route("/predictions")
def predictions_view():
    return render_template("predictions.html")

@app.route("/admin")
@login_required
def admin():
    if session.get("role") != "ADMIN":
        return redirect(url_for("index"))
    return render_template("admin.html")

@app.route("/data")
def data_page():
    return render_template("data.html")

@app.route("/alerts")
def alerts_page():
    return render_template("alerts.html")

@app.route("/support")
def support_page():
    return render_template("support.html")

# =========================================================
# REAL-TIME APIS
# =========================================================
@app.route("/api/live-telemetry")
def get_live_telemetry():
    global _station_index
    station = GLOBAL_STATIONS[_station_index % len(GLOBAL_STATIONS)]
    _station_index += 1
    try:
        db = get_db_conn()
        event = ingest_open_meteo_live_event(station, db=db)
        if not event or event.get("Temperature_C") is None:
            return jsonify({"success": False, "error": "No climate data available", "data": []}), 503
        return jsonify({
            "success": True,
            "station_count": len(GLOBAL_STATIONS),
            "data": {
                "station": event.get("StationName"),
                "region": event.get("Region"),
                "lat": event.get("LocationLat"),
                "lon": event.get("LocationLng"),
                "temp": event.get("Temperature_C"),
                "temp_f": event.get("Temperature_F"),
                "humidity": event.get("RelativeHumidity"),
                "precip_in": event.get("Precipitation(in)"),
                "wind_speed": event.get("WindSpeed_kmh"),
                "pressure": event.get("SurfacePressure_hpa"),
                "type": event.get("Type"),
                "severity": event.get("Severity"),
                "is_anomaly": event.get("is_anomaly"),
                "timestamp": event.get("StartTime(UTC)")
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "data": []}), 500

@app.route("/api/radar-points")
def get_radar_points():
    """Return all global station coordinates for geospatial map."""
    try:
        db = get_db_conn()
        col = db["live_telemetry_stream"] if db is not None else None
        points = []
        for s in GLOBAL_STATIONS:
            point = {
                "name": s["name"], "region": s["region"],
                "lat": s["lat"], "lon": s["lon"],
                "temp": "—", "type": "Unknown", "severity": "Normal"
            }
            if col is not None:
                try:
                    event = col.find_one({"StationName": s["name"]}, sort=[("StartTime(UTC)", -1)])
                    if event:
                        point["temp"] = event.get("Temperature_C", "—")
                        point["type"] = event.get("Type", "Unknown")
                        point["severity"] = event.get("Severity", "Normal")
                except Exception:
                    pass
            points.append(point)
        return jsonify({"success": True, "data": points, "total": len(points)})
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to load data.", "data": []}), 500

@app.route("/api/anomalies")
def get_anomalies_api():
    """Real anomaly data from MongoDB anomalies collection."""
    try:
        db = get_db_conn()
        if db is None:
            fb = get_fallback_data("anomalies.json")
            if fb: return jsonify(fb)
            return jsonify({"success": False, "error": "Database unavailable. Run ml/train_models.py to populate.", "data": []}), 503

        col = db["anomalies"]
        total = col.count_documents({})

        if total == 0:
            return jsonify({
                "success": True,
                "message": "No anomaly results. Run ml/train_models.py to generate.",
                "total_records": 0,
                "total_anomalies": 0,
                "critical_count": 0,
                "anomaly_rate": "0.00",
                "severity_distribution": {},
                "type_distribution": {},
                "anomalies": []
            })

        total_records = db["weather_events_cleaned"].count_documents({})
        critical_count = col.count_documents({"Severity": {"$in": ["Critical","Severe","Heavy"]}})
        anomaly_rate = round((total / max(total_records, 1)) * 100, 2)

        sev_agg = list(col.aggregate([
            {"$group": {"_id": "$Severity", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}, {"$limit": 6}
        ]))
        severity_distribution = {d["_id"]: d["count"] for d in sev_agg if d["_id"]}

        type_agg = list(col.aggregate([
            {"$group": {"_id": "$Type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}, {"$limit": 8}
        ]))
        type_distribution = {d["_id"]: d["count"] for d in type_agg if d["_id"]}

        records = list(col.find(
            {}, {"_id": 0, "StartTime(UTC)": 1, "State": 1, "Type": 1,
                 "Severity": 1, "Precipitation(in)": 1, "Distance(mi)": 1, "anomaly_score": 1}
        ).sort("StartTime(UTC)", -1).limit(50))

        anomalies_out = [{
            "StartTime": r.get("StartTime(UTC)", ""),
            "State": r.get("State", ""),
            "Type": r.get("Type", ""),
            "Severity": r.get("Severity", ""),
            "Precipitation": r.get("Precipitation(in)"),
            "Distance": r.get("Distance(mi)"),
            "anomaly_score": r.get("anomaly_score", -0.2)
        } for r in records]

        return jsonify({
            "success": True,
            "total_records": total_records,
            "total_anomalies": total,
            "critical_count": critical_count,
            "anomaly_rate": str(anomaly_rate),
            "severity_distribution": severity_distribution,
            "type_distribution": type_distribution,
            "anomalies": anomalies_out
        })
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "anomalies": [], "total_anomalies": 0}), 500

@app.route("/api/predictions")
def get_predictions_api():
    """Real prediction data from MongoDB predictions collection."""
    try:
        db = get_db_conn()
        if db is None:
            fb = get_fallback_data("predictions.json")
            if fb: return jsonify(fb)
            return jsonify({"success": False, "error": "Database unavailable.", "data": []}), 503

        col = db["predictions"]
        total = col.count_documents({})
        if total == 0:
            return jsonify({
                "success": False,
                "error": "No prediction data. Run ml/train_models.py to generate predictions.",
                "total_predictions": 0, "predictions": []
            })

        # Try new schema first: {metrics: {...}, series: [{Year, Month, EventCount, PredictedCount}, ...]}
        doc = col.find_one({"series": {"$exists": True}})
        if doc:
            metrics = doc.get("metrics", {})
            series = doc.get("series", [])
            r2 = metrics.get("R2", 0)
            mae = metrics.get("MAE", 0)
            rmse = metrics.get("RMSE", 0)

            actuals = [s.get("EventCount", 0) for s in series]
            preds = [s.get("PredictedCount", 0) for s in series]
            labels = [f"{s.get('Year','')}-{str(s.get('Month','')).zfill(2)}" for s in series]

            pred_out = [{
                "State": "Monthly",
                "Type": "Event Frequency",
                "actual": s.get("EventCount"),
                "predicted": s.get("PredictedCount"),
                "timestamp": f"{s.get('Year','')}-{str(s.get('Month','')).zfill(2)}-01"
            } for s in series[-30:]]

            avg_predicted = sum(preds) / len(preds) if preds else 0

            return jsonify({
                "success": True,
                "total_predictions": len(series),
                "avg_predicted": avg_predicted,
                "r2": r2, "mae": mae, "rmse": rmse,
                "forecast_labels": labels[-14:],
                "forecast_actual": actuals[-14:],
                "forecast_predicted": preds[-14:],
                "scatter_actual": actuals[:40],
                "scatter_predicted": preds[:40],
                "feature_names": ["Month", "TimeIndex", "AvgPrecip", "AvgDuration", "AvgSeverity", "Lag_1"],
                "feature_importances": [],
                "predictions": pred_out
            })

        # Fallback: old schema with actual/predicted fields per document
        records = list(col.find({}, {"_id": 0, "State": 1, "Type": 1, "actual": 1, "predicted": 1, "timestamp": 1}).sort("timestamp", -1).limit(30))
        if not records:
            return jsonify({"success": False, "error": "No prediction records found.", "total_predictions": 0, "predictions": []})

        summary = db["climate_summary"].find_one({"type": "model_metrics"}) or {}
        r2 = summary.get("r2", 0)
        mae = summary.get("mae", 0)
        rmse = summary.get("rmse", 0)
        actuals = [float(r["actual"]) for r in records if r.get("actual") is not None]
        preds = [float(r["predicted"]) for r in records if r.get("predicted") is not None]
        avg_predicted = sum(preds) / len(preds) if preds else 0
        labels = [f"D+{i+1}" for i in range(min(14, len(actuals)))]

        return jsonify({
            "success": True,
            "total_predictions": total,
            "avg_predicted": avg_predicted,
            "r2": r2, "mae": mae, "rmse": rmse,
            "forecast_labels": labels,
            "forecast_actual": actuals[:14],
            "forecast_predicted": preds[:14],
            "scatter_actual": actuals[:40],
            "scatter_predicted": preds[:40],
            "feature_names": [],
            "feature_importances": [],
            "predictions": records
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "predictions": [], "total_predictions": 0}), 500

@app.route("/api/admin-stats")
def get_admin_stats():
    """Real system stats: psutil CPU/RAM/Disk + MongoDB collection counts + Hadoop nodes."""
    try:
        import psutil
        cpu_pct = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu_data = {"percent": cpu_pct, "count": cpu_count, "freq_current": cpu_freq.current if cpu_freq else None}
        ram_data = {"percent": ram.percent, "total": ram.total, "used": ram.used, "available": ram.available}
        disk_data = {"percent": disk.percent, "total": disk.total, "used": disk.used, "free": disk.free}
    except Exception:
        cpu_data = None
        ram_data = None
        disk_data = None

    db = get_db_conn()
    if db is None:
        fb = get_fallback_data("admin-stats.json")
        if fb: 
            if cpu_data and fb.get('data'): fb['data']['cpu'] = cpu_data
            if ram_data and fb.get('data'): fb['data']['ram'] = ram_data
            if disk_data and fb.get('data'): fb['data']['disk'] = disk_data
            return jsonify(fb)

    mongo_stats = []
    mongo_collections = 0
    if db is not None:
        try:
            col_names = db.list_collection_names()
            for cname in col_names[:10]:
                cnt = db[cname].count_documents({})
                mongo_stats.append({
                    "name": cname, "count": cnt,
                    "avg_obj_size": 512,
                    "size_mb": round(cnt * 512 / 1048576, 1),
                    "indexes": 2
                })
            mongo_collections = len(col_names)
        except Exception:
            pass

    # Check if Hadoop is running locally via jps
    hadoop_nodes = []
    cluster_status = "Unavailable"
    try:
        import subprocess
        jps_out = subprocess.check_output(["jps"], text=True, timeout=3)
        if "NameNode" in jps_out or "DataNode" in jps_out:
            cluster_status = "HEALTHY"
            if "NameNode" in jps_out:
                hadoop_nodes.append({"name": "NameNode", "role": "Master", "status": "RUNNING"})
            if "DataNode" in jps_out:
                hadoop_nodes.append({"name": "DataNode", "role": "Worker", "status": "RUNNING"})
            if "ResourceManager" in jps_out:
                hadoop_nodes.append({"name": "ResourceManager", "role": "Master", "status": "RUNNING"})
            if "NodeManager" in jps_out:
                hadoop_nodes.append({"name": "NodeManager", "role": "Worker", "status": "RUNNING"})
    except Exception:
        pass

    return jsonify({
        "success": True,
        "data": {
            "cpu": cpu_data, "ram": ram_data, "disk": disk_data,
            "mongo_collections": mongo_collections,
            "mongo_stats": mongo_stats,
            "hadoop_nodes": hadoop_nodes,
            "cluster_status": cluster_status
        }
    })

@app.route("/api/analytics-trends")
def get_analytics_trends():
    """Monthly weather trends from MongoDB for Geospatial Analytics page."""
    try:
        db = get_db_conn()
        if db is None:
            fb = get_fallback_data("analytics-trends.json")
            if fb: return jsonify(fb)
            return jsonify({"success": False, "error": "Database unavailable.", "data": []}), 503

        col = db["weather_events_cleaned"]
        total = col.count_documents({})
        if total == 0:
            return jsonify({"success": True, "message": "No climate data available", "trends": [], "total": 0})

        pipeline = [
            {"$group":{"_id":{"type":"$Type", "month":"$Month"},"count":{"$sum":1},"avg_precip":{"$avg":"$Precipitation(in)"}}},
            {"$sort":{"count":-1}},
            {"$limit":50}
        ]
        results = list(col.aggregate(pipeline))
        return jsonify({"success": True, "trends": results, "total": total})
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "trends": [], "total": 0}), 500

@app.route("/api/alerts")
def get_alerts_api():
    """Real alerts from MongoDB alerts collection."""
    try:
        db = get_db_conn()
        if db is None:
            fb = get_fallback_data("alerts.json")
            if fb: return jsonify(fb)
            return jsonify({"success": False, "error": "Database unavailable.", "alerts": [], "total": 0}), 503
        
        col = db["alerts"]
        total = col.count_documents({})
        unread = col.count_documents({"status": "Unread"})
        critical = col.count_documents({"severity": {"$in": ["Severe", "High", "Critical"]}})
        records = list(col.find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
        return jsonify({
            "success": True,
            "total": total,
            "unread": unread,
            "critical": critical,
            "alerts": records
        })
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to load alerts.", "alerts": [], "total": 0}), 500

@app.route("/api/kpis")
def get_kpis_api():
    """Global KPI summary from MongoDB climate_summary collection."""
    try:
        db = get_db_conn()
        if db is None:
            fb = get_fallback_data("kpis.json")
            if fb: return jsonify(fb)
            return jsonify({"success": False, "error": "Database unavailable."}), 503
        
        doc = db["climate_summary"].find_one({}, {"_id": 0, "kpis": 1, "state_summary": 1, "type_summary": 1, "severity_summary": 1})
        if not doc:
            return jsonify({"success": False, "error": "No summary data available."})
        return jsonify({"success": True, "data": doc})
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to load KPIs."}), 500

@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Save user feedback to MongoDB."""
    try:
        data = request.get_json()
        if not data or not data.get('message'):
            return jsonify({"success": False, "error": "Message is required."}), 400
        db = get_db_conn()
        if db is not None:
            db['feedback'].insert_one({
                "name": data.get('name', 'Anonymous'),
                "email": data.get('email', ''),
                "category": data.get('category', 'General'),
                "message": data.get('message', ''),
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "status": "New"
            })
        return jsonify({"success": True, "message": "Feedback saved."})
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to save feedback."}), 500

@app.route("/api/trigger-compute", methods=["POST"])
def trigger_compute():
    return jsonify({
        "success": False,
        "error": "HDFS is currently unavailable. Serverless execution environment cannot launch local MapReduce."
    }), 503

@app.route("/api/export-geojson")
def export_geojson():
    features = [{
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [s["lon"], s["lat"]]},
        "properties": {"station": s["name"], "region": s["region"]}
    } for s in GLOBAL_STATIONS]
    geojson_data = {
        "type": "FeatureCollection",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "features": features
    }
    return Response(
        json.dumps(geojson_data, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=earthscape_telemetry.geojson"}
    )

if __name__ == "__main__":
    print("EarthScape Flask Server starting on http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
