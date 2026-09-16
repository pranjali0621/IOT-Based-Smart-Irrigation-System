"""
Irrigation decision logic.
Determines when to water based on soil moisture and weather.
"""
from app.config import settings


def decide_irrigation(moisture: float, rain_detected: bool, 
                     forecast_rain: bool = False) -> dict:
    """
    Make irrigation decision based on soil moisture and weather.
    
    Logic:
    - If moisture < THRESHOLD_DRY AND no rain (detected or forecasted) → WATER
    - If rain detected locally OR forecasted → SKIP (avoid overwatering)
    - If moisture adequate → SKIP
    
    Args:
        moisture: Current soil moisture (0-100%)
        rain_detected: Is rain currently falling (local sensor)
        forecast_rain: Is rain forecasted (weather API, default False for now)
        
    Returns:
        dict: {
            "decision": "WATER" | "SKIP" | "MONITOR",
            "reason": str,
            "confidence": float (0.0-1.0),
            "details": dict
        }
    """
    threshold_dry = settings.moisture_threshold_dry  # 35%
    threshold_optimal = settings.moisture_threshold_optimal  # 50%
    
    # Check rain
    any_rain = rain_detected or forecast_rain
    
    # Decision logic
    if moisture < threshold_dry and not any_rain:
        decision = "WATER"
        reason = (f"Soil moisture {moisture:.1f}% is below dry threshold "
                 f"({threshold_dry}%) and no rain detected")
        confidence = 0.95
        action = "START_PUMP"
        
    elif any_rain:
        decision = "SKIP"
        rain_source = "Local sensor" if rain_detected else "Weather forecast"
        reason = f"Rain detected ({rain_source}). Skipping to avoid overwatering"
        confidence = 0.98
        action = "NONE"
        
    elif moisture < threshold_optimal:
        decision = "MONITOR"
        reason = (f"Soil moisture {moisture:.1f}% is adequate but below optimal "
                 f"({threshold_optimal}%). Monitor next reading")
        confidence = 0.85
        action = "NONE"
        
    else:
        decision = "SKIP"
        reason = f"Soil moisture {moisture:.1f}% is adequate"
        confidence = 0.90
        action = "NONE"
    
    return {
        "decision": decision,
        "reason": reason,
        "confidence": confidence,
        "details": {
            "moisture_level": moisture,
            "threshold_dry": threshold_dry,
            "threshold_optimal": threshold_optimal,
            "rain_detected": rain_detected,
            "forecast_rain": forecast_rain,
            "action": action
        }
    }


def get_decision_summary(decision_result: dict) -> str:
    """
    Get human-readable summary of decision.
    
    Args:
        decision_result: Result from decide_irrigation()
        
    Returns:
        str: User-friendly message
    """
    decision = decision_result["decision"]
    confidence = decision_result["confidence"]
    
    if decision == "WATER":
        return f"✅ Water now (Confidence: {confidence*100:.0f}%)"
    elif decision == "SKIP":
        return f"⏭️  Skip watering (Confidence: {confidence*100:.0f}%)"
    elif decision == "MONITOR":
        return f"👀 Monitor next reading (Confidence: {confidence*100:.0f}%)"
    else:
        return "❓ Unknown decision"
