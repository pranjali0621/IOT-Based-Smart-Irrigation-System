"""
Mock ESP32 Sensor Simulator - New Plant
========================================
Generates realistic sensor data and posts it to the FloraPulse backend.

Usage:
    python simulate_esp32_new_plant.py <sensor_id> <plant_id> <username> <password>

    sensor_id  – the sensor ID string used when you created the plant
                 (e.g. ESP32_NEW_001)
    plant_id   – the numeric plant ID returned after creation
                 (visible in the /api/plants/my-plants response)
    username   – your FloraPulse account username
    password   – your FloraPulse account password

Example:
    python simulate_esp32_new_plant.py ESP32_NEW_001 2 new mypassword
"""

import requests
import random
import time
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL      = "http://localhost:8000"
UPLOAD_URL    = f"{BASE_URL}/api/sensor-data/upload"
LOGIN_URL     = f"{BASE_URL}/api/auth/login"
REGISTER_URL  = f"{BASE_URL}/api/sensors/register"
PLANTS_URL    = f"{BASE_URL}/api/plants/my-plants"

POLL_INTERVAL   = 10    # seconds between readings
MAX_ITERATIONS  = None  # None = run forever

# Realistic sensor ranges
MOISTURE_MIN = 25
MOISTURE_MAX = 75
TEMP_MIN     = 18
TEMP_MAX     = 35
HUM_MIN      = 30
HUM_MAX      = 85
RAIN_PROB    = 0.15


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login(username: str, password: str) -> str | None:
    """Log in and return the JWT access token, or None on failure."""
    try:
        resp = requests.post(
            LOGIN_URL,
            json={"username": username, "password": password},
            timeout=5,
        )
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            print(f"✅ Logged in as '{username}'")
            return token
        else:
            print(f"❌ Login failed ({resp.status_code}): {resp.text}")
            return None
    except requests.RequestException as e:
        print(f"❌ Login request error: {e}")
        return None


def fetch_plant_id(token: str) -> int | None:
    """
    Fetch the first plant that belongs to the authenticated user.
    Returns the plant ID, or None if no plants found.
    """
    try:
        resp = requests.get(
            PLANTS_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.status_code == 200:
            plants = resp.json().get("plants", [])
            if plants:
                return plants[0]["id"]
        return None
    except requests.RequestException:
        return None


def register_sensor(token: str, sensor_id: str, plant_id: int) -> bool:
    """
    Register the sensor against the given plant. Safe to call even when
    the sensor is already registered (returns 'already_registered').
    """
    try:
        resp = requests.post(
            REGISTER_URL,
            data={"sensor_id": sensor_id, "plant_id": plant_id},
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.status_code == 200:
            status = resp.json().get("status", "")
            if status == "already_registered":
                print(f"ℹ️  Sensor '{sensor_id}' already registered to plant {plant_id}")
            else:
                print(f"✅ Sensor '{sensor_id}' registered to plant {plant_id}")
            return True
        else:
            print(f"❌ Sensor registration failed ({resp.status_code}): {resp.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Registration request error: {e}")
        return False


def generate_reading(sensor_id: str) -> dict:
    return {
        "sensor_id":   sensor_id,
        "moisture":    round(random.uniform(MOISTURE_MIN, MOISTURE_MAX), 1),
        "temperature": round(random.uniform(TEMP_MIN, TEMP_MAX), 1),
        "humidity":    round(random.uniform(HUM_MIN, HUM_MAX), 1),
        "rain_detected": random.random() < RAIN_PROB,
    }


def post_reading(data: dict) -> bool:
    try:
        resp = requests.post(UPLOAD_URL, json=data, timeout=5)
        return resp.status_code == 200
    except requests.RequestException as e:
        print(f"❌ Upload error: {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(sensor_id: str, plant_id: int | None, username: str, password: str):
    print("🌱 FloraPulse New-Plant ESP32 Simulator")
    print(f"🔌 Sensor ID  : {sensor_id}")
    print(f"📤 Upload URL : {UPLOAD_URL}")
    print(f"⏱️  Interval   : {POLL_INTERVAL}s")
    print("─" * 50)

    # Step 1 – authenticate
    token = login(username, password)
    if not token:
        print("❌ Cannot continue without a valid token.")
        sys.exit(1)

    # Step 2 – resolve plant_id if not provided
    if plant_id is None:
        plant_id = fetch_plant_id(token)
        if plant_id is None:
            print(
                "❌ No plants found for this user. "
                "Add a plant via the web app first."
            )
            sys.exit(1)
        print(f"ℹ️  Using first plant found: plant_id={plant_id}")

    # Step 3 – register sensor (idempotent)
    if not register_sensor(token, sensor_id, plant_id):
        print("❌ Cannot continue without a registered sensor.")
        sys.exit(1)

    print(f"\n🔄 Streaming data … (Ctrl+C to stop)\n")

    iteration = 0
    try:
        while True:
            if MAX_ITERATIONS and iteration >= MAX_ITERATIONS:
                print(f"\n✅ Completed {MAX_ITERATIONS} iterations. Stopping.")
                break

            iteration += 1
            data    = generate_reading(sensor_id)
            success = post_reading(data)

            ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            icon = "✅" if success else "❌"
            rain = "🌧️  " if data["rain_detected"] else ""
            print(
                f"{icon} [{ts}] #{iteration} | "
                f"Moisture: {data['moisture']}% | "
                f"Temp: {data['temperature']}°C | "
                f"Humidity: {data['humidity']}% | "
                f"{rain}"
            )
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped after {iteration} posts.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(__doc__)
        print(
            "Usage: python simulate_esp32_new_plant.py "
            "<sensor_id> <plant_id> <username> <password>"
        )
        print(
            "       python simulate_esp32_new_plant.py "
            "<sensor_id> auto <username> <password>   "
            "(auto-detects your first plant)"
        )
        sys.exit(1)

    _sensor_id = sys.argv[1]
    _plant_arg = sys.argv[2]
    _username  = sys.argv[3]
    _password  = sys.argv[4]

    _plant_id = None if _plant_arg.lower() == "auto" else int(_plant_arg)

    main(_sensor_id, _plant_id, _username, _password)