import os
import requests
# pyrefly: ignore [missing-import]
from app.config import settings

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"



def fetch_weather_forecast(city_name: str = "Mumbai") -> dict:
    """
    Fetch weather forecast from OpenWeather.

    Args:
        city_name (str): City name for the forecast.

    Returns:
        dict: Simplified weather forecast data.
    """

    if not settings.openweather_api_key:
        return {
            "available": False,
            "forecast_rain": False,
            "rain_probability": 0,
            "rainfall_mm": 0,
            "cloud_coverage": 0,
            "temperature": None,
            "error": "OpenWeather API key not configured"
        }

    params = {
        "q": city_name,
        "appid": settings.openweather_api_key,
        "units": "metric"
    }

    try:
        response = requests.get(
            OPENWEATHER_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()
        forecast_list = data.get("list", [])

        if not forecast_list:
            return {
                "available": False,
                "forecast_rain": False,
                "rain_probability": 0,
                "rainfall_mm": 0,
                "cloud_coverage": 0,
                "temperature": None,
                "error": "No forecast data received"
            }

        # OpenWeather provides forecasts in 3-hour intervals.
        # First 8 entries ≈ next 24 hours.
        next_24_hours = forecast_list[:8]

        rain_probabilities = []
        rainfall_values = []
        cloud_values = []
        temperatures = []

        for forecast in next_24_hours:

            # Probability of precipitation: 0.0 - 1.0
            pop = forecast.get("pop", 0)
            rain_probabilities.append(pop * 100)

            # Rainfall amount in mm
            rain_data = forecast.get("rain", {})
            rainfall_values.append(
                rain_data.get("3h", 0)
            )

            # Cloud coverage %
            clouds = forecast.get("clouds", {})
            cloud_values.append(
                clouds.get("all", 0)
            )

            # Temperature °C
            main = forecast.get("main", {})
            temperature = main.get("temp")

            if temperature is not None:
                temperatures.append(temperature)

        max_rain_probability = max(rain_probabilities, default=0)
        total_rainfall = sum(rainfall_values)

        # Irrigation rule:
        # Rain probability > 50% means rain is forecast.
        forecast_rain = max_rain_probability > 50

        return {
            "available": True,
            "forecast_rain": forecast_rain,
            "rain_probability": max_rain_probability,
            "rainfall_mm": total_rainfall,
            "cloud_coverage": (
                sum(cloud_values) / len(cloud_values)
                if cloud_values else 0
            ),
            "temperature": (
                sum(temperatures) / len(temperatures)
                if temperatures else None
            ),
            "error": None
        }

    except requests.exceptions.RequestException as e:
        return {
            "available": False,
            "forecast_rain": False,
            "rain_probability": 0,
            "rainfall_mm": 0,
            "cloud_coverage": 0,
            "temperature": None,
            "error": str(e)
        }