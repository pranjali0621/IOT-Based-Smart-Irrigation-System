#!/usr/bin/env python3
"""
Generate 48-hour realistic sensor data for demo.
Simulates plant drying down and watering decisions.
"""

import sys
sys.path.insert(0, '/Users/ishekasingh/IOT-Based-Smart-Irrigation-System/florapulse-backend')

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.database_models import User, Plant, Sensor, SensorReading, IrrigationDecision
from app.services.irrigation_engine import decide_irrigation
from app.utils.auth import hash_password
import random

def generate_demo_data():
    """Generate complete demo dataset"""
    db = SessionLocal()
    
    print("🌱 Generating Demo Data...")
    
    # 1. Create user
    print("  1️⃣ Creating user...")
    user = User(
        username="demo",
        email="demo@florapulse.local",
        password_hash=hash_password("demo123"),
        full_name="Demo User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"     ✅ User created: {user.username}")
    
    # 2. Create plant
    print("  2️⃣ Creating plant...")
    plant = Plant(
        user_id=user.id,
        name="Monstera in Living Room",
        species="Monstera deliciosa",
        location="Living Room Window",
        description="Large green plant, 2 years old, watered weekly"
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)
    print(f"     ✅ Plant created: {plant.name}")
    
    # 3. Create sensor
    print("  3️⃣ Creating sensor...")
    sensor = Sensor(
        plant_id=plant.id,
        sensor_id="ESP32_DEMO_001",
        sensor_name="Moisture Sensor #1",
        is_connected=True
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    print(f"     ✅ Sensor created: {sensor.sensor_id}")
    
    # 4. Generate 48-hour readings
    print("  4️⃣ Generating 48-hour sensor readings...")
    
    now = datetime.now()
    start_time = now - timedelta(hours=48)
    
    # Realistic depletion curve
    readings_data = []
    
    # Hour 0-12: High moisture (just watered)
    for i in range(0, 12, 2):
        timestamp = start_time + timedelta(hours=i)
        moisture = 75 - (i * 1.5)  # Slowly decrease
        temp = 22 + random.uniform(-1, 1)
        humidity = 60 + random.uniform(-5, 5)
        readings_data.append({
            'timestamp': timestamp,
            'moisture': moisture,
            'temp': temp,
            'humidity': humidity,
            'rain': False
        })
    
    # Hour 12-24: Medium moisture (normal drying)
    for i in range(12, 24, 2):
        timestamp = start_time + timedelta(hours=i)
        moisture = 75 - (i * 1.5)
        temp = 24 + random.uniform(-2, 2)
        humidity = 55 + random.uniform(-5, 5)
        readings_data.append({
            'timestamp': timestamp,
            'moisture': moisture,
            'temp': temp,
            'humidity': humidity,
            'rain': False
        })
    
    # Hour 24-36: Low moisture (drying more)
    for i in range(24, 36, 2):
        timestamp = start_time + timedelta(hours=i)
        moisture = 75 - (i * 1.5)  # Continues decreasing
        temp = 23 + random.uniform(-1, 2)
        humidity = 58 + random.uniform(-5, 5)
        readings_data.append({
            'timestamp': timestamp,
            'moisture': moisture,
            'temp': temp,
            'humidity': humidity,
            'rain': False
        })
    
    # Hour 36-48: Very low (needs watering)
    for i in range(36, 48, 2):
        timestamp = start_time + timedelta(hours=i)
        moisture = 75 - (i * 1.5)
        if moisture < 0:
            moisture = 5  # Don't go below 5
        temp = 22 + random.uniform(-1, 1)
        humidity = 60 + random.uniform(-5, 5)
        readings_data.append({
            'timestamp': timestamp,
            'moisture': moisture,
            'temp': temp,
            'humidity': humidity,
            'rain': False
        })
    
    # Create reading objects and decisions
    for data in readings_data:
        reading = SensorReading(
            sensor_id=sensor.id,
            timestamp=data['timestamp'],
            moisture=max(0, min(100, data['moisture'])),  # Clamp 0-100
            temperature=data['temp'],
            humidity=data['humidity'],
            rain_detected=data['rain']
        )
        
        # Make decision
        decision_result = decide_irrigation(
            reading.moisture,
            data['rain']
        )
        
        decision = IrrigationDecision(
            plant_id=plant.id,
            timestamp=data['timestamp'],
            moisture_level=reading.moisture,
            decision=decision_result["decision"],
            reason=decision_result["reason"],
            confidence=decision_result["confidence"]
        )
        
        db.add_all([reading, decision])
    
    db.commit()
    print(f"     ✅ {len(readings_data)} readings created")
    
    # Summary
    print("\n" + "="*50)
    print("✅ DEMO DATA GENERATED SUCCESSFULLY")
    print("="*50)
    print(f"User:      {user.username} / demo123")
    print(f"Plant:     {plant.name}")
    print(f"Sensor:    {sensor.sensor_id}")
    print(f"Readings:  {len(readings_data)} over 48 hours")
    print(f"Moisture:  75% → 5% (realistic depletion)")
    print("="*50)
    print("\nUse these credentials in demo:")
    print(f"  Username: {user.username}")
    print(f"  Password: demo123")
    print(f"  Plant ID: {plant.id}")
    print(f"  Sensor ID: {sensor.sensor_id}")
    print("="*50 + "\n")
    
    db.close()

if __name__ == "__main__":
    generate_demo_data()
