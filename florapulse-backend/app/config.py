"""
Configuration and environment variables for FloraPulse backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from .env file."""
    
    # Database
    database_url: str = "sqlite:///./florapulse.db"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    openweather_api_key: str
    
    # Irrigation Thresholds
    moisture_threshold_dry: float = 35.0
    moisture_threshold_optimal: float = 50.0
    moisture_threshold_wet: float = 70.0
    
    # Simulation
    simulation_enabled: bool = True
    simulation_interval_seconds: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create a global settings instance
settings = Settings()
