# FloraPulse Backend

Smart IoT-based plant irrigation system with automated decision-making and watering predictions.

## Overview

FloraPulse is a complete backend for an intelligent plant watering system that:
- **Monitors** soil moisture, temperature, humidity, and rainfall in real-time
- **Validates** sensor data to ensure quality and prevent errors
- **Decides** when to water based on soil conditions and weather forecasts
- **Predicts** when the next watering will be needed using historical trends
- **Logs** all decisions and sensor readings for analysis and improvement

The system is designed to be affordable, reliable, and suitable for home gardens, hostels, offices, and small-scale gardening applications.

## Quick Start

### 1. Prerequisites
- Python 3.12+
- pip (Python package manager)

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd florapulse-backend

# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start the simulator (mock ESP32)
python simulate_esp32.py

# View API documentation
# Open browser: http://localhost:8000/docs
```

## System Architecture

### Components

**1. Sensor Input (ESP32 or Simulator)**
- Reads: Soil moisture, temperature, humidity, rain status
- Sends: JSON via HTTP POST every 30 seconds (real) or 10 seconds (simulator)

**2. Backend API (FastAPI)**
- Receives sensor data
- Validates against ranges (moisture 0-100%, temp -40-80°C)
- Stores in database
- Makes irrigation decisions
- Calculates predictions

**3. Database (SQLite)**
- Stores: Sensor readings, decisions, pump events, system status
- Enables: Historical analysis, trend calculation

**4. Frontend (Streamlit - External)**
- Displays: Live sensor data, historical charts, predictions
- Shows: Confidence scores, decision reasons

### Data Flow
Sensor/Simulator
↓ HTTP POST
FastAPI Backend
├─ Validator (reject bad data)
├─ Database (store readings)
├─ Decision Logic (WATER/SKIP/MONITOR)
├─ Prediction Engine (estimate next watering)
└─ Logger (store decisions)
↓
SQLite Database
↓
Streamlit Dashboard
↓
User Interface


## API Endpoints

All endpoints are documented at: http://localhost:8000/docs

### Sensor Data

**POST** `/api/sensor-data/upload`
- Submit a sensor reading from ESP32
- Request: `{"moisture": 45.5, "temperature": 28.3, "humidity": 65.0, "rain_detected": false}`
- Response: `{"status": "success", "id": 1, "saved_at": "..."}`
- Validation: Moisture 0-100%, Temp -40-80°C, Humidity 0-100%

**GET** `/api/sensor-data/history?hours=24&limit=100`
- Fetch historical sensor readings
- Query params: hours (default 24), limit (default 100)
- Response: Array of sensor readings with timestamps

### Irrigation Decisions

**GET** `/api/status`
- Current system state
- Response: Pump status, last moisture, last temperature, last update time

**POST** `/api/irrigation/decide`
- Get irrigation decision for current conditions
- Request: `{"moisture": 45, "rain_detected": false}`
- Response: `{"decision": "WATER|SKIP|MONITOR", "reason": "...", "confidence": 0.95}`

### Predictions

**GET** `/api/prediction/next-watering`
- Estimate when next watering will be needed
- Uses 48-hour historical depletion rate
- Response: Hours until dry, estimated time, confidence score

### Dashboard

**GET** `/api/dashboard/live`
- Aggregated data for Streamlit frontend
- Response: Current readings, last 10 readings, recent decisions, prediction, pump status

### Health

**GET** `/health`
- Check if API is running
- Response: `{"status": "healthy", "timestamp": "...", "service": "FloraPulse Backend"}`

## Decision Logic

The system makes three types of decisions:

| Decision | Condition | Confidence | Action |
|----------|-----------|-----------|--------|
| **WATER** | Moisture < 35% AND no rain | 0.95 | Start pump, water soil |
| **SKIP** | Moisture adequate OR rain forecast | 0.90-0.98 | Don't water, avoid overwatering |
| **MONITOR** | Moisture 35-50% AND no rain | 0.85 | Check next reading, prepare for watering |

Decision factors:
- **Moisture threshold (dry):** 35% (configurable in `.env`)
- **Moisture threshold (optimal):** 50% (configurable)
- **Rain logic:** Uses OR (any rain = skip) to prevent overwatering
- **Confidence:** Higher for clear conditions, lower for ambiguous cases

## Predictions

The system estimates when watering will be needed:

1. Analyzes last 48 hours of sensor data
2. Calculates depletion rate: `(initial% - current%) / hours = %/hour`
3. Predicts: `hours_until_dry = (current% - threshold%) / depletion_rate`
4. Sets confidence based on time horizon:
   - < 24 hours: 0.85 (reliable)
   - 24-48 hours: 0.75 (moderately reliable)
   - > 48 hours: 0.60 (speculative)

Example: If soil is 60% and depletes at 1%/hour with 35% threshold:
- Buffer: 60% - 35% = 25%
- Time: 25% / 1%/hour = 25 hours
- Prediction: "Water in ~25 hours"

## Project Structure
florapulse-backend/
├── app/
│ ├── init.py
│ ├── main.py # FastAPI app, routes, endpoints
│ ├── config.py # Load settings from .env
│ ├── database.py # SQLAlchemy setup
│ ├── database_models.py # ORM models (4 tables)
│ ├── models.py # Pydantic schemas (validation)
│ │
│ ├── services/
│ │ ├── init.py
│ │ ├── irrigation_engine.py # Decision logic (WATER/SKIP/MONITOR)
│ │ └── prediction_engine.py # Depletion rate, watering predictions
│ │
│ └── utils/
│ ├── init.py
│ └── validators.py # Input validation (ranges)
│
├── docs/ # Documentation (daily walkthroughs)
│ ├── INDEX.md
│ ├── day-1/, day-2/, ..., day-5/
│ └── README.md
│
├── tests/ # Unit tests (Phase 2)
│ └── init.py
│
├── simulate_esp32.py # Mock ESP32 (generates test data)
├── requirements.txt # Python dependencies
├── .env # Configuration (thresholds, API keys)
├── .gitignore # Git ignore rules
├── florapulse.db # SQLite database (created on first run)
└── README.md # This file


## Configuration

Edit `.env` to customize behavior:

```env
# Database
DATABASE_URL=sqlite:///./florapulse.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Irrigation Thresholds
MOISTURE_THRESHOLD_DRY=35          # Water below this %
MOISTURE_THRESHOLD_OPTIMAL=50      # Monitor below this %
MOISTURE_THRESHOLD_WET=70          # Upper bound

# Simulation (for testing without hardware)
SIMULATION_ENABLED=true
SIMULATION_INTERVAL_SECONDS=10     # Send data every N seconds
```

## Database Schema

### sensor_readings
| Column | Type | Purpose |
|--------|------|---------|
| id | Integer (PK) | Unique identifier |
| timestamp | DateTime | When reading was taken |
| moisture | Float | Soil moisture 0-100% |
| temperature | Float | Temperature in °C |
| humidity | Float | Humidity 0-100% |
| rain_detected | Boolean | Is rain falling? |

### irrigation_decisions
| Column | Type | Purpose |
|--------|------|---------|
| id | Integer (PK) | Unique identifier |
| timestamp | DateTime | When decision was made |
| moisture_level | Float | Moisture at time of decision |
| decision | String | WATER, SKIP, or MONITOR |
| reason | String | Why this decision |
| confidence | Float | 0.0-1.0 confidence score |

### pump_events
| Column | Type | Purpose |
|--------|------|---------|
| id | Integer (PK) | Unique identifier |
| timestamp | DateTime | When pump event occurred |
| action | String | ON or OFF |
| duration_seconds | Integer | How long pump ran |
| reason | String | auto or manual |

### system_status
| Column | Type | Purpose |
|--------|------|---------|
| id | Integer (PK) | Unique identifier |
| last_update | DateTime | Last system update |
| pump_status | String | Current pump ON/OFF |
| last_moisture | Float | Most recent moisture reading |
| last_temperature | Float | Most recent temperature |
| last_humidity | Float | Most recent humidity |
| estimated_hours_to_watering | Float | Next watering ETA |

## Testing

### 1. Validation Testing

```bash
# Valid data (should succeed)
curl -X POST http://localhost:8000/api/sensor-data/upload \
  -H "Content-Type: application/json" \
  -d '{"moisture": 45.5, "temperature": 28, "humidity": 65}'

# Invalid data (should fail with 400)
curl -X POST http://localhost:8000/api/sensor-data/upload \
  -H "Content-Type: application/json" \
  -d '{"moisture": 150}'  # Out of range
```

### 2. Decision Logic Testing

```bash
# Dry + no rain → WATER
curl -X POST http://localhost:8000/api/irrigation/decide \
  -d '{"moisture": 30, "rain_detected": false}'

# Dry + rain → SKIP
curl -X POST http://localhost:8000/api/irrigation/decide \
  -d '{"moisture": 30, "rain_detected": true}'

# Optimal → SKIP
curl -X POST http://localhost:8000/api/irrigation/decide \
  -d '{"moisture": 55, "rain_detected": false}'
```

### 3. Prediction Testing

```bash
# After 5+ minutes of simulator data
curl http://localhost:8000/api/prediction/next-watering
```

### 4. View API Docs
http://localhost:8000/docs


Interactive "Try it out" interface for all endpoints.

## Hardware Integration

### Transitioning from Simulator to Real ESP32

The simulator proves the software works. When real hardware arrives:

1. **Flash ESP32** with Arduino C++ code that:
   - Reads sensors (moisture, DHT22, rain)
   - Creates same JSON structure
   - POSTs to same endpoint

2. **No backend changes needed** — Same API endpoint, same request format

3. **Update simulator interval** — Change 10s to 30s if desired

Example Arduino code:
```cpp
#include <WiFi.h>
#include <HTTPClient.h>

void loop() {
  float moisture = analogRead(A0) / 40.95;  // 0-100%
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  bool rain = digitalRead(D1) == LOW;
  
  String payload = "{\"moisture\": " + String(moisture) + 
                   ", \"temperature\": " + String(temp) + 
                   ", \"humidity\": " + String(humidity) + 
                   ", \"rain_detected\": " + String(rain) + "}";
  
  HTTPClient http;
  http.begin("http://YOUR_BACKEND_IP:8000/api/sensor-data/upload");
  http.addHeader("Content-Type", "application/json");
  http.POST(payload);
  http.end();
  
  delay(30000);  // 30 seconds
}
```

## Technologies Used

- **Framework:** FastAPI (Python async web framework)
- **Database:** SQLite (file-based, no server needed)
- **ORM:** SQLAlchemy (Python ↔ Database mapping)
- **Validation:** Pydantic (input/output validation)
- **Web Server:** Uvicorn (ASGI server)
- **Hardware Simulation:** Python requests (HTTP client)

## Development Roadmap

### Phase 1 (Days 1-5) — Core System ✅
- [x] FastAPI backend
- [x] SQLite database
- [x] Sensor data API
- [x] Validation
- [x] Decision logic
- [x] Predictions
- [x] Simulator

### Phase 2 — Enhancement
- [ ] OpenWeather API integration (weather forecasting)
- [ ] Advanced ML predictions (instead of linear depletion)
- [ ] Pump relay control
- [ ] WiFi configuration for ESP32
- [ ] Mobile app
- [ ] Cloud deployment

### Phase 3 — Production
- [ ] PostgreSQL (scalable database)
- [ ] Load testing and optimization
- [ ] Comprehensive logging
- [ ] Security hardening
- [ ] User authentication
- [ ] Data backup strategy

## License

[Your License Here]

## Authors

- Isheka Singh (Backend, Decision Logic, Predictions)
- Shreeya Shete (Frontend, Dashboard)

## Support

For issues, questions, or suggestions:
1. Check API docs: http://localhost:8000/docs
2. Review documentation in `docs/` folder
3. Open an issue in GitHub

---

**System Status:** 70% Complete (Day 3 of 5)
**Next Step:** Day 4 - Polish & Documentation (in progress)
**Final Step:** Day 5 - Demo Ready & Presentation
