"""
Mock ESP32 Sensor Simulator – Demo Plant (ESP32_DEMO_001)
==========================================================
Generates realistic sensor data for the seeded demo plant and posts it to
the FloraPulse backend.

The demo sensor 'ESP32_DEMO_001' is automatically seeded by the backend on
every startup, so this script should never get a 404.  If for some reason
the sensor is missing it will re-register itself automatically.

Usage:
    python simulate_esp32.py

No arguments required – uses the built-in demo credentials.
"""

import requests
import random
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL     = "http://localhost:8000"
UPLOAD_URL   = f"{BASE_URL}/api/sensor-data/upload"
LOGIN_URL    = f"{BASE_URL}/api/auth/login"
REGISTER_URL = f"{BASE_URL}/api/sensors/register"
PLANTS_URL   = f"{BASE_URL}/api/plants/my-plants"

SENSOR_ID     = "ESP32_DEMO_001"
DEMO_USER     = "demo"
DEMO_PASS     = "demo123"

POLL_INTERVAL  = 10    # seconds
MAX_ITERATIONS = None  # None = run forever

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

def login() -> str | None:
    """Log in as the demo user and return the JWT access token."""
    try:
        resp = requests.post(
            LOGIN_URL,
            json={"username": DEMO_USER, "password": DEMO_PASS},
            timeout=5,
        )
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            print(f"✅ Logged in as '{DEMO_USER}'")
            return token
        print(f"⚠️  Login failed ({resp.status_code}): {resp.text}")
        return None
    except requests.RequestException as e:
        print(f"⚠️  Login request error: {e}")
        return None


def get_first_plant_id(token: str) -> int | None:
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
    except requests.RequestException:
        pass
    return None


def ensure_sensor_registered(token: str) -> bool:
    """
    Make sure ESP32_DEMO_001 is registered.  The backend seeds it on
    startup, but this acts as a safety net.
    """
    plant_id = get_first_plant_id(token)
    if plant_id is None:
        print("⚠️  No plants found for demo user – cannot auto-register sensor.")
        return False

    try:
        resp = requests.post(
            REGISTER_URL,
            data={"sensor_id": SENSOR_ID, "plant_id": plant_id},
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.status_code == 200:
            status = resp.json().get("status", "")
            if status == "already_registered":
                print(f"ℹ️  Sensor '{SENSOR_ID}' already registered (plant {plant_id})")
            else:
                print(f"✅ Sensor '{SENSOR_ID}' registered to plant {plant_id}")
            return True
        print(f"⚠️  Sensor registration response ({resp.status_code}): {resp.text}")
        return False
    except requests.RequestException as e:
        print(f"⚠️  Sensor registration error: {e}")
        return False


def generate_reading() -> dict:
    return {
        "sensor_id":     SENSOR_ID,
        "moisture":      round(random.uniform(MOISTURE_MIN, MOISTURE_MAX), 1),
        "temperature":   round(random.uniform(TEMP_MIN, TEMP_MAX), 1),
        "humidity":      round(random.uniform(HUM_MIN, HUM_MAX), 1),
        "rain_detected": random.random() < RAIN_PROB,
    }


def post_reading(data: dict) -> tuple[bool, dict]:
    """Post data; return (success, response_body)."""
    try:
        resp = requests.post(UPLOAD_URL, json=data, timeout=5)
        if resp.status_code == 200:
            return True, resp.json()
        return False, {"error": resp.text, "status_code": resp.status_code}
    except requests.RequestException as e:
        return False, {"error": str(e)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("🌱 FloraPulse Demo ESP32 Simulator")
    print(f"🔌 Sensor ID  : {SENSOR_ID}")
    print(f"📤 Upload URL : {UPLOAD_URL}")
    print(f"⏱️  Interval   : {POLL_INTERVAL}s")
    print("─" * 50)

    # Attempt to log in; if it fails we still try posting (sensor may be
    # pre-seeded and no auth is needed for the upload endpoint).
    token = login()
    if token:
        ensure_sensor_registered(token)
    else:
        print("⚠️  Proceeding without login – sensor must already be in the DB.")

    print(f"\n🔄 Streaming data … (Ctrl+C to stop)\n")

    iteration = 0
    consecutive_404 = 0

    try:
        while True:
            if MAX_ITERATIONS and iteration >= MAX_ITERATIONS:
                print(f"\n✅ Completed {MAX_ITERATIONS} iterations. Stopping.")
                break

            iteration += 1
            data           = generate_reading()
            success, body  = post_reading(data)

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

            # If we get 404, try to re-register once
            if not success and body.get("status_code") == 404:
                consecutive_404 += 1
                print(f"   ⚠️  404 received – attempting re-registration …")
                if token:
                    ensure_sensor_registered(token)
                else:
                    token = login()
                    if token:
                        ensure_sensor_registered(token)
                if consecutive_404 >= 3:
                    print("❌ Repeated 404s – giving up. Check the backend.")
                    break
            else:
                consecutive_404 = 0

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped after {iteration} posts.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()