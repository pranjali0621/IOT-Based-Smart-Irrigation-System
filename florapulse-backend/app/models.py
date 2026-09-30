"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ============ Requests ============

class SensorDataRequest(BaseModel):
    """Schema for incoming sensor data from ESP32."""
    sensor_id: str
    moisture: float = Field(..., ge=0, le=100, description="Soil moisture 0-100%")
    temperature: Optional[float] = Field(
        None,
        ge=-40,
        le=80,
        description="Temperature in °C"
    )
    humidity: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Humidity 0-100%"
    )
    rain_detected: bool = Field(
        False,
        description="Is rain detected?"
    )


class IrrigationDecisionRequest(BaseModel):
    """Schema for requesting irrigation decision."""
    moisture: float = Field(..., ge=0, le=100, description="Current soil moisture %")
    rain_detected: bool = Field(False, description="Is rain detected?")


class PumpControlRequest(BaseModel):
    """Schema for manual pump control."""
    action: str = Field(..., description="ON or OFF")
    duration_seconds: Optional[int] = Field(None, ge=1, description="Duration in seconds")
    reason: str = Field("manual", description="Reason for action")


# ============ Responses ============

class SensorReadingResponse(BaseModel):
    """Response for sensor data upload."""
    status: str
    id: int
    saved_at: datetime

    class Config:
        from_attributes = True


class SensorHistoryItem(BaseModel):
    """Single sensor reading in history."""
    id: int
    timestamp: datetime
    moisture: float
    temperature: Optional[float]
    humidity: Optional[float]
    rain_detected: bool

    class Config:
        from_attributes = True


class SensorHistoryResponse(BaseModel):
    """Response for sensor history query."""
    readings: list[SensorHistoryItem]
    total: int


class SystemStatusResponse(BaseModel):
    """Current system state."""
    pump_status: str
    last_moisture: Optional[float]
    last_temperature: Optional[float]
    last_humidity: Optional[float]
    last_update: datetime
    estimated_hours_to_watering: float

    class Config:
        from_attributes = True


class IrrigationDecisionResponse(BaseModel):
    """Response for irrigation decision."""
    decision: str
    reason: str
    confidence: float
    forecast_rain_probability: float
    sensor_rain_detected: bool
    current_moisture: float


class DashboardLiveResponse(BaseModel):
    """Live data for Streamlit dashboard."""
    current_moisture: Optional[float]
    current_temperature: Optional[float]
    current_humidity: Optional[float]
    pump_status: str
    last_10_readings: list[SensorHistoryItem]
    recent_decisions: list[dict]
    estimated_next_watering: str
    last_update: datetime


class ErrorResponse(BaseModel):
    """Standard error response."""
    error_code: str
    message: str
    timestamp: datetime


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    created_at: datetime

    class Config:
        orm_mode = True   