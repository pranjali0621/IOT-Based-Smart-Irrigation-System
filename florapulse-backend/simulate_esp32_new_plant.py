"""
Mock ESP32 Sensor Simulator - New Plant Demo

Generates realistic sensor data and posts to backend API.
The sensor ID is provided when starting the simulator.
"""

import requests
import random
import time
import sys
from datetime import datetime


# Configuration
API_URL = "http://localhost:8000/api/sensor-data/upload"
POLL_INTERVAL = 10  # seconds between posts
MAX_ITERATIONS = None  # None = infinite, or set number like 100


# Sensor value ranges
MOISTURE_MIN = 25
MOISTURE_MAX = 75

TEMPERATURE_MIN = 18
TEMPERATURE_MAX = 35

HUMIDITY_MIN = 30
HUMIDITY_MAX = 85

RAIN_PROBABILITY = 0.15


def generate_sensor_data(sensor_id):
    """
    Generate realistic sensor readings.

    Args:
        sensor_id (str): ID of the sensor sending the data.

    Returns:
        dict: Sensor data matching SensorDataRequest schema.
    """

    return {
        "sensor_id": sensor_id,
        "moisture": round(random.uniform(MOISTURE_MIN, MOISTURE_MAX), 1),
        "temperature": round(random.uniform(TEMPERATURE_MIN, TEMPERATURE_MAX), 1),
        "humidity": round(random.uniform(HUMIDITY_MIN, HUMIDITY_MAX), 1),
        "rain_detected": random.random() < RAIN_PROBABILITY
    }


def post_to_api(data):
    """
    POST sensor data to backend API.

    Args:
        data (dict): Sensor reading.

    Returns:
        bool: True if successful, False otherwise.
    """

    try:
        response = requests.post(
            API_URL,
            json=data,
            timeout=5
        )

        return response.status_code == 200

    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return False


def main(sensor_id):
    """
    Main simulator loop.

    Generates and posts sensor data indefinitely
    or until MAX_ITERATIONS.
    """

    print("🌱 FloraPulse New Plant ESP32 Simulator Started")
    print(f"🔌 Sensor ID: {sensor_id}")
    print(f"📤 Posting to: {API_URL}")
    print(f"⏱️  Interval: {POLL_INTERVAL} seconds")
    print("🔄 Press Ctrl+C to stop\n")

    iteration = 0

    try:

        while True:

            # Stop after MAX_ITERATIONS if set
            if MAX_ITERATIONS and iteration >= MAX_ITERATIONS:
                print(
                    f"\n✅ Completed {MAX_ITERATIONS} iterations. Stopping."
                )
                break

            iteration += 1

            # Generate data
            data = generate_sensor_data(sensor_id)

            # Post to API
            success = post_to_api(data)

            # Log result
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            status = "✅" if success else "❌"
            rain = "🌧️ " if data["rain_detected"] else ""

            print(
                f"{status} [{timestamp}] #{iteration} | "
                f"Sensor: {sensor_id} | "
                f"Moisture: {data['moisture']}% | "
                f"Temp: {data['temperature']}°C | "
                f"Humidity: {data['humidity']}% | "
                f"{rain}"
            )

            # Wait before next post
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:

        print(
            f"\n\n🛑 Stopped by user after {iteration} posts"
        )

    except Exception as e:

        print(f"\n\n❌ Unexpected error: {e}")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("❌ Please provide a sensor ID.")
        print(
            "Example: python simulate_esp32_new_plant.py ESP32_NEW_001"
        )
        sys.exit(1)

    sensor_id = sys.argv[1]

    main(sensor_id)