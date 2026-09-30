"""
FloraPulse Sensors — Streamlit page
Shows real-time sensor data fetched from the backend for the logged-in user.
Each sensor row shows the plant it belongs to, its ID, and live readings
(moisture %, temperature °C, humidity %) pulled from the most recent ESP32
upload.  The status badge (Good / Low / Critical) is computed client-side
based on moisture thresholds so no backend logic change is needed.

Auth guard: redirects to login if no token is in session state.
Auto-refreshes every 15 seconds via st.rerun().
"""

import base64
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Sensors | FloraPulse", page_icon="🌿", layout="wide")

# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------
st.session_state.setdefault("auth_token", None)

if not st.session_state.get("auth_token"):
    st.warning("You must log in to view your sensors.")
    if st.button("Go to Login", key="login_redirect"):
        st.switch_page("pages/2_Login.py")
    st.stop()

BACKEND_URL = "http://localhost:8000"
TOKEN = st.session_state["auth_token"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# ---------------------------------------------------------------------------
# Background image
# ---------------------------------------------------------------------------
APP_DIR = Path(__file__).parent
BG_CANDIDATES = [
    APP_DIR / "background.png",
    APP_DIR / "assets" / "background.png",
    APP_DIR / "static" / "background.png",
    APP_DIR / "images" / "background.png",
]
BG_PATH = next((p for p in BG_CANDIDATES if p.exists()), None)
bg_b64 = base64.b64encode(BG_PATH.read_bytes()).decode() if BG_PATH else ""

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_b64}");
        background-size: cover;
        background-position: center top;
        background-repeat: no-repeat;
        background-attachment: scroll;
    }}
    h1.app-title {{ text-align:center; color:#1f4d3a; margin-bottom:0; }}
    p.app-sub {{ text-align:center; color:#66786f; margin-top:4px; font-size:14px; }}
    iframe {{ border: none !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Shared card CSS (injected into every iframe)
# ---------------------------------------------------------------------------
CARD_CSS = """
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; font-family: 'Segoe UI', Roboto, -apple-system, sans-serif;
    background: transparent;
  }
  .card {
    background: #ffffff;
    border: 3px solid #5fa93a;
    border-radius: 24px;
    box-shadow: 5px 6px 0 rgba(60,110,30,0.12);
    padding: 18px 22px;
    height: calc(100vh - 6px);
    overflow: auto;
  }
  .title {
    display: flex; align-items: center; gap: 8px;
    font-weight: 600; font-size: 15px; color: #1f4d3a; margin-bottom: 12px;
  }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: #5fa93a; flex-shrink:0; }
  .stat-row { display: flex; justify-content: space-between; gap: 12px; margin-top: 14px; }
  .stat { flex: 1; text-align: left; }
  .stat label { display: block; font-size: 12px; color: #66786f; margin-bottom: 6px; }
  .stat .val { font-size: 26px; font-weight: 700; color: #2e7d54; }
  #chart { width: 100%; height: calc(100% - 34px); }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th {
    text-align: left; color: #66786f; font-weight: 600; font-size: 11.5px;
    text-transform: uppercase; letter-spacing: .3px;
    padding: 8px 10px; border-bottom: 2px solid #eef4f0;
  }
  td { padding: 10px 10px; border-bottom: 1px solid #eef4f0; color: #1c2b24; }
  tr:last-child td { border-bottom: none; }
  .badge {
    display: inline-block; padding: 3px 12px; border-radius: 12px;
    font-size: 11.5px; font-weight: 600;
  }
  .badge.good   { background: #e3f6ea; color: #2e7d54; }
  .badge.low    { background: #fdf1de; color: #b9781f; }
  .badge.crit   { background: #fbe7e6; color: #c0433f; }
  .badge.offline{ background: #f0f0f0; color: #888; }
  .conn-dot { display:inline-block; width:8px; height:8px; border-radius:50%;
              margin-right:5px; }
  .conn-online  { background:#2e7d54; }
  .conn-offline { background:#aaa; }
  .live-badge {
    display:inline-block; background:#e8f9f0; color:#2e7d54;
    font-size:11px; font-weight:700; padding:2px 9px; border-radius:20px;
    margin-left:8px; vertical-align:middle;
  }
  .ts { font-size:11px; color:#aaa; }
</style>
"""

PLOTLY_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"
BADGE_CLASS = {"Good": "good", "Low": "low", "Critical": "crit", "Offline": "offline"}


# ---------------------------------------------------------------------------
# Helpers – status computation
# ---------------------------------------------------------------------------
MOISTURE_THRESHOLDS = {"Good": (35, 100), "Low": (20, 35), "Critical": (0, 20)}


def moisture_status(value) -> str:
    if value is None:
        return "Offline"
    if value >= 35:
        return "Good"
    if value >= 20:
        return "Low"
    return "Critical"


def temp_status(value) -> str:
    if value is None:
        return "Offline"
    if 15 <= value <= 32:
        return "Good"
    if 10 <= value <= 38:
        return "Low"
    return "Critical"


def hum_status(value) -> str:
    if value is None:
        return "Offline"
    if 35 <= value <= 80:
        return "Good"
    if 20 <= value <= 90:
        return "Low"
    return "Critical"


def friendly_age(iso_str) -> str:
    """Return 'X mins ago' / 'X hrs ago' string from ISO timestamp."""
    if not iso_str:
        return "Never"
    try:
        ts = datetime.fromisoformat(iso_str)
        # Make naive if tz-aware
        if ts.tzinfo is not None:
            ts = ts.replace(tzinfo=None)
        diff = datetime.now() - ts
        secs = int(diff.total_seconds())
        if secs < 60:
            return f"{secs}s ago"
        if secs < 3600:
            return f"{secs // 60}m ago"
        return f"{secs // 3600}h ago"
    except Exception:
        return iso_str[:16] if iso_str else "Unknown"


# ---------------------------------------------------------------------------
# Fetch live sensor data from backend
# ---------------------------------------------------------------------------
@st.cache_data(ttl=12, show_spinner=False)
def fetch_sensors(token: str):
    """Fetch sensors for the current user. Cached for 12 s."""
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/sensors/my-sensors",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8,
        )
        if resp.status_code == 401:
            return None, "session_expired"
        if resp.status_code == 200:
            return resp.json().get("sensors", []), None
        return [], f"Backend error {resp.status_code}"
    except requests.RequestException as e:
        return [], f"Connection error: {e}"


# ---------------------------------------------------------------------------
# Card renderers
# ---------------------------------------------------------------------------
def render_overview_card(stats: list, height: int = 190) -> None:
    stat_html = "".join(
        f"<div class='stat'><label>{label}</label><div class='val'>{value}</div></div>"
        for label, value in stats
    )
    html = f"""
    <html><head>{CARD_CSS}</head>
    <body>
      <div class="card">
        <div class="title"><span class="dot"></span>Sensor Overview
          <span class="live-badge">⚡ LIVE</span>
        </div>
        <div class="stat-row">{stat_html}</div>
      </div>
    </body></html>
    """
    components.html(html, height=height)


def render_table_card(title: str, headers: list, rows: list, height: int = 420, badge_col: int = -1) -> None:
    head_html = "".join(f"<th>{h}</th>" for h in headers)
    body_html = ""
    for row in rows:
        cells = ""
        for i, cell in enumerate(row):
            if i == badge_col:
                cls = BADGE_CLASS.get(str(cell), "offline")
                cells += f"<td><span class='badge {cls}'>{cell}</span></td>"
            else:
                cells += f"<td>{cell}</td>"
        body_html += f"<tr>{cells}</tr>"
    html = f"""
    <html><head>{CARD_CSS}</head>
    <body>
      <div class="card">
        <div class="title"><span class="dot"></span>{title}</div>
        <table>
          <thead><tr>{head_html}</tr></thead>
          <tbody>{body_html}</tbody>
        </table>
      </div>
    </body></html>
    """
    components.html(html, height=height)


def render_chart_card(title: str, fig_data: list, layout: dict, height: int = 320) -> None:
    layout = {
        "margin": dict(l=10, r=10, t=6, b=6),
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"size": 12, "color": "#66786f"},
        "legend": {"orientation": "h", "y": -0.15, "x": 0.5, "xanchor": "center"},
        "xaxis": {"showgrid": False},
        "yaxis": {"gridcolor": "#eef4f0"},
        **layout,
    }
    html = f"""
    <html><head>{CARD_CSS}</head>
    <body>
      <div class="card">
        <div class="title"><span class="dot"></span>{title}</div>
        <div id="chart"></div>
      </div>
      <script src="{PLOTLY_CDN}"></script>
      <script>
        Plotly.newPlot(
          document.getElementById('chart'),
          {json.dumps(fig_data)},
          {json.dumps(layout)},
          {{displayModeBar: false, responsive: true}}
        );
      </script>
    </body></html>
    """
    components.html(html, height=height)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
if st.button("← Back to Dashboard", key="back_btn"):
    st.switch_page("pages/6_Dashboard.py")

st.markdown("<h1 class='app-title'>🌿 Sensors</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='app-sub'>Hardware tuned to nature's frequency &nbsp;·&nbsp; live data from your ESP32 sensors</p>",
    unsafe_allow_html=True,
)
st.write("")

# ---------------------------------------------------------------------------
# Fetch data
# ---------------------------------------------------------------------------
sensors_raw, err = fetch_sensors(TOKEN)

if err == "session_expired":
    st.session_state.auth_token = None
    st.toast("Session expired — please log in again.")
    st.switch_page("pages/2_Login.py")
    st.stop()

if err:
    st.error(f"⚠️ Could not load sensor data: {err}")
    st.info("Make sure the backend server is running at http://localhost:8000")
    st.stop()

if not sensors_raw:
    st.info("🌱 No sensors found for your account. Add a plant and connect an ESP32 sensor to get started.")
    st.stop()

# ---------------------------------------------------------------------------
# Build display rows
# ---------------------------------------------------------------------------
SENSORS_TABLE = []   # [Plant, Sensor ID, Moisture, Temp, Humidity, Status]
CONN_TABLE    = []   # [Sensor ID, Connection, Last Reading, Status]
statuses      = []

for s in sensors_raw:
    plant  = s.get("plant_name", "Unknown")
    sid    = s.get("sensor_id", "—")
    moist  = s.get("latest_moisture")
    temp   = s.get("latest_temperature")
    hum    = s.get("latest_humidity")
    online = s.get("is_connected", False)
    age    = friendly_age(s.get("last_reading_at"))

    # Format readings for display
    moist_str = f"{moist}%" if moist is not None else "—"
    temp_str  = f"{temp}°C" if temp is not None else "—"
    hum_str   = f"{hum}%" if hum is not None else "—"

    # Overall status: offline → moisture → temp → hum (worst wins)
    if not online and moist is None:
        status = "Offline"
    else:
        # Use moisture as primary health indicator
        status = moisture_status(moist)

    statuses.append(status)
    conn_label = "Online" if online else "Offline"

    SENSORS_TABLE.append([plant, sid, moist_str, temp_str, hum_str, status])
    CONN_TABLE.append([sid, conn_label, age, status])

# ---------------------------------------------------------------------------
# Summary counts
# ---------------------------------------------------------------------------
total   = len(statuses)
good    = statuses.count("Good")
low     = statuses.count("Low")
crit    = statuses.count("Critical")
offline = statuses.count("Offline")

# ---------------------------------------------------------------------------
# Overview card
# ---------------------------------------------------------------------------
render_overview_card([
    ("Total Sensors",    str(total)),
    ("Healthy",          str(good)),
    ("Needs Attention",  str(low)),
    ("Critical",         str(crit)),
    ("Offline",          str(offline)),
])

st.write("")

# ---------------------------------------------------------------------------
# Per-plant sensor table (full width)
# ---------------------------------------------------------------------------
render_table_card(
    "Live Sensor Readings by Plant",
    ["Plant", "Sensor ID", "Soil Moisture", "Temperature", "Humidity", "Status"],
    SENSORS_TABLE,
    height=max(280, 100 + 50 * len(SENSORS_TABLE)),
    badge_col=5,
)

st.write("")

# ---------------------------------------------------------------------------
# Sensor health: donut chart + connection detail table
# ---------------------------------------------------------------------------
health_left, health_right = st.columns([1, 1.4])

with health_left:
    STATUS_COLORS = {
        "Good": "#2e7d54",
        "Low": "#e0a530",
        "Critical": "#c0433f",
        "Offline": "#aaaaaa",
    }
    pie_labels = ["Good", "Low", "Critical", "Offline"]
    pie_values = [good, low, crit, offline]
    # Remove zero-count slices
    filtered = [(lbl, val) for lbl, val in zip(pie_labels, pie_values) if val > 0]
    fl, fv = zip(*filtered) if filtered else (["Good"], [1])
    fc = [STATUS_COLORS[lbl] for lbl in fl]

    render_chart_card(
        "Sensor Health Distribution",
        [
            {
                "type": "pie",
                "labels": list(fl),
                "values": list(fv),
                "hole": 0.6,
                "marker": {"colors": fc},
            }
        ],
        {"legend": {"orientation": "h", "y": -0.15, "x": 0.5, "xanchor": "center"}},
        height=340,
    )

with health_right:
    render_table_card(
        "Connection & Last Reading",
        ["Sensor ID", "Connection", "Last Reading", "Status"],
        CONN_TABLE,
        height=340,
        badge_col=3,
    )

# ---------------------------------------------------------------------------
# Auto-refresh every 15 seconds
# ---------------------------------------------------------------------------
st.write("")
refresh_placeholder = st.empty()
refresh_placeholder.caption(f"⏱️ Auto-refreshing every 15 seconds · Last updated: {datetime.now().strftime('%H:%M:%S')}")

time.sleep(15)
st.cache_data.clear()
st.rerun()