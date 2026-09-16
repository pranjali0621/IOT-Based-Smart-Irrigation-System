"""
SQLAlchemy ORM models for database tables.
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class SensorReading(Base):
    """Stores raw sensor data from ESP32."""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    moisture = Column(Float, nullable=False)  # 0-100%
    temperature = Column(Float, nullable=True)  # °C
    humidity = Column(Float, nullable=True)  # 0-100%
    rain_detected = Column(Boolean, default=False)  # True/False


class IrrigationDecision(Base):
    """Logs irrigation decisions made by the system."""
    __tablename__ = "irrigation_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    moisture_level = Column(Float, nullable=False)
    decision = Column(String(50), nullable=False)  # "WATER", "SKIP", "MONITOR"
    reason = Column(String(255))
    confidence = Column(Float, default=0.8)  # 0.0 to 1.0


class PumpEvent(Base):
    """Logs pump on/off events."""
    __tablename__ = "pump_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    action = Column(String(10), nullable=False)  # "ON" or "OFF"
    duration_seconds = Column(Integer)  # Duration if action is "ON"
    reason = Column(String(100))  # "auto" or "manual"


class SystemStatus(Base):
    """Stores current system state."""
    __tablename__ = "system_status"
    
    id = Column(Integer, primary_key=True, index=True)
    last_update = Column(DateTime(timezone=True), server_default=func.now())
    pump_status = Column(String(10), default="OFF")  # "ON" or "OFF"
    last_moisture = Column(Float)
    last_temperature = Column(Float)
    last_humidity = Column(Float)
    estimated_hours_to_watering = Column(Float, default=0.0)
