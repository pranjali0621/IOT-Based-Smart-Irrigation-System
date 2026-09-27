"""
Input validation functions for sensor data.

This module validates sensor readings against physical constraints:
- Soil moisture: 0-100% (0% = dry, 100% = saturated)
- Temperature: -40 to 80°C (sensor operating range)
- Humidity: 0-100% (0% = bone dry air, 100% = fog)

All validators return boolean (True = valid, False = invalid).
For detailed error messages, use validate_sensor_data() which returns tuple.

Example:
    >>> validate_moisture(45.5)
    True
    
    >>> validate_moisture(150)
    False
    
    >>> is_valid, msg = validate_sensor_data(45, 28, 65)
    >>> if not is_valid:
    ...     raise ValueError(msg)
"""


def validate_moisture(value: float) -> bool:
    """
    Validate soil moisture percentage.
    
    Checks if moisture reading is within physical bounds.
    Real soil moisture ranges from 0% (bone dry) to 100% (completely saturated).
    
    Args:
        value (float): Soil moisture as percentage (0-100)
        
    Returns:
        bool: True if 0 <= value <= 100, False otherwise
        
    Example:
        >>> validate_moisture(45.5)
        True
        >>> validate_moisture(-5)
        False
    """
    return 0 <= value <= 100


def validate_temperature(value: float) -> bool:
    """
    Validate temperature reading in Celsius.
    
    Checks if temperature is within realistic range for soil/air conditions.
    Range covers:
    - -40°C: Minimum sensor operating temperature
    - 0°C: Freezing point (water ice)
    - 25°C: Comfortable room temperature
    - 80°C: Maximum sensor operating temperature
    
    Args:
        value (float): Temperature in degrees Celsius (-40 to 80)
        
    Returns:
        bool: True if -40 <= value <= 80, False otherwise
        
    Example:
        >>> validate_temperature(28)
        True
        >>> validate_temperature(100)
        False
    """
    return -40 <= value <= 80


def validate_humidity(value: float) -> bool:
    """
    Validate humidity percentage.
    
    Checks if humidity reading is within physical bounds.
    Real relative humidity ranges from 0% (bone dry air) to 100% (saturated/fog).
    
    Args:
        value (float): Relative humidity as percentage (0-100)
        
    Returns:
        bool: True if 0 <= value <= 100, False otherwise
        
    Example:
        >>> validate_humidity(65)
        True
        >>> validate_humidity(105)
        False
    """
    return 0 <= value <= 100


def validate_sensor_data(moisture: float, temperature: float = None, 
                        humidity: float = None) -> tuple[bool, str]:
    """
    Validate all sensor data together with detailed error messages.
    
    Performs range checking on all provided sensor values.
    Fields are optional: if None, they are skipped.
    This allows systems with partial sensor setups to work.
    
    Args:
        moisture (float): Soil moisture % (required, 0-100)
        temperature (float, optional): Temperature °C (optional, -40 to 80)
        humidity (float, optional): Humidity % (optional, 0-100)
        
    Returns:
        tuple[bool, str]: (is_valid, message)
            - is_valid: True if all provided values are valid
            - message: "All data valid" or specific error description
            
    Example:
        >>> is_valid, msg = validate_sensor_data(45, 28, 65)
        >>> is_valid
        True
        >>> msg
        'All data valid'
        
        >>> is_valid, msg = validate_sensor_data(150, 28, 65)
        >>> is_valid
        False
        >>> msg
        'Moisture 150 out of range (0-100%)'
        
        >>> is_valid, msg = validate_sensor_data(45, None, 65)
        >>> is_valid
        True  # temperature skipped (None)
    """
    # Moisture is always required and checked first
    if not validate_moisture(moisture):
        return False, f"Moisture {moisture} out of range (0-100%)"
    
    # Temperature is optional but validated if provided
    if temperature is not None and not validate_temperature(temperature):
        return False, f"Temperature {temperature} out of range (-40 to 80°C)"
    
    # Humidity is optional but validated if provided
    if humidity is not None and not validate_humidity(humidity):
        return False, f"Humidity {humidity} out of range (0-100%)"
    
    # All checks passed
    return True, "All data valid"
