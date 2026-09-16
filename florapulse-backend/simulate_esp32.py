"""
Mock ESP32 Sensor Simulator
Generates realistic sensor data and posts to backend API.
"""
import requests
import random
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/sensor-data/upload"
POLL_INTERVAL = 10  # seconds between posts
MAX_ITERATIONS = None  # None = infinite, or set number like 100

# Sensor value ranges (realistic)
MOISTURE_MIN = 25
MOISTURE_MAX = 75
TEMPERATURE_MIN = 18
TEMPERATURE_MAX = 35
HUMIDITY_MIN = 30
HUMIDITY_MAX = 85
RAIN_PROBABILITY = 0.15  # 15% chance of rain detected


def generate_sensor_data():
    """
    Generate realistic sensor readings.
    
    Returns:
        dict: Sensor data matching SensorDataRequest schema
    """
    return {
        "moisture": round(random.uniform(MOISTURE_MIN, MOISTURE_MAX), 1),
        "temperature": round(random.uniform(TEMPERATURE_MIN, TEMPERATURE_MAX), 1),
        "humidity": round(random.uniform(HUMIDITY_MIN, HUMIDITY_MAX), 1),
        "rain_detected": random.random() < RAIN_PROBABILITY
    }


def post_to_api(data):
    """
    POST sensor data to backend API.
    
    Args:
        data (dict): Sensor reading
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.post(API_URL, json=data, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return False


def main():
    """
    Main simulator loop.
    Generates and posts sensor data indefinitely or until MAX_ITERATIONS.
    """
    print("🌱 FloraPulse ESP32 Simulator Started")
    print(f"📤 Posting to: {API_URL}")
    print(f"⏱️  Interval: {POLL_INTERVAL} seconds")
    print(f"🔄 Press Ctrl+C to stop\n")
    
    iteration = 0
    
    try:
        while True:
            # Stop after MAX_ITERATIONS if set
            if MAX_ITERATIONS and iteration >= MAX_ITERATIONS:
                print(f"\n✅ Completed {MAX_ITERATIONS} iterations. Stopping.")
                break
            
            iteration += 1
            
            # Generate data
            data = generate_sensor_data()
            
            # Post to API
            success = post_to_api(data)
            
            # Log result
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "✅" if success else "❌"
            rain = "🌧️ " if data["rain_detected"] else ""
            
            print(f"{status} [{timestamp}] #{iteration} | "
                  f"Moisture: {data['moisture']}% | "
                  f"Temp: {data['temperature']}°C | "
                  f"Humidity: {data['humidity']}% | "
                  f"{rain}")
            
            # Wait before next post
            time.sleep(POLL_INTERVAL)
    
    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped by user after {iteration} posts")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
