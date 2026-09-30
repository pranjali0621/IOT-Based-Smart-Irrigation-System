import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Smart Garden | Admin",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# CONSTANTS & STYLES
# ==================================================
BACKEND_URL = "http://localhost:8000"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600&family=Nunito:wght@400;600;700&display=swap');

html, body, .stApp, .stApp *:not([data-testid="stIconMaterial"]), [data-baseweb="popover"] * {
    font-family: 'Nunito', 'Segoe UI', sans-serif;
}

.title-font {
    font-family: 'Fredoka', 'Nunito', sans-serif !important;
}

.admin-card {
    background-color: #EAF7E6;
    border: 2px solid #7ED321;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    color: #087522;
}

.admin-card-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.stat-box {
    background: white;
    border: 2px solid #7ED321;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}

.stat-value {
    font-size: 32px;
    font-weight: 700;
    font-family: 'Fredoka', 'Nunito', sans-serif;
    color: #087522;
}

.stat-label {
    font-size: 14px;
    color: #2b3f12;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# AUTH GUARD
# ==================================================
token = st.session_state.get("auth_token")
is_admin = st.session_state.get("is_admin", False)

if not token or not is_admin:
    st.markdown("<div style='text-align: center; padding: 50px;'><h2 class='title-font'>Admin access only</h2><p>You must be logged in as an administrator to view this page.</p></div>", unsafe_allow_html=True)
    if st.button("← Go to Login"):
        st.switch_page("pages/2_Login.py")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}

# ==================================================
# DATA FETCHING
# ==================================================
@st.cache_data(ttl=5)  # Cache for 5 seconds to avoid spamming the backend on UI interactions
def fetch_data(endpoint: str, params: dict = None):
    try:
        res = requests.get(f"{BACKEND_URL}/api/admin/{endpoint}", headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Error fetching {endpoint}: {res.text}")
            return []
    except Exception as e:
        st.error(f"Connection error: {e}")
        return []

# Force refresh function
def clear_cache():
    fetch_data.clear()

# ==================================================
# HEADER & REFRESH
# ==================================================
col1, col2, col3 = st.columns([4, 1, 1])
with col1:
    st.markdown("<h1 class='title-font'>🔧 Admin Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; color: #68803a;'>System overview & user management</p>", unsafe_allow_html=True)
with col2:
    st.button("🔄 Refresh", on_click=clear_cache, width="stretch")
with col3:
    def logout():
        st.session_state.auth_token = None
        st.session_state.user = None
        st.session_state.is_admin = False
    
    if st.button("🚪 Logout", on_click=logout, width="stretch"):
        st.switch_page("pages/2_Login.py")

# Fetch all data
users_data = fetch_data("users")
plants_data = fetch_data("plants")
sensors_data = fetch_data("sensors")
readings_data = fetch_data("readings", {"limit": 50})

st.markdown("---")

# ==================================================
# SECTION 7: STATISTICS
# ==================================================
st.markdown("<div class='admin-card-title'>📊 System Statistics</div>", unsafe_allow_html=True)

stat1, stat2, stat3, stat4 = st.columns(4)

with stat1:
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{len(users_data)}</div>
            <div class="stat-label">Total Users</div>
        </div>
    """, unsafe_allow_html=True)
with stat2:
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{len(plants_data)}</div>
            <div class="stat-label">Total Plants</div>
        </div>
    """, unsafe_allow_html=True)
with stat3:
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{len(sensors_data)}</div>
            <div class="stat-label">Total Sensors</div>
        </div>
    """, unsafe_allow_html=True)
with stat4:
    # Approximate based on recent readings
    st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{len(readings_data)}</div>
            <div class="stat-label">Recent Readings</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==================================================
# SECTION 3: USERS TABLE
# ==================================================
with st.container():
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("<div class='admin-card-title'>👤 Users</div>", unsafe_allow_html=True)
    if users_data:
        df_users = pd.DataFrame(users_data)
        # Rename columns for display
        df_users = df_users.rename(columns={
            "id": "ID",
            "username": "Username",
            "email": "Email",
            "full_name": "Full Name",
            "created_at": "Created"
        })
        # Format datetime
        if "Created" in df_users.columns:
            df_users["Created"] = pd.to_datetime(df_users["Created"]).dt.strftime("%Y-%m-%d %H:%M")
        
        st.dataframe(df_users, hide_index=True, width="stretch")
    else:
        st.info("No users found.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# SECTION 4: PLANTS TABLE
# ==================================================
with st.container():
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("<div class='admin-card-title'>🌱 Plants</div>", unsafe_allow_html=True)
    if plants_data:
        df_plants = pd.DataFrame(plants_data)
        df_plants = df_plants.rename(columns={
            "id": "ID",
            "plant_name": "Plant Name",
            "owner_username": "Owner",
            "created_at": "Created"
        })
        if "Created" in df_plants.columns:
            df_plants["Created"] = pd.to_datetime(df_plants["Created"]).dt.strftime("%Y-%m-%d %H:%M")
        
        st.dataframe(df_plants, hide_index=True, width="stretch")
    else:
        st.info("No plants found.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# SECTION 5: SENSORS TABLE
# ==================================================
with st.container():
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("<div class='admin-card-title'>📡 Sensors</div>", unsafe_allow_html=True)
    if sensors_data:
        df_sensors = pd.DataFrame(sensors_data)
        # Apply dot for connection status
        df_sensors["is_connected"] = df_sensors["is_connected"].apply(
            lambda x: "🟢 Connected" if x else "🔴 Disconnected"
        )
        df_sensors = df_sensors.rename(columns={
            "sensor_id": "Sensor ID",
            "plant_name": "Plant",
            "owner_username": "Owner",
            "is_connected": "Status",
            "last_data_received": "Last Data"
        })
        if "Last Data" in df_sensors.columns:
            df_sensors["Last Data"] = pd.to_datetime(df_sensors["Last Data"]).dt.strftime("%Y-%m-%d %H:%M")
            df_sensors["Last Data"] = df_sensors["Last Data"].fillna("Never")
            
        st.dataframe(df_sensors, hide_index=True, width="stretch")
    else:
        st.info("No sensors found.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# SECTION 6: LATEST READINGS
# ==================================================
with st.container():
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("<div class='admin-card-title'>📊 Latest Readings (Live Feed)</div>", unsafe_allow_html=True)
    if readings_data:
        df_readings = pd.DataFrame(readings_data)
        df_readings = df_readings.rename(columns={
            "sensor_id": "Sensor",
            "plant_name": "Plant",
            "moisture": "Moisture (%)",
            "temperature": "Temp (°C)",
            "humidity": "Humidity (%)",
            "timestamp": "Time"
        })
        if "Time" in df_readings.columns:
            df_readings["Time"] = pd.to_datetime(df_readings["Time"]).dt.strftime("%H:%M:%S")
            
        st.dataframe(df_readings, hide_index=True, width="stretch")
    else:
        st.info("No recent readings found.")
    st.markdown("</div>", unsafe_allow_html=True)

# Navigation
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🏠 Back to Dashboard"):
    st.switch_page("pages/6_Dashboard.py")
    