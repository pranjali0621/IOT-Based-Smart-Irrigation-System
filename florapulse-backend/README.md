# FloraPulse Backend

## Overview
FastAPI-based backend for the Smart IoT Plant Irrigation System.

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. View API Docs
Open browser: http://localhost:8000/docs

## Project Structure
- `app/main.py` - FastAPI application entry point
- `app/database.py` - SQLAlchemy database setup
- `app/database_models.py` - ORM models
- `app/models.py` - Pydantic schemas
- `app/services/` - Business logic
- `app/utils/` - Validation & helpers
- `simulate_esp32.py` - Mock data generator

## API Endpoints
- `POST /api/sensor-data/upload` - Submit sensor readings
- `GET /api/sensor-data/history` - Fetch historical data
- `GET /api/status` - Get current system status
- `POST /api/irrigation/decide` - Get irrigation decision
- `GET /api/dashboard/live` - Get dashboard data
