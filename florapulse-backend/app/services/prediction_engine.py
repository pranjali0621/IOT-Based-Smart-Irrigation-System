"""
Prediction engine for watering forecasts.

This module calculates when the next irrigation will be needed
based on historical soil moisture depletion trends.

It works by:
1. Analyzing historical sensor readings (last 48 hours)
2. Calculating depletion rate (% moisture lost per hour)
3. Estimating time until soil reaches dry threshold

The depletion rate is empirical (actual observed) and includes all factors:
- Plant water uptake (roots absorbing)
- Soil evaporation (surface drying)
- Weather effects (sun, wind, humidity)
- All combined into one number: %/hour

Confidence decreases with time horizon:
- Near-term (< 24 hours): 0.85 confidence (reliable)
- Medium-term (24-48 hours): 0.75 confidence (moderately reliable)
- Far-term (> 48 hours): 0.60 confidence (uncertain)

Example:
    >>> prediction = estimate_next_watering(db, current_moisture=55)
    >>> prediction['hours_until_dry']
    18.5
    >>> prediction['confidence']
    0.85
    >>> prediction['estimated_time']
    '2025-01-15T14:50:00.123456'
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from app.config import settings
from app.database_models import SensorReading, Sensor, PumpEvent


def calculate_depletion_rate(
    db: Session,
    plant_id: int,
    hours_lookback: int = 24
) -> dict:
    """
    Calculate soil moisture depletion rate for a specific plant.

    Analyzes sensor readings from the last N hours and calculates
    how quickly soil moisture is decreasing.

    Watering events are excluded because they artificially increase
    soil moisture and would distort the depletion rate.

    Args:
        db: Database session
        plant_id: ID of the plant
        hours_lookback: Number of hours of historical data to analyze

    Returns:
        dict containing:
            - depletion_rate_per_hour
            - hours_analyzed
            - data_quality
            - confidence
    """

    # Calculate lookback period
    cutoff_time = datetime.now() - timedelta(hours=hours_lookback)

    # Get sensor readings belonging to this plant
    readings = (
        db.query(SensorReading)
        .join(Sensor, SensorReading.sensor_id == Sensor.id)
        .filter(
            Sensor.plant_id == plant_id,
            SensorReading.timestamp >= cutoff_time
        )
        .order_by(SensorReading.timestamp.asc())
        .all()
    )

    # Step 6: Not enough data
    if len(readings) < 2:
        return {
            "depletion_rate_per_hour": 0.0,
            "hours_analyzed": 0.0,
            "data_quality": "LOW",
            "confidence": 0.0,
            "readings_analyzed": len(readings),
            "message": "Insufficient data. Need at least 2 readings."
        }

    # Get watering events during the same period
    watering_events = (
        db.query(PumpEvent)
        .filter(
            PumpEvent.plant_id == plant_id,
            PumpEvent.timestamp >= cutoff_time
        )
        .order_by(PumpEvent.timestamp.asc())
        .all()
    )

    # Step 8: Filter out readings affected by watering
    valid_readings = []

    for reading in readings:

        # Check whether this reading happened after a watering event
        affected_by_watering = False

        for event in watering_events:
            if event.timestamp <= reading.timestamp:
                # Ignore readings immediately after watering
                time_since_watering = (
                    reading.timestamp - event.timestamp
                ).total_seconds() / 3600

                if time_since_watering < 1:
                    affected_by_watering = True
                    break

        if not affected_by_watering:
            valid_readings.append(reading)

    # Need at least 2 valid readings
    if len(valid_readings) < 2:
        return {
            "depletion_rate_per_hour": 0.0,
            "hours_analyzed": 0.0,
            "data_quality": "LOW",
            "confidence": 0.0,
            "readings_analyzed": len(valid_readings),
            "message": "Not enough valid readings after filtering watering events."
        }

    # Step 7: Get first and last valid readings
    first_reading = valid_readings[0]
    last_reading = valid_readings[-1]

    moisture_start = first_reading.moisture
    moisture_end = last_reading.moisture

    # Calculate elapsed time
    hours_elapsed = (
        last_reading.timestamp - first_reading.timestamp
    ).total_seconds() / 3600

    # Avoid division by zero
    if hours_elapsed <= 0:
        return {
            "depletion_rate_per_hour": 0.0,
            "hours_analyzed": 0.0,
            "data_quality": "LOW",
            "confidence": 0.0,
            "readings_analyzed": len(valid_readings),
            "message": "Invalid timestamps."
        }

    # Calculate depletion
    depletion = moisture_start - moisture_end

    # Step 9: Moisture increased or stayed the same
    if depletion <= 0:
        return {
            "depletion_rate_per_hour": 0.0,
            "hours_analyzed": round(hours_elapsed, 1),
            "data_quality": "MEDIUM",
            "confidence": 0.3,
            "readings_analyzed": len(valid_readings),
            "message": "Moisture did not decrease during the analysis period."
        }

    # Calculate depletion rate
    depletion_rate = depletion / hours_elapsed

    # Step 9: Reject unreasonable depletion rate
    if depletion_rate > 10:
        return {
            "depletion_rate_per_hour": 0.0,
            "hours_analyzed": round(hours_elapsed, 1),
            "data_quality": "LOW",
            "confidence": 0.2,
            "readings_analyzed": len(valid_readings),
            "message": "Depletion rate is too high (>10% per hour)."
        }

    # Step 10: Determine data quality
    if len(valid_readings) >= 20:
        data_quality = "HIGH"
        confidence = 0.90
    elif len(valid_readings) >= 10:
        data_quality = "MEDIUM"
        confidence = 0.70
    else:
        data_quality = "LOW"
        confidence = 0.50

    return {
        "depletion_rate_per_hour": round(depletion_rate, 3),
        "hours_analyzed": round(hours_elapsed, 1),
        "data_quality": data_quality,
        "confidence": confidence,
        "readings_analyzed": len(valid_readings),
        "moisture_start": round(moisture_start, 1),
        "moisture_end": round(moisture_end, 1),
        "moisture_depletion": round(depletion, 1),
        "message": (
            f"Soil moisture is decreasing at "
            f"{round(depletion_rate, 3)}% per hour."
        )
    }
def predict_next_watering(
    db: Session,
    plant_id: int
) -> dict:
    """
    Predict when a plant will next require watering.

    Uses the latest soil moisture reading and the depletion rate
    calculated from historical sensor data.

    Args:
        db: Database session
        plant_id: ID of the plant

    Returns:
        dict containing:
            - next_watering_in_hours
            - estimated_datetime
            - estimated_time_friendly
            - current_moisture
            - watering_threshold
            - depletion_rate_per_hour
            - data_quality
            - confidence
            - status
    """

    # Step 2: Get watering threshold from configuration
    watering_threshold = settings.moisture_threshold_dry

    # Step 4: Get latest reading for this plant
    latest_reading = (
        db.query(SensorReading)
        .join(Sensor, SensorReading.sensor_id == Sensor.id)
        .filter(Sensor.plant_id == plant_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    # Handle no sensor data
    if latest_reading is None:
        return {
            "next_watering_in_hours": None,
            "estimated_datetime": None,
            "estimated_time_friendly": None,
            "current_moisture": None,
            "watering_threshold": watering_threshold,
            "depletion_rate_per_hour": None,
            "data_quality": "LOW",
            "confidence": 0,
            "status": "INSUFFICIENT_DATA",
            "message": "No sensor readings available for this plant."
        }

    current_moisture = latest_reading.moisture

    # Step 5: Get depletion rate from Task 3
    rate_info = calculate_depletion_rate(
        db,
        plant_id=plant_id,
        hours_lookback=24
    )

    depletion_rate = rate_info["depletion_rate_per_hour"]

    # Step 10.1: Already below watering threshold
    if current_moisture <= watering_threshold:
        return {
            "next_watering_in_hours": 0.0,
            "estimated_datetime": datetime.now().isoformat(),
            "estimated_time_friendly": "WATER NOW",
            "current_moisture": round(current_moisture, 1),
            "watering_threshold": watering_threshold,
            "depletion_rate_per_hour": round(depletion_rate, 3),
            "data_quality": rate_info["data_quality"],
            "confidence": max(rate_info["confidence"] * 100, 30),
            "status": "WATER_NOW",
            "message": "Soil moisture is already at or below the watering threshold."
        }

    # Step 10.2: No depletion / stable plant
    if depletion_rate <= 0:
        return {
            "next_watering_in_hours": None,
            "estimated_datetime": None,
            "estimated_time_friendly": "Not needed in the near term",
            "current_moisture": round(current_moisture, 1),
            "watering_threshold": watering_threshold,
            "depletion_rate_per_hour": round(depletion_rate, 3),
            "data_quality": rate_info["data_quality"],
            "confidence": round(rate_info["confidence"] * 100),
            "status": "MONITORING",
            "message": "Plant moisture is stable or increasing."
        }

    # Step 6: Calculate hours until watering
    moisture_buffer = current_moisture - watering_threshold

    hours_until_watering = (
        moisture_buffer / depletion_rate
    )

    # Step 7: Calculate estimated datetime
    now = datetime.now()

    estimated_datetime = (
        now + timedelta(hours=hours_until_watering)
    )

    # Friendly time format
    if estimated_datetime.date() == now.date():
        estimated_time_friendly = (
            estimated_datetime.strftime("%-I:%M %p") + " today"
        )
    elif estimated_datetime.date() == (
        now + timedelta(days=1)
    ).date():
        estimated_time_friendly = (
            estimated_datetime.strftime("%-I:%M %p") + " tomorrow"
        )
    else:
        estimated_time_friendly = estimated_datetime.strftime(
            "%b %d, %-I:%M %p"
        )

    # Step 9: Confidence
    confidence = rate_info["confidence"] * 100

    # Step 11: Determine status
    if hours_until_watering < 4:
        status = "WATER_SOON"
    else:
        status = "MONITORING"

    return {
        "next_watering_in_hours": round(hours_until_watering, 1),
        "estimated_datetime": estimated_datetime.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "estimated_time_friendly": estimated_time_friendly,
        "current_moisture": round(current_moisture, 1),
        "watering_threshold": watering_threshold,
        "depletion_rate_per_hour": round(depletion_rate, 3),
        "data_quality": rate_info["data_quality"],
        "confidence": round(confidence),
        "status": status,
        "message": (
            f"Estimated watering needed in "
            f"{round(hours_until_watering, 1)} hours."
        )
    }