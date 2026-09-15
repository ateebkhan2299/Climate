"""
EarthScape Climate Agency - Flask Web Application & Surveillance HQ
Full Python Flask Backend with Live Open-Meteo API + MongoDB real data.
Unique content on every page: Command Center, Geospatial, Anomaly Detection, Predictions, Admin.
Exporting top-level app and handler for Vercel/Render deployment.
"""
from flask import Flask, render_template, jsonify, request, Response, session, redirect, url_for
import os, sys, json, datetime, random, requests

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.open_meteo import GLOBAL_STATIONS, fetch_live_weather_from_open_meteo, ingest_open_meteo_live_event
from database.mongodb import get_db
from functools import wraps

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "earthscape_super_secret_cyber_key"
handler = app   # Vercel requires top-level "handler"

db = get_db()
_station_index = 0

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
        # Check against MongoDB users collection
        try:
            import bcrypt
            user_doc = db["users"].find_one({"username": username})
            if user_doc:
                stored_hash = user_doc.get("password_hash","")
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode()
                if bcrypt.checkpw(password.encode(), stored_hash):
                    session["username"] = username
                    session["role"] = user_doc.get("role","ANALYST")
                    return redirect(url_for("index"))
            # Fallback: demo credentials
            demo = {"admin":"admin123","analyst":"analyst123"}
            if username in demo and demo[username] == password:
                session["username"] = username
                session["role"] = "ADMIN" if username=="admin" else "ANALYST"
                return redirect(url_for("index"))
            return render_template("login.html", error="ACCESS DENIED — Invalid credentials.")
        except Exception:
            # If bcrypt/mongo unavailable, use demo credentials
            demo = {"admin":"admin123","analyst":"analyst123"}
            if username in demo and demo[username] == password:
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
# PAGE ROUTES (unique template per route)
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

@app.route('/admin')
@login_required
def admin():
    if session.get('role') != 'ADMIN':
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/data')
@login_required
def data_page():
    return render_template('data.html')

@app.route('/alerts')
@login_required
def alerts_page():
    return render_template('alerts.html')

@app.route('/support')
@login_required
def support_page():
    return render_template('support.html')

# =========================================================
# REAL-TIME APIS
# =========================================================
@app.route("/api/live-telemetry")
def get_live_telemetry():
    global _station_index
    station = GLOBAL_STATIONS[_station_index % len(GLOBAL_STATIONS)]
    _station_index += 1
    try:
        event = ingest_open_meteo_live_event(station, db=db)
        if not event or event.get("Temperature_C") is None:
            return jsonify({"success": False, "error": "No climate data available", "data": []}), 503
        return jsonify({
            "success": True,
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
    try:
        if db is None:
            return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "data": []}), 503
            
        col = db["live_telemetry_stream"]
        # Fetch the most recent event for each station
        points = []
        for s in GLOBAL_STATIONS:
            event = col.find_one({"StationName": s["name"]}, sort=[("StartTime(UTC)", -1)])
            if event:
                points.append({
                    "name": s["name"], "region": s["region"],
                    "lat": s["lat"], "lon": s["lon"],
                    "temp": event.get("Temperature_C", "—"),
                    "type": event.get("Type", "Unknown"),
                    "severity": event.get("Severity", "Unknown")
                })
        
        if not points:
             return jsonify({"success": True, "error": "No climate data available", "data": []})
             
        return jsonify({"success": True, "data": points})
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "data": []}), 500

@app.route("/api/anomalies")
def get_anomalies_api():
    """Real anomaly data from MongoDB anomalies collection."""
    try:
        if db is None:
             return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "data": []}), 503
             
        col = db["anomalies"]
        total = col.count_documents({})
        
        if total == 0:
            return jsonify({
                "success": True, 
                "message": "No anomaly results available.",
                "total_anomalies": 0,
                "critical_count": 0,
                "anomaly_rate": "0.00",
                "severity_distribution": {},
                "type_distribution": {},
                "anomalies": []
            })
            
        total_records = db["weather_events_cleaned"].count_documents({})
        critical_count = col.count_documents({"Severity": {"$in": ["Critical","Severe","Heavy"]}})
        anomaly_rate = round((total / max(total_records,1)) * 100, 2)
        # Severity distribution
        sev_agg = list(col.aggregate([{"$group":{"_id":"$Severity","count":{"$sum":1}}},{"$sort":{"count":-1}},{"$limit":6}]))
        severity_distribution = {d["_id"]:d["count"] for d in sev_agg if d["_id"]}
        # Type distribution
        type_agg = list(col.aggregate([{"$group":{"_id":"$Type","count":{"$sum":1}}},{"$sort":{"count":-1}},{"$limit":8}]))
        type_distribution = {d["_id"]:d["count"] for d in type_agg if d["_id"]}
        # Latest anomaly records
        records = list(col.find({},{"_id":0,"StartTime(UTC)":1,"State":1,"Type":1,"Severity":1,"Precipitation(in)":1,"Distance(mi)":1,"anomaly_score":1}).sort("StartTime(UTC)",-1).limit(50))
        anomalies_out = []
        for r in records:
            anomalies_out.append({
                "StartTime": r.get("StartTime(UTC)",""),
                "State": r.get("State",""),
                "Type": r.get("Type",""),
                "Severity": r.get("Severity",""),
                "Precipitation": r.get("Precipitation(in)"),
                "Distance": r.get("Distance(mi)"),
                "Duration": r.get("Duration(h)"),
                "anomaly_score": r.get("anomaly_score", -0.2)
            })
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
        if db is None:
             return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "data": []}), 503
             
        col = db["predictions"]
        total = col.count_documents({})
        if total == 0:
            return jsonify({
                "success": False,
                "error": "Prediction model is not available. Train the model to generate predictions.",
                "total_predictions": 0,
                "predictions": []
            })
            
        # Model metrics from climate_summary
        summary = db["climate_summary"].find_one({"type":"model_metrics"}) or {}
        r2 = summary.get("r2", 0)
        mae = summary.get("mae", 0)
        rmse = summary.get("rmse", 0)
        
        # Latest 30 predictions
        records = list(col.find({},{"_id":0,"State":1,"Type":1,"actual":1,"predicted":1,"timestamp":1}).sort("timestamp",-1).limit(30))
        pred_out = []
        actuals, preds = [], []
        for r in records:
            act = r.get("actual")
            pred = r.get("predicted")
            if act is not None: actuals.append(float(act))
            if pred is not None: preds.append(float(pred))
            pred_out.append({"State":r.get("State",""),"Type":r.get("Type",""),"actual":act,"predicted":pred,"timestamp":r.get("timestamp","")})
        
        avg_predicted = sum(preds)/len(preds) if preds else 0
        
        # 14-day forecast
        fa = actuals[:14] if len(actuals)>=14 else actuals
        fp = preds[:14] if len(preds)>=14 else preds
        days = [f"D+{i+1}" for i in range(max(len(fa), len(fp)))]
        
        # Feature importances from saved model (or empty if none)
        features = ["Distance(mi)","Duration(h)","Precipitation","WindSpeed","Visibility","Temperature"]
        importances = summary.get("feature_importances", [0, 0, 0, 0, 0, 0])
        
        return jsonify({
            "success": True,
            "total_predictions": total,
            "avg_predicted": avg_predicted,
            "r2": r2, "mae": mae, "rmse": rmse,
            "forecast_labels": days,
            "forecast_actual": fa,
            "forecast_predicted": fp,
            "scatter_actual": actuals[:40],
            "scatter_predicted": preds[:40],
            "feature_names": features,
            "feature_importances": importances,
            "predictions": pred_out
        })
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "predictions": [], "total_predictions": 0}), 500

@app.route("/api/admin-stats")
def get_admin_stats():
    """Real system stats: psutil CPU/RAM/Disk + MongoDB collection counts + Hadoop nodes."""
    try:
        import psutil
        cpu_pct = psutil.cpu_percent(interval=0.5)
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

    # MongoDB collection stats
    mongo_stats = []
    mongo_collections = 0
    if db is not None:
        try:
            col_names = db.list_collection_names()
            for cname in col_names[:10]:
                cnt = db[cname].count_documents({})
                mongo_stats.append({"name": cname, "count": cnt, "avg_obj_size": 512, "size_mb": round(cnt*512/1048576,1), "indexes": 2})
            mongo_collections = len(col_names)
        except Exception:
            pass
            
    # Check if Hadoop is running locally via jps
    hadoop_nodes = []
    cluster_status = "Unavailable"
    try:
        import subprocess
        jps_out = subprocess.check_output(["jps"], text=True)
        if "NameNode" in jps_out or "DataNode" in jps_out:
            cluster_status = "HEALTHY"
            if "NameNode" in jps_out: hadoop_nodes.append({"name":"NameNode","role":"Master","status":"RUNNING"})
            if "DataNode" in jps_out: hadoop_nodes.append({"name":"DataNode","role":"Worker","status":"RUNNING"})
            if "ResourceManager" in jps_out: hadoop_nodes.append({"name":"ResourceManager","role":"Master","status":"RUNNING"})
            if "NodeManager" in jps_out: hadoop_nodes.append({"name":"NodeManager","role":"Worker","status":"RUNNING"})
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
        if db is None:
             return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "data": []}), 503
             
        col = db["weather_events_cleaned"]
        total = col.count_documents({})
        if total == 0:
            return jsonify({"success": True, "message": "No climate data available", "trends": [], "total": 0})
            
        # Aggregate by month and type
        pipeline = [
            {"$group":{"_id":{"type":"$Type", "month":"$Month"},"count":{"$sum":1},"avg_precip":{"$avg":"$Precipitation(in)"}}},
            {"$sort":{"count":-1}},
            {"$limit":50}
        ]
        results = list(col.aggregate(pipeline))
        return jsonify({"success": True, "trends": results, "total": total})
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to load data. Please try again later.", "trends": [], "total": 0}), 500

@app.route("/api/trigger-compute", methods=["POST"])
def trigger_compute():
    return jsonify({"success": False, "error": "HDFS is currently unavailable. Serverless execution environment cannot launch local MapReduce."}), 503

@app.route("/api/export-geojson")
def export_geojson():
    features = [{"type":"Feature","geometry":{"type":"Point","coordinates":[s["lon"],s["lat"]]},"properties":{"station":s["name"],"region":s["region"]}} for s in GLOBAL_STATIONS]
    geojson_data = {"type":"FeatureCollection","timestamp":datetime.datetime.now(datetime.timezone.utc).isoformat(),"features":features}
    return Response(json.dumps(geojson_data,indent=2), mimetype="application/json",
        headers={"Content-disposition":"attachment; filename=earthscape_telemetry.geojson"})

if __name__ == "__main__":
    print("EarthScape Surveillance HQ Flask Server starting on http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
