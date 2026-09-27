from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# 1. USERS TABLE
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    plants = relationship("Plant", back_populates="owner", cascade="all, delete-orphan")

# 2. PLANTS TABLE
class Plant(Base):
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    species = Column(String(100), nullable=True)
    plant_picture = Column(LargeBinary, nullable=True)
    location = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    owner = relationship("User", back_populates="plants")
    sensors = relationship("Sensor", back_populates="plant", cascade="all, delete-orphan")

# 3. SENSORS TABLE
class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, index=True)
    sensor_id = Column(String(50), unique=True, nullable=False)
    sensor_name = Column(String(100), nullable=True)
    is_connected = Column(Boolean, default=False)
    last_data_received = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    plant = relationship("Plant", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")

# 4. SENSOR READINGS TABLE
class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    moisture = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    rain_detected = Column(Boolean, default=False)
    
    sensor = relationship("Sensor", back_populates="readings")

# 5. IRRIGATION DECISIONS TABLE
class IrrigationDecision(Base):
    __tablename__ = "irrigation_decisions"
    
    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    moisture_level = Column(Float, nullable=False)
    decision = Column(String(20), nullable=False)
    reason = Column(String(500), nullable=False)
    confidence = Column(Float, nullable=False)

# 6. PUMP EVENTS TABLE
class PumpEvent(Base):
    __tablename__ = "pump_events"
    
    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    action = Column(String(20), nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    reason = Column(String(100), nullable=True)

# 7. SYSTEM STATUS TABLE
class SystemStatus(Base):
    __tablename__ = "system_status"
    
    id = Column(Integer, primary_key=True)
    last_update = Column(DateTime, default=datetime.now)
    pump_status = Column(String(20), default="OFF")
    last_moisture = Column(Float, nullable=True)
    last_temperature = Column(Float, nullable=True)
    last_humidity = Column(Float, nullable=True)
    estimated_hours_to_watering = Column(Float, nullable=True)
