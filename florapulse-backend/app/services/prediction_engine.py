"""
Prediction engine for estimating time until next watering.
Uses historical moisture depletion rate.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from app.database_models import SensorReading
from app.config import settings


def get_depletion_rate(db: Session, hours: int = 24) -> dict:
    """
    Calculate soil moisture depletion rate from historical data.
    
    Analyzes how fast moisture decreases over time.
    
    Args:
        db: Database session
        hours: How many hours back to analyze (default 24)
        
    Returns:
        dict: {
            "depletion_rate": float (% per hour),
            "readings_analyzed": int,
            "time_period_hours": int,
            "is_valid": bool
        }
    """
    # Get readings from last N hours
    cutoff_time = datetime.now() - timedelta(hours=hours)
    readings = db.query(SensorReading)\
        .filter(SensorReading.timestamp >= cutoff_time)\
        .order_by(SensorReading.timestamp.asc())\
        .all()
    
    # Need at least 2 readings to calculate rate
    if len(readings) < 2:
        return {
            "depletion_rate": 0.0,
            "readings_analyzed": len(readings),
            "time_period_hours": hours,
            "is_valid": False,
            "reason": "Insufficient data (need at least 2 readings)"
        }
    
    # Get first and last moisture values
    first_moisture = readings[0].moisture
    last_moisture = readings[-1].moisture
    
    # Calculate time difference in hours
    time_diff = (readings[-1].timestamp - readings[0].timestamp).total_seconds() / 3600
    
    # Calculate depletion rate (% per hour)
    if time_diff > 0:
        depletion_rate = (first_moisture - last_moisture) / time_diff
    else:
        depletion_rate = 0.0
    
    # Depletion rate could be negative (moisture increasing, e.g., after rain)
    # For prediction, we care about positive depletion (drying out)
    
    return {
        "depletion_rate": round(depletion_rate, 3),
        "readings_analyzed": len(readings),
        "time_period_hours": round(time_diff, 1),
        "is_valid": True,
        "first_moisture": round(first_moisture, 1),
        "last_moisture": round(last_moisture, 1),
        "change": round(first_moisture - last_moisture, 1)
    }


def estimate_next_watering(db: Session, current_moisture: float) -> dict:
    """
    Estimate hours until next watering is needed.
    
    Uses depletion rate to predict when soil reaches dry threshold.
    
    Args:
        db: Database session
        current_moisture: Current soil moisture %
        
    Returns:
        dict: {
            "hours_until_dry": float,
            "estimated_time": str (datetime),
            "confidence": float (0.0-1.0),
            "details": dict
        }
    """
    threshold_dry = settings.moisture_threshold_dry  # 35%
    
    # Get depletion rate from last 48 hours
    rate_info = get_depletion_rate(db, hours=48)
    
    if not rate_info["is_valid"]:
        return {
            "hours_until_dry": None,
            "estimated_time": None,
            "confidence": 0.0,
            "message": rate_info.get("reason", "Cannot calculate"),
            "details": rate_info
        }
    
    depletion_rate = rate_info["depletion_rate"]
    
    # Prediction only makes sense if soil is drying (positive rate)
    if depletion_rate <= 0:
        return {
            "hours_until_dry": None,
            "estimated_time": None,
            "confidence": 0.0,
            "message": "Soil moisture stable or increasing (no depletion)",
            "details": rate_info,
            "note": "Could be recent rain or watering"
        }
    
    # Calculate: hours until current_moisture reaches threshold_dry
    # Formula: (current - threshold) / rate = hours
    moisture_buffer = current_moisture - threshold_dry
    
    if moisture_buffer <= 0:
        hours_until_dry = 0.0
        confidence = 1.0
    else:
        hours_until_dry = moisture_buffer / depletion_rate
        # Confidence decreases if prediction is far in future (less reliable)
        if hours_until_dry < 24:
            confidence = 0.85
        elif hours_until_dry < 48:
            confidence = 0.75
        else:
            confidence = 0.60  # Very uncertain for long predictions
    
    # Calculate estimated time
    estimated_time = datetime.now() + timedelta(hours=hours_until_dry)
    
    return {
        "hours_until_dry": round(hours_until_dry, 1),
        "estimated_time": estimated_time.isoformat(),
        "confidence": round(confidence, 2),
        "message": f"Estimated watering needed in {round(hours_until_dry, 1)} hours",
        "details": {
            "current_moisture": current_moisture,
            "threshold_dry": threshold_dry,
            "depletion_rate": depletion_rate,
            "readings_analyzed": rate_info["readings_analyzed"],
            "analysis_period_hours": rate_info["time_period_hours"]
        }
    }
