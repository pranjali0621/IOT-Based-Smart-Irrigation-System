"""
Irrigation decision engine.

This module implements the core logic for automated irrigation decisions.
It uses a rule-based approach:

1. Check soil moisture level
2. Check for rain (detected or forecast)
3. Apply thresholds to make decision
4. Return decision with confidence score

Decision Types:
    WATER: Soil is dry, no rain → Turn pump on
    SKIP: Either moisture adequate OR rain expected → Don't water
    MONITOR: Between dry and optimal → Watch next reading

Thresholds (configurable in .env):
    MOISTURE_THRESHOLD_DRY: 35% (below = needs water)
    MOISTURE_THRESHOLD_OPTIMAL: 50% (below = monitor)

Example Usage:
    >>> result = decide_irrigation(moisture=30, rain_detected=False)
    >>> result['decision']
    'WATER'
    >>> result['confidence']
    0.95
"""
from app.config import settings


def decide_irrigation(moisture: float, rain_detected: bool, 
                     forecast_rain: bool = False) -> dict:
    """
    Make irrigation decision based on soil moisture and weather.
    
    This is the core decision logic. It evaluates:
    1. Is soil dry? (moisture < threshold_dry)
    2. Is rain falling or forecast? (rain_detected OR forecast_rain)
    3. Is soil adequately moist? (moisture > threshold_optimal)
    
    Decision Rules:
    - If moisture < THRESHOLD_DRY AND no rain → WATER (confidence: 0.95)
    - If any rain detected or forecast → SKIP (confidence: 0.98, avoid overwatering)
    - If moisture between thresholds → MONITOR (confidence: 0.85, check again soon)
    - If moisture adequate → SKIP (confidence: 0.90, all good)
    
    Args:
        moisture (float): Current soil moisture 0-100% (required, validated)
        rain_detected (bool): Is rain currently falling (local sensor)
        forecast_rain (bool, optional): Is rain forecasted (weather API, default False)
        
    Returns:
        dict: Decision result with keys:
            - decision (str): 'WATER', 'SKIP', or 'MONITOR'
            - reason (str): Human-readable explanation
            - confidence (float): 0.0-1.0, how sure we are
            - details (dict): Raw values used in decision
                - moisture_level
                - threshold_dry
                - threshold_optimal
                - rain_detected
                - forecast_rain
                - action (PUMP command for automation)
                
    Example:
        >>> result = decide_irrigation(
        ...     moisture=30,
        ...     rain_detected=False,
        ...     forecast_rain=False
        ... )
        >>> result
        {
            'decision': 'WATER',
            'reason': 'Soil moisture 30.0% is below dry threshold...',
            'confidence': 0.95,
            'details': {...}
        }
    
    Note:
        - Confidence ranges: 0.85 (MONITOR) to 0.98 (rain)
        - Rain logic uses OR: Any rain is reason enough to skip
        - Action field is for future pump automation
    """
    # Load thresholds from configuration
    threshold_dry = settings.moisture_threshold_dry      # 35%
    threshold_optimal = settings.moisture_threshold_optimal  # 50%
    
    # Check rain status (either current or forecast)
    any_rain = rain_detected or forecast_rain
    
    # Apply decision logic
    if moisture < threshold_dry and not any_rain:
        # CASE 1: Dry soil AND no rain → Water now
        decision = "WATER"
        reason = (f"Soil moisture {moisture:.1f}% is below dry threshold "
                 f"({threshold_dry}%) and no rain detected")
        confidence = 0.95
        action = "START_PUMP"
        
    elif any_rain:
        # CASE 2: Rain detected OR forecast → Skip (avoid overwatering)
        decision = "SKIP"
        rain_source = "Local sensor" if rain_detected else "Weather forecast"
        reason = f"Rain detected ({rain_source}). Skipping to avoid overwatering"
        confidence = 0.98  # Most confident (rain is clear signal)
        action = "NONE"
        
    elif moisture < threshold_optimal:
        # CASE 3: Not dry but not optimal → Monitor
        decision = "MONITOR"
        reason = (f"Soil moisture {moisture:.1f}% is adequate but below optimal "
                 f"({threshold_optimal}%). Monitor next reading")
        confidence = 0.85
        action = "NONE"
        
    else:
        # CASE 4: Everything good → Skip
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
    Convert decision result to user-friendly summary string.
    
    Takes detailed decision dict and produces a short, emoji-friendly string
    suitable for displays or logs.
    
    Args:
        decision_result (dict): Result from decide_irrigation()
        
    Returns:
        str: Short human-readable summary with emoji
            Examples:
                "✅ Water now (Confidence: 95%)"
                "⏭️  Skip watering (Confidence: 98%)"
                "👀 Monitor next reading (Confidence: 85%)"
                "❓ Unknown decision"
                
    Example:
        >>> result = decide_irrigation(30, False)
        >>> summary = get_decision_summary(result)
        >>> print(summary)
        "✅ Water now (Confidence: 95%)"
    """
    decision = decision_result["decision"]
    confidence = decision_result["confidence"]
    confidence_percent = confidence * 100
    
    if decision == "WATER":
        return f"✅ Water now (Confidence: {confidence_percent:.0f}%)"
    elif decision == "SKIP":
        return f"⏭️  Skip watering (Confidence: {confidence_percent:.0f}%)"
    elif decision == "MONITOR":
        return f"👀 Monitor next reading (Confidence: {confidence_percent:.0f}%)"
    else:
        return "❓ Unknown decision"
