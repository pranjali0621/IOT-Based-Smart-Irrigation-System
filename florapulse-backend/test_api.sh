#!/bin/bash

API="http://localhost:8000"

echo "=========================================="
echo "1. REGISTER USER"
echo "=========================================="
REGISTER=$(curl -s -X POST "$API/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "isheka",
    "email": "isheka@test.com",
    "password": "password123",
    "full_name": "Isheka Singh"
  }')

echo "$REGISTER" | python3 -m json.tool

if echo "$REGISTER" | grep -q '"id"'; then
  echo "✅ Registration successful"
else
  echo "❌ Registration failed - check server logs"
  echo "$REGISTER"
  exit 1
fi

echo ""
echo "=========================================="
echo "2. LOGIN"
echo "=========================================="
LOGIN=$(curl -s -X POST "$API/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "isheka",
    "password": "password123"
  }')

echo "$LOGIN" | python3 -m json.tool

TOKEN=$(echo "$LOGIN" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi

echo ""
echo "✅ Token received: ${TOKEN:0:30}..."
echo ""

echo "=========================================="
echo "3. GET CURRENT USER"
echo "=========================================="
curl -s -X GET "$API/api/auth/me" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=========================================="
echo "4. CREATE PLANT"
echo "=========================================="
PLANT=$(curl -s -X POST "$API/api/plants/create" \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=Monstera" \
  -F "species=Monstera deliciosa" \
  -F "location=Living Room" \
  -F "description=Big green plant")

echo "$PLANT" | python3 -m json.tool

PLANT_ID=$(echo "$PLANT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)

if [ -z "$PLANT_ID" ]; then
  echo "❌ Plant creation failed"
  exit 1
fi

echo ""
echo "✅ Plant created: ID $PLANT_ID"
echo ""

echo "=========================================="
echo "5. GET MY PLANTS"
echo "=========================================="
curl -s -X GET "$API/api/plants/my-plants" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=========================================="
echo "6. REGISTER SENSOR"
echo "=========================================="
SENSOR=$(curl -s -X POST "$API/api/sensors/register" \
  -H "Authorization: Bearer $TOKEN" \
  -F "plant_id=$PLANT_ID" \
  -F "sensor_id=ESP32_DEMO01" \
  -F "sensor_name=Moisture Sensor")

echo "$SENSOR" | python3 -m json.tool
echo ""

echo "=========================================="
echo "7. GET SENSOR STATUS (before data)"
echo "=========================================="
curl -s -X GET "$API/api/sensors/ESP32_DEMO01/status" | python3 -m json.tool
echo ""

echo "=========================================="
echo "8. UPLOAD SENSOR DATA"
echo "=========================================="
UPLOAD=$(curl -s -X POST "$API/api/sensor-data/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "ESP32_DEMO01",
    "moisture": 55.5,
    "temperature": 28.3,
    "humidity": 65.0,
    "rain_detected": false
  }')

echo "$UPLOAD" | python3 -m json.tool
echo ""

echo "=========================================="
echo "9. GET SENSOR STATUS (after data)"
echo "=========================================="
curl -s -X GET "$API/api/sensors/ESP32_DEMO01/status" | python3 -m json.tool
echo ""

echo "=========================================="
echo "10. GET SYSTEM STATUS"
echo "=========================================="
curl -s -X GET "$API/api/status" | python3 -m json.tool
echo ""

echo "=========================================="
echo "11. GET IRRIGATION DECISION"
echo "=========================================="
curl -s -X POST "$API/api/irrigation/decide" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "ESP32_DEMO01",
    "moisture": 55.5,
    "temperature": 28.3,
    "humidity": 65.0,
    "rain_detected": false
  }' | python3 -m json.tool
echo ""

echo "=========================================="
echo "✅ ALL TESTS COMPLETE!"
echo "=========================================="
