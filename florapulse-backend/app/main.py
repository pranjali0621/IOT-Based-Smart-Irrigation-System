"""
FloraPulse Backend - FastAPI Application Entry Point.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import init_db, get_db
from app.models import (
    SensorDataRequest,
    SensorReadingResponse,
    SensorHistoryResponse,
    SensorHistoryItem,
    SystemStatusResponse,
    IrrigationDecisionRequest,
    IrrigationDecisionResponse,
    DashboardLiveResponse,
)
from app.database_models import (
    SensorReading,
    IrrigationDecision,
    SystemStatus
)
from app.config import settings
from app.services.irrigation_engine import decide_irrigation as engine_decide
from app.services.prediction_engine import estimate_next_watering
from app.utils.validators import validate_sensor_data

# Initialize FastAPI app
app = FastAPI(
    title="FloraPulse Backend",
    description="Smart IoT Plant Irrigation System API",
    version="1.0.0"
)

# Add CORS middleware (for Streamlit frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Startup Events ============

@app.on_event("startup")
def startup_event():
    """Initialize database on app startup."""
    print("🌱 Initializing FloraPulse Backend...")
    init_db()
    print("✅ Database initialized")
    print(f"🚀 Server running on http://{settings.api_host}:{settings.api_port}")


# ============ Health Check ============

@app.get("/health")
def health_check():
    """Check if API is running."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FloraPulse Backend"
    }


# ============ Sensor Data Endpoints ============

@app.post("/api/sensor-data/upload", response_model=SensorReadingResponse)
def upload_sensor_data(
    request: SensorDataRequest,
    db: Session = Depends(get_db)
):
    """
    Upload sensor reading from ESP32.
    Validates data before saving.
    """
    try:
        # Validate sensor data
        is_valid, error_msg = validate_sensor_data(
            moisture=request.moisture,
            temperature=request.temperature,
            humidity=request.humidity
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Create new sensor reading record
        reading = SensorReading(
            moisture=request.moisture,
            temperature=request.temperature,
            humidity=request.humidity,
            rain_detected=request.rain_detected
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)
        
        return SensorReadingResponse(
            status="success",
            id=reading.id,
            saved_at=reading.timestamp
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/sensor-data/history", response_model=SensorHistoryResponse)
def get_sensor_history(
    hours: int = 24,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Fetch sensor readings from last N hours.
    """
    try:
        from sqlalchemy import desc
        
        readings = db.query(SensorReading)\
            .order_by(desc(SensorReading.timestamp))\
            .limit(limit)\
            .all()
        
        items = [SensorHistoryItem.from_orm(r) for r in readings]
        
        return SensorHistoryResponse(
            readings=items,
            total=len(items)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")


# ============ System Status Endpoint ============

@app.get("/api/status", response_model=SystemStatusResponse)
def get_system_status(db: Session = Depends(get_db)):
    """Get current system state."""
    try:
        status = db.query(SystemStatus).first()
        
        if not status:
            status = SystemStatus()
            db.add(status)
            db.commit()
        
        return SystemStatusResponse.from_orm(status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")


# ============ Irrigation Decision Endpoint ============

@app.post("/api/irrigation/decide", response_model=IrrigationDecisionResponse)
def decide_irrigation_endpoint(
    request: IrrigationDecisionRequest,
    db: Session = Depends(get_db)
):
    """
    Make irrigation decision using service logic.
    Uses soil moisture, local rain sensor, and forecasting (coming soon).
    """
    try:
        # Use irrigation engine service
        result = engine_decide(
            moisture=request.moisture,
            rain_detected=request.rain_detected,
            forecast_rain=False  # Will add weather API in Phase 2
        )
        
        # Log decision
        irrigation_log = IrrigationDecision(
            moisture_level=request.moisture,
            decision=result["decision"],
            reason=result["reason"],
            confidence=result["confidence"]
        )
        db.add(irrigation_log)
        db.commit()
        
        return IrrigationDecisionResponse(
            decision=result["decision"],
            reason=result["reason"],
            confidence=result["confidence"]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Decision error: {str(e)}")


# ============ Prediction Endpoint ============

@app.get("/api/prediction/next-watering")
def predict_next_watering(db: Session = Depends(get_db)):
    """
    Estimate when next watering will be needed.
    Uses historical depletion rate to predict.
    """
    try:
        # Get latest moisture
        latest = db.query(SensorReading).order_by(SensorReading.id.desc()).first()
        
        if not latest:
            return {
                "status": "no_data",
                "message": "No sensor data available yet",
                "hours_until_dry": None
            }
        
        # Get prediction
        prediction = estimate_next_watering(db, latest.moisture)
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# ============ Dashboard Endpoint ============

@app.get("/api/dashboard/live", response_model=DashboardLiveResponse)
def get_dashboard_live(db: Session = Depends(get_db)):
    """
    Get aggregated live data for Streamlit dashboard.
    """
    try:
        # Get latest reading
        latest_reading = db.query(SensorReading).order_by(SensorReading.id.desc()).first()
        
        # Get last 10 readings
        last_10 = db.query(SensorReading).order_by(SensorReading.id.desc()).limit(10).all()
        last_10.reverse()  # Oldest first
        
        # Get recent decisions
        recent_decisions = db.query(IrrigationDecision)\
            .order_by(IrrigationDecision.id.desc())\
            .limit(5)\
            .all()
        
        # Get system status
        status = db.query(SystemStatus).first()
        
        # Get next watering estimate
        estimated_watering = "TBD"
        if latest_reading:
            prediction = estimate_next_watering(db, latest_reading.moisture)
            if prediction["confidence"] > 0:
                estimated_watering = f"In ~{prediction['hours_until_dry']} hours"
        
        return DashboardLiveResponse(
            current_moisture=latest_reading.moisture if latest_reading else None,
            current_temperature=latest_reading.temperature if latest_reading else None,
            current_humidity=latest_reading.humidity if latest_reading else None,
            pump_status=status.pump_status if status else "OFF",
            last_10_readings=[SensorHistoryItem.from_orm(r) for r in last_10],
            recent_decisions=[
                {
                    "time": d.timestamp.isoformat(),
                    "decision": d.decision,
                    "reason": d.reason,
                    "confidence": d.confidence
                }
                for d in recent_decisions
            ],
            estimated_next_watering=estimated_watering,
            last_update=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )
