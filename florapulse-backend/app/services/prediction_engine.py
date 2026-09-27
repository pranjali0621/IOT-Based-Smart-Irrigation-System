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
from app.database_models import SensorReading
from app.config import settings


def get_depletion_rate(db: Session, hours: int = 24) -> dict:
    """
    Calculate soil moisture depletion rate from historical data.
    
    Analyzes how fast soil moisture decreases over a time period.
    Returns empirical rate (actual observed decrease).
    
    The depletion rate includes:
    - Plant water uptake (roots absorbing moisture)
    - Soil surface evaporation
    - All weather effects (sun, wind, humidity)
    
    Needs minimum 2 readings to calculate (start and end points).
    
    Args:
        db (Session): Database session
        hours (int, optional): How many hours back to analyze (default 24)
            - 24: Last 24 hours (daily rate)
            - 48: Last 48 hours (includes full day/night cycle)
            - Used in estimate_next_watering with 48 hours
        
    Returns:
        dict: Analysis results with keys:
            - depletion_rate (float): %/hour (how fast soil dries)
            - readings_analyzed (int): Number of readings used
            - time_period_hours (float): Actual time span analyzed
            - is_valid (bool): Whether calculation succeeded
            - reason (str): If not valid, why not
            - first_moisture (float): Initial moisture %
            - last_moisture (float): Final moisture %
            - change (float): Total change in %
            
    Example:
        >>> rate = get_depletion_rate(db, hours=48)
        >>> rate['depletion_rate']
        0.833  # 0.833% per hour
        >>> rate['readings_analyzed']
        96  # About 2 readings per hour
    
    Notes:
        - Depletion rate can be negative if soil is increasing (watering/rain)
        - Minimum 2 readings required (start and end)
        - Returns early if insufficient data
    """
    # Calculate cutoff time (now minus N hours)
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # Query readings from database
    readings = db.query(SensorReading)\
        .filter(SensorReading.timestamp >= cutoff_time)\
        .order_by(SensorReading.timestamp.asc())\
        .all()
    
    # Check minimum data requirement
    if len(readings) < 2:
        return {
            "depletion_rate": 0.0,
            "readings_analyzed": len(readings),
            "time_period_hours": hours,
            "is_valid": False,
            "reason": "Insufficient data (need at least 2 readings)"
        }
    
    # Extract first and last moisture values
    first_moisture = readings[0].moisture
    last_moisture = readings[-1].moisture
    
    # Calculate time difference in hours
    time_diff = (readings[-1].timestamp - readings[0].timestamp).total_seconds() / 3600
    
    # Calculate depletion rate (%/hour)
    # Formula: (initial - final) / hours = rate
    if time_diff > 0:
        depletion_rate = (first_moisture - last_moisture) / time_diff
    else:
        depletion_rate = 0.0
    
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
    
    Uses empirical depletion rate to predict when soil reaches dry threshold.
    
    Formula:
        hours_until_dry = (current_moisture - threshold_dry) / depletion_rate
    
    Example with numbers:
        - Current moisture: 60%
        - Dry threshold: 35%
        - Depletion rate: 1% per hour
        - Hours until dry: (60 - 35) / 1 = 25 hours
        - Estimated time: ~25 hours from now
    
    Confidence decreases with prediction distance:
        - < 24 hours: 0.85 (high, near-term reliable)
        - 24-48 hours: 0.75 (moderate, medium-term less certain)
        - > 48 hours: 0.60 (low, far predictions speculative)
    
    Args:
        db (Session): Database session
        current_moisture (float): Current soil moisture % (0-100, validated)
        
    Returns:
        dict: Prediction with keys:
            - hours_until_dry (float): Hours until reaching dry threshold
            - estimated_time (str): ISO format datetime
            - confidence (float): 0.0-1.0, how reliable prediction is
            - message (str): User-friendly summary
            - details (dict): Calculation details
                - current_moisture
                - threshold_dry
                - depletion_rate
                - readings_analyzed
                - analysis_period_hours
                
    Example:
        >>> pred = estimate_next_watering(db, current_moisture=55)
        >>> pred['hours_until_dry']
        18.5
        >>> pred['confidence']
        0.85
        >>> pred['message']
        'Estimated watering needed in 18.5 hours'
    
    Error Cases:
        - Not enough data: confidence=0.0, message explains
        - Soil stable/increasing: confidence=0.0, no watering needed
        - Already dry: hours_until_dry=0.0, water immediately
    """
    # Load dry threshold from config
    threshold_dry = settings.moisture_threshold_dry  # 35%
    
    # Get depletion rate from last 48 hours (full day/night cycle)
    rate_info = get_depletion_rate(db, hours=48)
    
    # Check if we have valid depletion data
    if not rate_info["is_valid"]:
        return {
            "hours_until_dry": None,
            "estimated_time": None,
            "confidence": 0.0,
            "message": rate_info.get("reason", "Cannot calculate"),
            "details": rate_info
        }
    
    # Extract depletion rate
    depletion_rate = rate_info["depletion_rate"]
    
    # Handle non-drying soil (stable or increasing moisture)
    if depletion_rate <= 0:
        return {
            "hours_until_dry": None,
            "estimated_time": None,
            "confidence": 0.0,
            "message": "Soil moisture stable or increasing (no depletion)",
            "details": rate_info,
            "note": "Could be recent rain or watering"
        }
    
    # Calculate buffer (how much above dry threshold)
    moisture_buffer = current_moisture - threshold_dry
    
    # Special case: Already dry
    if moisture_buffer <= 0:
        hours_until_dry = 0.0
        confidence = 1.0
    else:
        # Normal case: Calculate hours until dry
        # Formula: buffer / rate = hours
        hours_until_dry = moisture_buffer / depletion_rate
        
        # Set confidence based on prediction distance
        # (farther = less reliable)
        if hours_until_dry < 24:
            confidence = 0.85   # Near-term, reliable
        elif hours_until_dry < 48:
            confidence = 0.75   # Medium-term, moderately reliable
        else:
            confidence = 0.60   # Far-term, speculative
    
    # Calculate actual estimated time
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
