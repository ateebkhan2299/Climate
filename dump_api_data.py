import os
import json
from app import app

# Ensure fallback directory exists
output_dir = os.path.join(os.path.dirname(__file__), "static", "fallback_data")
os.makedirs(output_dir, exist_ok=True)

endpoints = [
    "/api/anomalies",
    "/api/predictions",
    "/api/analytics-trends",
    "/api/admin-stats",
    "/api/kpis",
    "/api/alerts"
]

print("Dumping real MongoDB data to fallback JSON files for Vercel...")

with app.test_client() as client:
    for endpoint in endpoints:
        response = client.get(endpoint)
        if response.status_code == 200:
            data = response.get_json()
            filename = endpoint.split("/")[-1] + ".json"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[SUCCESS] Dumped {endpoint} to {filename}")
        else:
            print(f"[FAILED] Could not dump {endpoint}, status: {response.status_code}")

print("Done!")
