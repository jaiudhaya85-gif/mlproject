import os
import time
import requests
from datetime import datetime

# Path to honeyfile
HONEYFILE_PATH = "honeyfile.txt"

# Backend API endpoint to create alert
API_URL = "http://127.0.0.1:5000/create-alert"

# Admin token (you can generate using login)
ADMIN_TOKEN = "YOUR_ADMIN_JWT_TOKEN"

# Store last modified time
last_modified = os.path.getmtime(HONEYFILE_PATH)

print("🔥 Honeyfile Monitor Started...")

while True:
    try:
        current_modified = os.path.getmtime(HONEYFILE_PATH)

        if current_modified != last_modified:
            print("🚨 Honeyfile Access Detected!")

            # Send alert to backend
            requests.post(
                API_URL,
                json={
                    "username": "unknown",
                    "alert_type": "honeyfile_access",
                    "description": "Unauthorized access to honeyfile detected"
                },
                headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
            )

            last_modified = current_modified

    except Exception as e:
        print("Error:", e)

    time.sleep(2)
