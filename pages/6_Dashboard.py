import base64
import math
import random
import re
import time as _time
from datetime import datetime, time, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
import requests

st.set_page_config(
    page_title="Smart Garden | Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# BACKEND CONFIG
# ==================================================
BACKEND_URL = "http://localhost:8000"

# ==================================================
# AUTH GUARD
# ==================================================
if st.session_state.get("auth_token") is None:
    st.markdown(
        "<div style='text-align: center; padding: 50px;'><h2>You must login first</h2></div>",
        unsafe_allow_html=True
    )
    if st.button("Go to Login"):
        st.switch_page("pages/2_Login.py")
    st.stop()

# ==================================================
# PATHS & CONSTANTS
# ==================================================
ASSETS = Path(__file__).parent / "assets"
NAV = [
    ("Dashboard", "🏠"),
    ("My plants", "🪴"),
    ("Weather Forecast", "⛅"),
    ("Sensors", "📡"),
    ("Analytics", "📊"),
    ("About us", "ℹ️"),
    ("Settings", "⚙️")
]
ART = {
    "plant": "plant.png",
    "can": "watering_can.png",
    "pump": "pump.png"
}
CITIES = {
    "Mumbai": (30, 80, .6),
    "Delhi": (33, 55, .25),
    "Bengaluru": (27, 70, .45),
    "Chennai": (33, 72, .35),
    "Kolkata": (32, 78, .5),
    "London": (16, 72, .4),
    "New York": (21, 60, .3)
}
KEEP = [
    "mode", "thr", "pump_on", "sched", "auto_sched",
    "unit", "city", "live", "sel_plant", "metric"
]

LAYOUT = {
    "nav": (0, 0, 227, 697),
    "health": (268, 40, 380, 303),
    "water": (648, 40, 309, 303),
    "weather": (957, 40, 325, 503),
    "pump": (268, 372, 689, 171),
    "sensors": (268, 573, 1014, 124),
    "panel": (268, 40, 1014, 657)
}

clamp = lambda v, lo, hi: max(lo, min(hi, v))

# ==================================================
# BACKEND API FUNCTIONS
# ==================================================
def load_plants_from_backend(token: str) -> dict:
    """Fetch plants from backend and convert to dashboard format"""
    try:
        if not token:
            st.error("No auth token available")
            return {}

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/api/plants/my-plants",
            headers=headers,
            timeout=10
        )

        if response.status_code == 401:
            st.session_state.auth_token = None
            st.toast("Session expired, please login again")
            st.switch_page("pages/2_Login.py")
            st.stop()

        if response.status_code != 200:
            st.error(f"Failed to load plants (status {response.status_code}): {response.text}")
            return {}

        data = response.json()
        backend_plants = data.get("plants", [])
        plants_dict = {}

        for plant in backend_plants:
            name = plant.get("name", f"Plant {plant.get('id')}")
            plants_dict[name] = {
                "id": plant.get("id"),
                "emoji": "🌱",
                "mlo": 30,
                "mhi": 70,
                "tlo": 16,
                "thi": 30,
                "moisture": 0,
                "temp": 0,
                "hum": 0,
                "light": 0,
                "hist": []
            }

        return plants_dict

    except Exception as e:
        st.error(f"Error loading plants: {str(e)}")
        return {}


def load_sensor_history(plant_id: int, token: str, limit: int = 60) -> list:
    """Fetch sensor reading history from backend"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/api/sensor-data/history?plant_id={plant_id}&limit={limit}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 401:
            st.session_state.auth_token = None
            st.toast("Session expired")
            st.switch_page("pages/2_Login.py")
            st.stop()

        if response.status_code != 200:
            return []

        readings = response.json().get("readings", [])
        return readings

    except Exception as e:
        st.warning(f"Could not load sensor history: {e}")
        return []

def load_next_watering_prediction(plant_id: int, token: str) -> dict:
    """Fetch next watering prediction from backend."""
    try:
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(
            f"{BACKEND_URL}/api/plants/{plant_id}/next-watering-prediction",
            headers=headers,
            timeout=10
        )

        if response.status_code == 401:
            st.session_state.auth_token = None
            st.toast("Session expired")
            st.switch_page("pages/2_Login.py")
            st.stop()

        if response.status_code != 200:
            st.warning(
                f"Could not load watering prediction "
                f"(status {response.status_code})"
            )
            return {}

        return response.json()

    except Exception as e:
        st.warning(f"Could not load watering prediction: {e}")
        return {}

def get_current_user(token: str) -> str:
    """Get logged-in user name from backend"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/api/auth/me",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json().get("username", "Gardener")
    except:
        pass

    return "Gardener"

# ==================================================
# STYLES
# ==================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600&family=Nunito:wght@400;600;700&display=swap');
:root{--u:min(100vw / 1366, 100vh / 768);--line:#6b9a22;--ink:#2b3f12;--mute:#68803a;--soft:#f3f9ec;
      --good:#6aaa4a;--warn:#e0a030;--bad:#d0583a;--head:'Fredoka','Nunito',sans-serif}
html,body,.stApp,.stApp *:not([data-testid="stIconMaterial"]),[data-baseweb="popover"] *{font-family:'Nunito','Segoe UI',sans-serif}
.h,.brand,.big,.mv,.ring b,.wnow b,.stt b,.pst b,.greet,.avatar-name,.chips b,.stats b,.snap b{font-family:var(--head)!important}
.stApp{background:%%BG%% center / cover no-repeat fixed;font-size:@{15}}
header,[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],footer,#MainMenu{display:none!important}
.block-container,[data-testid="stMainBlockContainer"]{max-width:100%!important;padding:@{38} 0 0!important}
.st-key-stage{position:relative;width:@{1282};height:@{697};margin:0 auto;gap:0}

:is(.st-key-nav,.st-key-health,.st-key-water,.st-key-weather,.st-key-pump,.st-key-sensors,.st-key-panel){
  position:absolute;box-sizing:border-box;background:#fff;color:var(--ink);overflow:hidden;
  border:max(2px,@{3}) solid var(--line);border-radius:@{36};padding:@{20} @{24};gap:@{8};
  box-shadow:@{9} @{11} @{16} rgba(0,0,0,.2)}
:is(.st-key-nav,.st-key-health,.st-key-water,.st-key-weather,.st-key-pump,.st-key-sensors,.st-key-panel)>*{flex-shrink:0}
.st-key-pump{padding:@{14} @{26}}
.st-key-sensors{justify-content:center;padding:@{12} @{26}}
.st-key-panel{overflow-y:auto}
.stApp [data-testid="stMarkdownContainer"] p{margin:0}
[data-testid="stHorizontalBlock"]{gap:@{14}}

.h{font-size:@{22};font-weight:500;line-height:1.15;color:var(--ink)}
.hdr{display:flex;align-items:center;justify-content:space-between;gap:@{10};min-height:@{56}}
.big{font-size:@{40};font-weight:500;line-height:1.05}
.sub{font-size:@{14};color:var(--mute)}
[data-testid="stWidgetLabel"] p{font-size:@{14};color:var(--mute)}
[data-baseweb="select"]>div{min-height:@{38};height:@{38};border-radius:@{12};background:var(--soft);border-color:#b9d98f}
[data-baseweb="select"] *,[data-testid="stTimeInput"] input{font-size:@{15}}
[data-testid="stTimeInput"] [data-baseweb="input"]{border-radius:@{12};background:var(--soft)}
[data-testid="stTimeInput"] input{height:@{38};background:var(--soft)}
[data-testid="stCaptionContainer"] p,[data-testid="stToggle"] p,[data-testid="stRadio"] label p{font-size:@{14};color:var(--ink)}
[data-baseweb="checkbox"]:has(input:checked)>:is(div,span):first-child{background:var(--good)!important}
[data-baseweb="radio"]:has(input:checked)>:is(div,span):first-child{background:var(--good)!important;border-color:var(--good)!important}
[data-baseweb="slider"] [role="slider"]{background:var(--good)!important;box-shadow:none!important}

.art{flex:none;background:center / contain no-repeat}
%%ART%%

.st-key-nav{gap:@{5}}
.brand{display:flex;align-items:center;gap:@{10};font-size:@{21};font-weight:500;white-space:nowrap;padding:@{2} 0 @{6}}
.brand i{width:@{38};height:@{38};border-radius:50%;display:grid;place-items:center;font-style:normal;font-size:@{20};
  background:linear-gradient(135deg,#dff2c6,#b9e08a)}
.st-key-nav button{justify-content:flex-start!important;gap:@{8};width:100%;min-height:0;height:@{42};padding:0 @{14};
  border:none!important;border-radius:@{21};background:transparent!important;box-shadow:none!important;
  transition:transform .15s ease,background .15s ease}
.st-key-nav button p{font-size:@{17};font-weight:600;color:var(--ink);white-space:nowrap}
.st-key-nav button:hover{background:#eaf5dc!important;transform:translateX(@{4})}
.st-key-nav button:is([kind=primary],[data-testid=stBaseButton-primary]){
  background:linear-gradient(90deg,#d9efc0,#eef8e2)!important;box-shadow:inset @{4} 0 0 var(--line)!important}
.st-key-nav button:is([kind=primary],[data-testid=stBaseButton-primary]) p{font-weight:700}
@media (prefers-reduced-motion:reduce){.st-key-nav button:hover{transform:none}}
.st-key-snapwrap{margin-top:auto}
.snap{background:var(--soft);border-radius:@{18};padding:@{10} @{14};font-size:@{14};color:var(--mute)}
.snap b{display:block;font-size:@{17};font-weight:500;color:var(--ink)}

.st-key-profile{position:fixed;top:@{14};right:@{26};z-index:1000;flex-direction:row;align-items:center;gap:@{10};width:auto}
.greet{font-size:@{17};font-weight:500;color:var(--ink);white-space:nowrap}
.st-key-profile [data-testid="stPopover"] button{width:@{46};height:@{46};min-height:0;padding:0;border-radius:50%;
  border:max(2px,@{3}) solid #fff;background:linear-gradient(135deg,#8fdc55,#5fa83a);
  box-shadow:@{3} @{5} @{10} rgba(0,0,0,.25)}
.st-key-profile [data-testid="stPopover"] button p{font-family:var(--head);font-size:@{20};color:#fff;font-weight:500}
.st-key-profile [data-testid="stPopover"] button [data-testid="stIconMaterial"]{display:none}
.avatar-name{font-size:@{18};font-weight:500}

:is(.st-key-water,.st-key-panel) button{width:100%;border:none;border-radius:999px;min-height:0;height:@{40};
  background:linear-gradient(90deg,#8fdc55,#c9e25f);box-shadow:@{4} @{6} @{8} rgba(0,0,0,.2)}
:is(.st-key-water,.st-key-panel) button p{font-size:@{17};font-weight:700;color:#fff}

.hrow{display:flex;align-items:center;gap:@{18}}
.ring{flex:none;width:@{104};height:@{104};border-radius:50%;display:flex;flex-direction:column;align-items:center;
  justify-content:center;background:radial-gradient(closest-side,#fff 76%,transparent 78%),conic-gradient(var(--c) calc(var(--s) * 1%),#e4efd3 0)}
.ring b{font-size:@{30};font-weight:500;line-height:1}.ring span{font-size:@{12};color:var(--mute)}
.stats{flex:1;display:flex;flex-direction:column;gap:@{6}}
.stats div{display:flex;justify-content:space-between;align-items:center;background:var(--soft);border-radius:@{12};padding:@{6} @{12};font-size:@{14};color:var(--mute)}
.stats b{font-size:@{17};font-weight:500;color:var(--ink)}

.wtop{display:flex;align-items:center;justify-content:space-between;min-height:@{92}}

.wnow{display:flex;align-items:center;justify-content:center;gap:@{12};min-height:@{54}}
.wnow span{font-size:@{40}}.wnow b{font-size:@{38};font-weight:500}
.chips{display:grid;grid-template-columns:repeat(3,1fr);gap:@{8}}
.chips div{text-align:center;font-size:@{13};color:var(--mute);background:var(--soft);border-radius:@{12};padding:@{5} 0}
.chips b{display:block;font-size:@{17};font-weight:500;color:var(--ink)}
.wlist{display:flex;flex-direction:column}
.wrow{display:grid;grid-template-columns:1fr .5fr 1.6fr 1fr;align-items:center;font-size:@{15};height:@{31};padding:0 @{10};border-radius:@{10}}
.wrow:nth-child(odd){background:var(--soft)}
.tip{font-size:@{14};background:#fff6dc;border-radius:@{12};padding:@{7} @{12};line-height:1.3}

.pst{display:flex;align-items:center;gap:@{14}}.pst b{font-size:@{26};font-weight:500;display:block;line-height:1.1}
.pst small{font-size:@{14};color:var(--mute)}
.dot{flex:none;width:@{40};height:@{40};border-radius:50%;background:#cfd8c3}
.dot.on{background:var(--good);animation:pulse 1.6s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(106,170,74,.55)}100%{box-shadow:0 0 0 @{16} rgba(106,170,74,0)}}
@media (prefers-reduced-motion:reduce){.dot.on{animation:none}}

.sens{display:grid;grid-template-columns:@{160} repeat(5,1fr);gap:@{22};align-items:center}
.stt b{display:block;font-size:@{20};font-weight:500;line-height:1.1}
.stt span{font-size:@{13};color:var(--mute)}
.ml{font-size:@{14};color:var(--mute);display:flex;align-items:center;gap:@{6}}
.ml i{width:@{9};height:@{9};border-radius:50%}
.mv{font-size:@{30};font-weight:500;line-height:1.15}.mv small{font-size:@{14};font-family:'Nunito'!important;color:var(--mute);margin-left:@{3}}
.m svg,.bar{width:100%;height:@{20};display:block;margin-top:@{2}}
.bar{background:#e4efd3;border-radius:@{10};position:relative;height:@{10};margin-top:@{9}}
.bar i{position:absolute;inset:0 auto 0 0;border-radius:@{10}}
.pcard{background:var(--soft);border-radius:@{18};padding:@{12};text-align:center;font-size:@{18};font-weight:600}
.pcard span{font-size:@{34};display:block}.pcard i{display:block;font-style:normal;font-size:@{15};font-weight:400}
</style>
"""


def inject_css():
    uri = bg_uri()
    rules = "".join(
        f".st-key-{k}{{left:@{{{x}}};top:@{{{y}}};width:@{{{w}}};height:@{{{h}}}}}"
        for k, (x, y, w, h) in LAYOUT.items()
    )
    css = CSS.replace("%%BG%%", uri).replace("%%ART%%", art_css()).replace("</style>", rules + "</style>")
    css = re.sub(r"@\{(\d+(?:\.\d+)?)\}", r"calc(var(--u) * \1)", css)
    st.markdown(css, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def art_css() -> str:
    size = {"plant": (68, 65), "can": (84, 90), "pump": (118, 88)}
    out = ""
    for key, fname in ART.items():
        p = ASSETS / fname
        if p.exists():
            w, h = size[key]
            out += (
                f".art-{key}{{width:@{{{w}}};height:@{{{h}}};"
                f"background-image:url(data:image/png;base64,{base64.b64encode(p.read_bytes()).decode()})}}"
            )
    return out


@st.cache_data(show_spinner=False)
def bg_uri() -> str:
    for name in ("garden_bg.png", "background.jpg"):
        p = ASSETS / name
        if p.exists():
            mime = "image/png" if p.suffix == ".png" else "image/jpeg"
            return f'url("data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}")'
    return "linear-gradient(160deg,#e9f7df,#f3fbee 50%,#d8f0c4)"

# ==================================================
# HELPER FUNCTIONS
# ==================================================
def health(p: dict) -> int:
    fit = lambda v, lo, hi, tol: 1 - min(1, max(lo - v, v - hi, 0) / tol)
    return round(100 * (
        .6 * fit(p["moisture"], p["mlo"], p["mhi"], 25)
        + .25 * fit(p["temp"], p["tlo"], p["thi"], 10)
        + .15 * fit(p["hum"], 35, 85, 30)
    ))


def status(score: int):
    if score >= 80:
        return ("Thriving", "var(--good)")
    elif score >= 60:
        return ("Doing okay", "var(--warn)")
    else:
        return ("Needs care", "var(--bad)")


def get_forecast(city: str, days: int = 5) -> list:
    """SAMPLE DATA - swap for a real API call"""
    base, hum, rain = CITIES[city]
    r = random.Random(f"{city}{datetime.now():%Y%m%d}")
    out = []
    for i in range(days):
        pr = int(clamp(rain * 100 + r.uniform(-35, 35), 5, 95))
        hi = base + r.uniform(-2, 2) - (3 if pr > 60 else 0)
        out.append({
            "day": "Today" if i == 0 else (datetime.now() + timedelta(i)).strftime("%a"),
            "hi": hi,
            "lo": hi - r.uniform(4, 7),
            "rain": pr,
            "hum": int(hum + r.uniform(-8, 8)),
            "wind": int(r.uniform(6, 22)),
            "icon": "🌧️" if pr >= 60 else "⛅" if pr >= 30 else "☀️"
        })
    return out


def T(c: float) -> str:
    if st.session_state.unit == "°F":
        return f"{c * 9 / 5 + 32:.0f}°F"
    else:
        return f"{c:.0f}°C"


def html(s: str) -> None:
    st.markdown(s, unsafe_allow_html=True)

# ==================================================
# CALLBACKS
# ==================================================
def go(view: str) -> None:
    st.session_state.view = view
    
    page_map = {
        "Settings": "pages/10_Settings.py",
        "Analytics": "pages/11_Analytics.py",
        "Sensors": "pages/9_Sensors.py",
        "Weather Forecast": "pages/12_Weather.py",
        "About us": "pages/7_About.py",
        "Profile": "pages/8_Profile.py"
    }
    
    if view in page_map:
        st.switch_page(page_map[view])


def open_plant(name: str) -> None:
    st.session_state.sel_plant = name
    st.session_state.view = "Dashboard"


def water_now() -> None:
    st.toast("Watering command sent! 💧")


def logout() -> None:
    st.session_state.auth_token = None
    st.toast("Logged out")
    st.switch_page("pages/2_Login.py")

# ==================================================
# CARD COMPONENTS
# ==================================================
def user_name() -> str:
    return get_current_user(st.session_state.auth_token)


def nav() -> None:
    ss = st.session_state
    with st.container(key="nav"):
        html('<div class="brand"><i>🌱</i>Smart Garden</div>')
        for n, icon in NAV:
            clicked = st.button(
                n,
                key=f"nav_{n}",
                icon=icon,
                type="primary" if ss.view == n else "secondary"
            )
            if clicked:
                go(n)
        with st.container(key="snapwrap"):
            plant_count = len(ss.plants) if ss.plants else 0
            html(f'<div class="snap"><b>{datetime.now():%a, %d %b}</b>{plant_count} plants linked</div>')
        st.toggle("Live updates", key="live")
        if st.button("Log out", key="logout", icon="🚪"):
            logout()


def profile() -> None:
    name = user_name()
    with st.container(key="profile"):
        html(f'<div class="greet">Hi, {name}</div>')
        with st.popover(name[0].upper(), help="Your profile"):
            html(f'<div class="avatar-name">{name}</div>')
            st.caption("Signed in to Smart Garden")
            if st.button("Settings", key="pf_settings", icon="⚙️"):
                go("Settings")
            if st.button("Log out", key="pf_logout", icon="🚪"):
                logout()


def card_health() -> None:
    ss = st.session_state
    if not ss.plants:
        st.error("No plants available")
        return

    with st.container(key="health"):
        html(
            '<div class="hdr"><div><div class="h">Plant health</div>'
            '<div class="sub">Pick a plant to inspect</div></div>'
            '<div class="art art-plant"></div></div>'
        )
        name = st.selectbox(
            "Plant",
            list(ss.plants),
            key="sel_plant",
            label_visibility="collapsed",
            index=0
        )
        if not name:
            name = list(ss.plants.keys())[0]
        p = ss.plants[name]
        s = health(p)
        lab, col = status(s)
        html(
            f'<div class="hrow"><div class="ring" style="--s:{s};--c:{col}"><b>{s}</b>'
            f'<span>{lab}</span></div>'
            f'<div class="stats"><div>Soil<b>{p["moisture"]:.0f}%</b></div>'
            f'<div>Air<b>{T(p["temp"])}</b></div>'
            f'<div>Humidity<b>{p["hum"]:.0f}%</b></div></div></div>'
        )


def card_water() -> None:
    ss = st.session_state

    if not ss.plants or ss.sel_plant not in ss.plants:
        st.error("Plant data not available")
        return

    plant_id = ss.plants[ss.sel_plant].get("id")

    prediction = {}

    if plant_id:
        prediction = load_next_watering_prediction(
            plant_id,
            ss.auth_token
        )

    with st.container(key="water"):

        html(
            '<div class="wtop">'
            '<div>'
            '<div class="h">Next watering</div>'
            '</div>'
            '<div class="art art-can"></div>'
            '</div>'
        )

        if prediction:

            status_value = prediction.get("status")
            hours = prediction.get("next_watering_in_hours")
            friendly_time = prediction.get(
                "estimated_time_friendly"
            )

            if status_value == "WATER_NOW":

                st.error("💧 WATER NOW")

            elif status_value == "WATER_SOON":

                st.warning(
                    f"💧 Water soon — {hours:.1f} hours"
                )

            elif hours is not None:

                if hours > 8:
                    st.success(
                        f"🌱 Next watering in {hours:.1f} hours"
                    )

                elif hours >= 4:
                    st.warning(
                        f"💧 Next watering in {hours:.1f} hours"
                    )

                else:
                    st.error(
                        f"🔴 Watering in {hours:.1f} hours"
                    )

            else:

                st.info("🌱 Plant is stable")

            if friendly_time:
                st.caption(
                    f"Estimated: {friendly_time}"
                )

            col1, col2 = st.columns(2)

            with col1:
                moisture = prediction.get("current_moisture")

                if moisture is not None:
                    st.metric(
                        "Moisture",
                        f"{moisture:.0f}%"
                    )

            with col2:
                rate = prediction.get(
                    "depletion_rate_per_hour"
                )

                if rate is not None:
                    st.metric(
                        "Drying rate",
                        f"{rate:.2f}%/hr"
                    )

            confidence = prediction.get("confidence")

            if confidence is not None:
                st.caption(
                    f"Prediction confidence: {confidence}%"
                )

        else:

            st.info(
                "Waiting for enough sensor data "
                "to predict watering."
            )

        st.divider()

        # Existing manual watering controls
        now = datetime.now()
        nxt = datetime.combine(now.date(), ss.sched)
        nxt = nxt if nxt > now else nxt + timedelta(days=1)

        h, m = divmod(
            int((nxt - now).total_seconds() // 60),
            60
        )

        a, b = st.columns(
            [1.1, 1],
            vertical_alignment="bottom"
        )

        a.time_input(
            "Water daily at",
            key="sched",
            step=300
        )

        b.toggle(
            "Follow schedule",
            key="auto_sched"
        )

        st.button(
            "Water now",
            key="water_now",
            icon="💧",
            on_click=water_now
        )


def card_weather() -> None:
    ss = st.session_state
    with st.container(key="weather"):
        html('<div class="h">Weather forecast</div>')
        a, b = st.columns([3, 2], vertical_alignment="center")
        a.selectbox("City", list(CITIES), key="city", label_visibility="collapsed")
        b.radio("Unit", ["°C", "°F"], key="unit", horizontal=True, label_visibility="collapsed")

        fc = get_forecast(ss.city)
        n = fc[0]
        html(
            f'<div class="wnow"><span>{n["icon"]}</span><b>{T(n["hi"])}</b></div>'
            f'<div class="chips"><div><b>{n["hum"]}%</b>humidity</div>'
            f'<div><b>{n["wind"]} km/h</b>wind</div>'
            f'<div><b>{n["rain"]}%</b>rain</div></div>'
            '<div class="wlist">'
            + "".join(
                f'<div class="wrow"><span>{d["day"]}</span><span>{d["icon"]}</span>'
                f'<span>{T(d["hi"])} / {T(d["lo"])}</span><span>💧 {d["rain"]}%</span></div>'
                for d in fc
            )
            + '</div>'
        )
        wet = next((d["day"] for d in fc[:3] if d["rain"] >= 60), None)
        when = "today" if wet == "Today" else wet
        tip = f"Rain likely {when}: consider skipping watering." if wet else "Dry days ahead: keep your watering schedule."
        html(f'<div class="tip">💡 {tip}</div>')


def card_pump() -> None:
    ss = st.session_state
    with st.container(key="pump"):
        art, a, b, c = st.columns([.75, 1.25, 1.15, 1.5], vertical_alignment="center")
        with art:
            html('<div class="art art-pump"></div>')
        with a:
            html(
                '<div class="h">Pump status</div>'
                f'<div class="pst"><div class="dot"></div><div>'
                f'<b>OFF</b><small>Idle · 0 L used</small></div></div>'
            )
        with b:
            st.radio("Mode", ["Auto", "Manual"], key="mode", horizontal=True, label_visibility="collapsed")
            st.toggle("Pump on / off", key="pump_on", disabled=ss.mode == "Auto")
        with c:
            st.slider(f"Auto-water when soil is below {ss.thr}%", 10, 70, key="thr")


def spark(vals: list, col: str) -> str:
    if len(vals) < 2:
        return '<svg viewBox="0 0 100 28"></svg>'
    lo, r = min(vals), (max(vals) - min(vals)) or 1
    pts = " ".join(
        f"{i * 100 / (len(vals) - 1):.1f},{27 - (v - lo) / r * 25:.1f}"
        for i, v in enumerate(vals)
    )
    return (
        f'<svg viewBox="0 0 100 28" preserveAspectRatio="none">'
        f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2" '
        f'vector-effect="non-scaling-stroke"/></svg>'
    )


def card_sensors() -> None:
    ss = st.session_state
    if not ss.plants or ss.sel_plant not in ss.plants:
        st.error("Plant data not available")
        return

    p = ss.plants[ss.sel_plant]
    hist = lambda k: [h.get(k, 0) for h in p["hist"]]
    rows = [
        ("Soil moisture", f'{p["moisture"]:.0f}', "%", p["mlo"] <= p["moisture"] <= p["mhi"], hist("moisture")),
        ("Temperature", T(p["temp"])[:-2], T(p["temp"])[-2:], p["tlo"] <= p["temp"] <= p["thi"], hist("temperature")),
        ("Humidity", f'{p["hum"]:.0f}', "%", 35 <= p["hum"] <= 85, hist("humidity")),
        ("Light", f'{p["light"] / 1000:.1f}', "klux", p["light"] <= 45000, hist("light")),
        ("Water tank", "100", "%", True, None)
    ]
    cells = ""
    for label, val, unit, ok, series in rows:
        col = "var(--good)" if ok else "var(--warn)"
        extra = spark(series, col) if series else '<div class="bar"><i style="width:100%;background:var(--good)"></i></div>'
        cells += (
            f'<div class="m"><div class="ml">{label}<i style="background:{col}"></i></div>'
            f'<div class="mv">{val}<small>{unit}</small></div>{extra}</div>'
        )
    stamp = f"{p['emoji']} {ss.sel_plant} · {datetime.now():%H:%M:%S}" if ss.live else "Updates paused"
    with st.container(key="sensors"):
        html(f'<div class="sens"><div class="stt"><b>Live sensor readings</b><span>{stamp}</span></div>{cells}</div>')

# ==================================================
# PANEL VIEWS
# ==================================================
def panel(view: str) -> None:
    ss = st.session_state
    with st.container(key="panel"):
        html(f'<div class="h">{view}</div>')
        if view == "My plants":
            if st.button("＋ Add a plant", key="add_plant"):
                st.switch_page("pages/5_Garden.py")

            if ss.plants:
                items = list(ss.plants.items())
                for i in range(0, len(items), 3):
                    for col, (n, p) in zip(st.columns(3), items[i:i + 3]):
                        s = health(p)
                        lab, c = status(s)
                        with col:
                            html(f'<div class="pcard"><span>{p["emoji"]}</span>{n}<i style="color:{c}">{s}% · {lab}</i></div>')
                            st.button(
                                "Open on dashboard",
                                key=f"open_{n}",
                                on_click=open_plant,
                                args=(n,),
                                width="stretch"
                            )
        elif view == "Weather Forecast":
            st.switch_page("pages/12_Weather.py")
            '''a, b = st.columns([3, 1])
            a.selectbox("City", list(CITIES), key="city")
            b.radio("Unit", ["°C", "°F"], key="unit", horizontal=True)
            fc = get_forecast(ss.city, 7)
            f = (lambda c: c * 9 / 5 + 32) if ss.unit == "°F" else (lambda c: c)
            df = pd.DataFrame(
                {"High": [f(d["hi"]) for d in fc], "Low": [f(d["lo"]) for d in fc]},
                index=[d["day"] for d in fc]
            )
            st.line_chart(df)
            st.dataframe(
                pd.DataFrame({
                    "Day": [d["day"] for d in fc],
                    "Rain %": [d["rain"] for d in fc],
                    "Humidity %": [d["hum"] for d in fc],
                    "Wind km/h": [d["wind"] for d in fc]
                }),
                hide_index=True,
                width="stretch"
            )'''
        elif view == "Sensors":
            st.switch_page("pages/9_Sensors.py")
            '''m = st.radio("Reading", ["moisture", "temperature", "humidity", "light"], key="metric", horizontal=True)
            data = {}
            for n, p in ss.plants.items():
                data[n] = pd.Series([h.get(m, 0) for h in p["hist"]])
            if data:
                st.line_chart(pd.DataFrame(data))
                st.dataframe(
                    pd.DataFrame([
                        {
                            "Plant": n,
                            "Soil %": round(p["moisture"]),
                            "Temp °C": round(p["temp"], 1),
                            "Humidity %": round(p["hum"]),
                            "Light lux": round(p["light"])
                        }
                        for n, p in ss.plants.items()
                    ]),
                    hide_index=True,
                    width="stretch" 
                )'''
        elif view == "Analytics":
            st.switch_page("pages/11_Analytics.py")
            '''sc = {n: health(p) for n, p in ss.plants.items()}
            a, b, c = st.columns(3)
            if sc:
                a.metric("Average health", f"{sum(sc.values()) / len(sc):.0f}%")
                b.metric("Water used", f"0.0 L")
                c.metric("Tank level", "100%")
                st.bar_chart(pd.Series(sc, name="Health score"))'''
        elif view == "About us":
            st.switch_page("pages/7_About.py")
            '''st.write(
                "**Smart Garden** listens to your plants, byte by byte. Soil, air and light sensors feed "
                "this dashboard so the pump waters only when your plants need it, and skips it when rain is coming."
            )'''
        else:  # Settings
            st.switch_page("pages/10_Settings.py")
            '''st.radio("Temperature unit", ["°C", "°F"], key="unit", horizontal=True)'''

# ==================================================
# INIT SESSION STATE
# ==================================================
def init_session_state():
    ss = st.session_state
    
    # If the user navigated back from an external page, reset view to Dashboard
    if ss.get("view") in ["Profile", "Settings", "Analytics", "Sensors", "Weather Forecast", "About us"]:
        ss.view = "Dashboard"
        
    ss.setdefault("view", "Dashboard")
    ss.setdefault("sel_plant", None)
    ss.setdefault("mode", "Auto")
    ss.setdefault("thr", 35)
    ss.setdefault("pump_on", False)
    ss.setdefault("sched", time(18, 30))
    ss.setdefault("auto_sched", True)
    ss.setdefault("unit", "°C")
    ss.setdefault("city", "Mumbai")
    ss.setdefault("live", True)
    ss.setdefault("metric", "moisture")
    ss.setdefault("plants", {})

    # Load plants from backend if empty
    if not ss.plants:
        ss.plants = load_plants_from_backend(ss.auth_token)
        if ss.plants and not ss.sel_plant:
            ss.sel_plant = list(ss.plants.keys())[0]

# ==================================================
# MAIN DASHBOARD
# ==================================================
def dashboard_body() -> None:
    ss = st.session_state

    # Load sensor history for current plant
    if ss.sel_plant and ss.sel_plant in ss.plants:
        plant_id = ss.plants[ss.sel_plant].get("id")
        if plant_id:
            readings = load_sensor_history(plant_id, ss.auth_token, limit=60)

            if readings:
                # Update current values
                latest = readings[-1]
                ss.plants[ss.sel_plant]["moisture"] = latest.get("moisture", 0)
                ss.plants[ss.sel_plant]["temp"] = latest.get("temperature", 0)
                ss.plants[ss.sel_plant]["hum"] = latest.get("humidity", 0)
                ss.plants[ss.sel_plant]["light"] = latest.get("light", 0)

                # Update history
                ss.plants[ss.sel_plant]["hist"] = readings

    if ss.view == "Dashboard":
        card_health()
        card_water()
        card_weather()
        card_pump()
        card_sensors()
    else:
        panel(ss.view)

# ==================================================
# RUN PAGE
# ==================================================
init_session_state()
inject_css()
profile()
with st.container(key="stage"):
    nav()
    dashboard_body()