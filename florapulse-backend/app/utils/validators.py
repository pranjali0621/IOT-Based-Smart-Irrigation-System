"""
Input validation functions for sensor data.
"""


def validate_moisture(value: float) -> bool:
    """
    Validate moisture percentage.
    
    Args:
        value: Moisture percentage
        
    Returns:
        bool: True if valid (0-100), False otherwise
    """
    return 0 <= value <= 100


def validate_temperature(value: float) -> bool:
    """
    Validate temperature in Celsius.
    
    Args:
        value: Temperature in °C
        
    Returns:
        bool: True if valid (-40 to 80°C), False otherwise
    """
    return -40 <= value <= 80


def validate_humidity(value: float) -> bool:
    """
    Validate humidity percentage.
    
    Args:
        value: Humidity percentage
        
    Returns:
        bool: True if valid (0-100), False otherwise
    """
    return 0 <= value <= 100


def validate_sensor_data(moisture: float, temperature: float = None, 
                        humidity: float = None) -> tuple[bool, str]:
    """
    Validate all sensor data together.
    
    Args:
        moisture: Soil moisture %
        temperature: Temperature °C (optional)
        humidity: Humidity % (optional)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not validate_moisture(moisture):
        return False, f"Moisture {moisture} out of range (0-100%)"
    
    if temperature is not None and not validate_temperature(temperature):
        return False, f"Temperature {temperature} out of range (-40 to 80°C)"
    
    if humidity is not None and not validate_humidity(humidity):
        return False, f"Humidity {humidity} out of range (0-100%)"
    
    return True, "All data valid"
