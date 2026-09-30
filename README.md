# FloraPulse - Smart IoT Plant Irrigation System

An intelligent, predictive watering system that monitors plants in real-time and automates irrigation based on environmental conditions, soil moisture trends, and weather forecasts.

## Overview

FloraPulse integrates embedded systems, IoT sensors, cloud analytics, and weather intelligence to deliver an efficient, affordable plant care solution. The system uses predictive modeling to estimate watering requirements before soil reaches critical dryness, integrates weather data to avoid unnecessary irrigation during rainfall, and provides a comprehensive dashboard for real-time monitoring and historical analysis.

### Key Features

- Real-time sensor monitoring (soil moisture, temperature, humidity, rainfall detection)
- Predictive watering based on historical soil depletion rates
- Weather-aware irrigation (prevents watering when rain is forecasted)
- Multi-plant support with individual health tracking
- Interactive dashboard with analytics and sensor visualization
- REST API for extensibility and mobile integration
- Database persistence for historical analysis

## Technology Stack

### Frontend
- **Framework**: Streamlit (Python)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib
- **HTTP Client**: Requests

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **External APIs**: OpenWeather API
- **Async Support**: Built-in async/await

### Hardware
- **Microcontroller**: ESP32
- **Sensors**: DHT22 (temperature/humidity), Capacitive soil moisture sensor, Rain sensor
- **Actuator**: DC water pump with relay module
- **Connectivity**: WiFi (built-in)
- **Communication**: HTTP requests to FastAPI backend

### DevOps
- **Version Control**: Git
- **Environment Management**: Python venv

## System Architecture

```
ESP32 (Hardware Layer)
    |
    v
WiFi Network
    |
    v
FastAPI Backend (http://localhost:8000)
    |
    +-- SQLite Database (sensor_data, watering_history, plant_profiles)
    |
    +-- OpenWeather API Integration
    |
    v
Streamlit Frontend (http://localhost:8501)
    |
    +-- Dashboard (real-time plant status)
    +-- Sensors (historical trends by plant)
    +-- Weather (7-day forecast)
    +-- Analytics (plant health aggregation)
    +-- Garden (plant management)
    +-- Profile (user settings)
    +-- Admin (system configuration)
```

## Project Structure

```
IOT-Based-Smart-Irrigation-System/
├── app.py                          # Streamlit entry point
├── requirements.txt                # Frontend dependencies
├── config.toml                     # Streamlit configuration
├── assets/                         # Images, backgrounds, UI assets
├── pages/                          # Streamlit multi-page app
│   ├── 1_Welcome.py               # Onboarding page
│   ├── 2_Login.py                 # Authentication
│   ├── 3_Sign_Up.py               # Account creation
│   ├── 4_Create.py                # Plant profile creation
│   ├── 5_Garden.py                # Garden management
│   ├── 6_Dashboard.py             # Main monitoring dashboard
│   ├── 7_About.py                 # Project information
│   ├── 8_Profile.py               # User profile
│   ├── 9_Sensors.py               # Sensor data visualization
│   ├── 10_Settings.py             # System settings
│   ├── 11_Analytics.py            # Historical analysis
│   ├── 12_Weather.py              # Weather integration
│   └── 9_Admin.py                 # Admin controls
│
├── florapulse-backend/             # FastAPI backend service
│   ├── main.py                    # FastAPI application entry
│   ├── requirements.txt           # Backend dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database connection & setup
│   │   ├── database_models.py     # SQLAlchemy ORM models
│   │   ├── models.py              # Pydantic request/response models
│   │   ├── main.py                # Route handlers
│   │   ├── services/
│   │   │   ├── irrigation_engine.py    # Watering logic
│   │   │   ├── prediction_engine.py    # Trend analysis & forecasting
│   │   │   └── weather_service.py      # OpenWeather API wrapper
│   │   └── utils/
│   │       ├── auth.py            # Authentication helpers
│   │       └── validators.py      # Input validation
│   ├── simulate_esp32.py          # ESP32 data simulator
│   ├── simulate_esp32_new_plant.py # New plant simulation
│   └── test_db.py                 # Database testing utilities
│
└── hardware/                       # ESP32 firmware (future)
    └── esp32_main.ino             # Sensor reading & WiFi communication
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- pip
- Git

### Frontend Setup

```bash
# Clone repository
git clone <repo-url>
cd IOT-Based-Smart-Irrigation-System

# Create virtual environment
python -m venv venv-frontend
source venv-frontend/bin/activate  # Mac/Linux
# or
venv-frontend\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

Access frontend at: `http://localhost:8501`

### Backend Setup

```bash
# Navigate to backend directory
cd florapulse-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python main.py
# or
uvicorn app.main:app --reload --port 8000
```

Access backend at: `http://localhost:8000`
API documentation at: `http://localhost:8000/docs`

### Hardware Setup

1. Install Arduino IDE
2. Install ESP32 board support
3. Configure WiFi credentials in `wifi_config.h`
4. Upload `esp32_main.ino` to ESP32
5. ESP32 will connect to backend and stream sensor data

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `POST /auth/logout` - User logout

### Plants
- `GET /api/plants` - List all plants
- `POST /api/plants` - Create new plant
- `GET /api/plants/{plant_id}` - Get plant details
- `PUT /api/plants/{plant_id}` - Update plant
- `DELETE /api/plants/{plant_id}` - Delete plant

### Sensors
- `POST /api/sensors` - Log sensor reading (from ESP32)
- `GET /api/sensors/{plant_id}` - Get sensor history
- `GET /api/sensors/{plant_id}/latest` - Get latest reading

### Watering
- `GET /api/watering/history` - Watering logs
- `GET /api/watering/prediction/{plant_id}` - Next watering estimate
- `POST /api/watering/manual` - Trigger manual watering

### Weather
- `GET /api/weather/{city}` - Current weather
- `GET /api/weather/{city}/forecast` - 7-day forecast

## Data Models

### Plant
```python
{
    "id": "uuid",
    "name": "Monstera Deliciosa",
    "emoji": "🌿",
    "location": "Living Room",
    "soil_type": "potting_mix",
    "watering_interval": 3,  # days
    "last_watered": "2026-09-27T14:30:00",
    "health_score": 85,
    "moisture": 65.5,
    "temperature": 22.3,
    "humidity": 58.2,
    "light": 1200
}
```

### Sensor Reading
```python
{
    "timestamp": "2026-09-27T15:45:00",
    "plant_id": "uuid",
    "soil_moisture": 65.5,
    "temperature": 22.3,
    "humidity": 58.2,
    "light_intensity": 1200,
    "rainfall_detected": false
}
```

## Workflows

### Real-Time Monitoring
1. ESP32 reads sensors every 30 seconds
2. Data sent to backend via HTTP POST
3. Backend stores in SQLite
4. Frontend fetches via REST API
5. Dashboard updates with real-time values

### Predictive Watering
1. Backend analyzes 7-day soil moisture history
2. Calculates depletion rate (% per day)
3. Estimates days until critical threshold
4. Checks weather forecast (rain within 24h?)
5. Schedules irrigation if needed
6. Sends signal to relay module

### Weather Integration
1. Backend queries OpenWeather API every 6 hours
2. Stores forecast in cache
3. Checks rainfall probability before watering
4. Frontend displays 7-day forecast with precipitation

## Development Workflow

### Git Strategy
- `main` - Production/stable code
- `backend-dev` - Backend development
- `frontend-dev` - Frontend development (archived, merged to main)

### Branch Conventions
```bash
# Create feature branch
git checkout -b feature/feature-name

# Commit frequently
git commit -m "Component: Specific change description"

# Push and create pull request
git push origin feature/feature-name
```

### Commit Message Format
```
Frontend: Add sensor visualization charts
Backend: Implement predictive watering algorithm
Hardware: Fix DHT22 sensor reading timeout
Database: Add watering_history table migration
```

## Testing

### Backend Testing
```bash
cd florapulse-backend
python test_db.py        # Database tests
python simulate_esp32.py # Sensor data simulation
```

### Frontend Testing
```bash
# Manual testing in Streamlit app
# Test login/signup flow
# Test plant creation
# Test dashboard navigation
# Verify API connectivity
```

## Performance & Scalability

### Current Metrics
- Sensor readings: 2 per minute per plant
- Dashboard refresh: 5-second intervals
- Forecast cache: 6-hour update cycle
- Database: SQLite (suitable for <1000 plants)

### Future Optimizations
- PostgreSQL for horizontal scaling
- Redis caching for API responses
- Background job queue (Celery) for predictions
- Mobile app (React Native)
- Cloud deployment (AWS/GCP)

## Hardware Specifications

### ESP32 Configuration
- CPU: Dual-core 240 MHz
- RAM: 320 KB
- WiFi: 802.11 b/g/n
- GPIO: 36 digital pins

### Sensor Specs
- DHT22: Temperature (-40 to 80°C), Humidity (0-100%)
- Soil Moisture: Capacitive (0-100%)
- Rain Sensor: Digital trigger + analog
- Light Sensor: Lux meter (0-65535)

### Power
- Operating: 5V, 1A
- Relay: 12V, rated for 16A @ 250V AC

## Team & Contributions

- **Backend & Database**: Database architecture, API endpoints, weather integration
- **Frontend & Dashboard**: Multi-page UI, real-time visualization, user authentication
- **Hardware & Firmware**: ESP32 integration, sensor calibration, WiFi communication

## Deployment

### Local Development
```bash
# Terminal 1: Backend
cd florapulse-backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
source venv-frontend/bin/activate
streamlit run app.py

# Access: http://localhost:8501
```

### Production Deployment (Future)
- Backend: Docker container on AWS EC2
- Frontend: Streamlit Cloud or Heroku
- Database: AWS RDS (PostgreSQL)
- Hardware: Raspberry Pi as bridge or cloud-connected ESP32

## Known Limitations

- SQLite limited to single-user access (upgrade to PostgreSQL for multi-user)
- Streamlit session state resets on page refresh (implement persistent state with backend)
- ESP32 WiFi range limited to ~100m
- One relay module controls one pump (multi-zone requires relay array)

## Future Enhancements

1. Machine learning for plant-specific watering patterns
2. Soil nutrient analysis via API integration
3. Multi-zone irrigation system
4. Mobile app (iOS/Android)
5. Greenhouse monitoring suite
6. CO2 and soil pH sensors
7. User community & plant database
8. Integration with smart home systems (Alexa, Google Home)

## Support & Documentation

- API Docs: `http://localhost:8000/docs` (when backend running)
- Streamlit Docs: https://docs.streamlit.io
- FastAPI Docs: https://fastapi.tiangolo.com
- ESP32 Docs: https://docs.espressif.com/projects/esp-idf/

## License

Educational project - SNDT Women's University, Mumbai

---

**Last Updated**: September 30, 2026
**Version**: 1.0.0
**Status**: Development Complete, Testing Phase
