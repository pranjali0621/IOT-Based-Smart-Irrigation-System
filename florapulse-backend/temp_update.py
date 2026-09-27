# This is a helper to show what to change
# In app/main.py, find this section:

# OLD (inline logic):
@app.post("/api/irrigation/decide", response_model=IrrigationDecisionResponse)
def decide_irrigation(
    request: IrrigationDecisionRequest,
    db: Session = Depends(get_db)
):
    threshold_dry = settings.moisture_threshold_dry
    if request.moisture < threshold_dry and not request.rain_detected:
        decision = "WATER"
        reason = f"Soil moisture {request.moisture:.1f}%..."
        confidence = 0.95
    else:
        decision = "SKIP"
        ...
    return IrrigationDecisionResponse(...)

# NEW (uses service):
from app.services.irrigation_engine import decide_irrigation as engine_decide

@app.post("/api/irrigation/decide", response_model=IrrigationDecisionResponse)
def decide_irrigation(
    request: IrrigationDecisionRequest,
    db: Session = Depends(get_db)
):
    result = engine_decide(
        moisture=request.moisture,
        rain_detected=request.rain_detected,
        forecast_rain=False  # Will add weather API later
    )
    
    return IrrigationDecisionResponse(
        decision=result["decision"],
        reason=result["reason"],
        confidence=result["confidence"]
    )
