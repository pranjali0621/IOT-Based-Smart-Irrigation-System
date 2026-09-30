import base64, json, time
from pathlib import Path
import streamlit as st

try:
    st.set_page_config(page_title="Smart Irrigation System – Settings", page_icon="💧", layout="wide")
except st.errors.StreamlitAPIException:
    pass  # already set by app.py
s = st.session_state
BASE = Path(__file__).parent
SAVE_FILE = BASE / "settings.json"
BATT = 85
UNITS = ["Celsius (°C)", "Fahrenheit (°F)"]
LANGS = ["English", "Español", "Français", "Deutsch", "हिन्दी"]
ZONES = ["UTC", "Asia/Kolkata (IST)", "Europe/London", "America/New_York", "America/Los_Angeles", "Australia/Sydney"]
DEFAULTS = dict(min_m=30, max_m=75, rain=5, buf=6, man=10, dname="Garden Zone Controller",
                unit=UNITS[0], lang=LANGS[0], tz=ZONES[0])
HW = [("Zone 1 pump", "Last calibrated 12 days ago"),
      ("Sensor A (moisture)", "Last calibrated 3 days ago"),
      ("Sensor B (temperature)", "Last calibrated 3 days ago")]

# ---------- state ----------
if "settings_init" not in s:
    saved = {}
    try:
        saved = json.loads(SAVE_FILE.read_text())
    except Exception:
        pass
    s.update({**DEFAULTS, **saved})
    s.wifi = ("ok", "Connected to GreenHouse_5G")
    s.cal = [h[1] for h in HW]
    s.manual_end = None
    s.settings_init = True

# ---------- styling ----------
@st.cache_data
def load_bg():
    for name in ("background.png", "background.jpg", "background.jpeg"):
        f = BASE / "assets" / name
        if f.exists():
            mime = "png" if f.suffix == ".png" else "jpeg"
            return f"url(data:image/{mime};base64," + base64.b64encode(f.read_bytes()).decode() + ") center/cover fixed,"
    return ""
bg = load_bg()
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');
:root{{--ink:#1f3a17;--mute:#5d7455;--g:#5a8a2c;--g2:#7fb03a;--line:#6f9a3d}}
html,body,.stApp,[class*="st-"],button,input{{font-family:'Outfit',system-ui,sans-serif}}
.stApp{{background:{bg}#eef8ea;color:var(--ink)}}
header[data-testid="stHeader"]{{background:transparent}}
#MainMenu,footer{{visibility:hidden}}
.block-container{{max-width:1100px;padding:1.6rem 1.2rem 3rem}}
.top{{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:.6rem}}
.top h1{{font-size:clamp(1.7rem,4vw,2.6rem);font-weight:700;letter-spacing:-.02em;margin:0;padding:0;color:var(--ink)}}
.user{{display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.72);border:2px solid var(--line);border-radius:40px;padding:6px 16px 6px 6px;font-weight:500}}
.av{{width:38px;height:38px;border-radius:50%;background:var(--g2);display:grid;place-items:center}}
[class*="st-key-card_"]{{background:rgba(255,255,255,.72);backdrop-filter:blur(6px);border:2px solid var(--line);border-radius:26px;padding:22px 24px;box-shadow:0 6px 18px rgba(60,90,30,.12)}}
.h2{{display:flex;align-items:center;gap:12px;font-size:1.3rem;font-weight:600;margin-bottom:.3rem}}
.h2 svg{{width:28px;height:28px;stroke:var(--g);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}
.lbl{{font-weight:500;color:var(--mute)}}
.ro{{display:flex;align-items:center;background:#fff;border:2px solid var(--line);border-radius:20px;padding:8px 14px;min-height:44px}}
.dot{{width:12px;height:12px;border-radius:50%;display:inline-block;flex:none;margin-left:auto}}
.ok{{background:#2fc23a;box-shadow:0 0 8px #2fc23a}}.busy{{background:#e0a020;box-shadow:0 0 8px #e0a020}}.low{{background:#d9382c;box-shadow:0 0 8px #d9382c}}
.status{{display:flex;align-items:center;gap:8px;color:var(--mute);font-size:.92rem}}.status .dot{{margin:0}}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div{{background:#fff!important;border:2px solid var(--line)!important;border-radius:20px!important;overflow:hidden}}
[data-testid="stWidgetLabel"] p{{font-weight:500;color:var(--mute)}}
.stButton>button{{font-weight:600;color:var(--ink);background:#fff;border:2px solid var(--line);border-radius:22px;padding:.4rem 1.1rem;transition:transform .1s}}
.stButton>button[kind="primary"]{{background:linear-gradient(#c9e68a,#7fb03a)}}
.stButton>button:hover{{border-color:var(--g);color:var(--ink)}}.stButton>button:active{{transform:scale(.96)}}
[class*="st-key-hw_"]{{background:#fff;border:2px solid var(--line);border-radius:22px;padding:8px 16px}}
.hwn{{font-weight:500}}.hwn small{{display:block;color:var(--mute);font-weight:400}}
.st-key-mode_box{{border-top:2px dashed var(--line);padding-top:14px;margin-top:6px}}
@media(max-width:820px){{.top{{flex-direction:column;align-items:flex-start}}}}
</style>""", unsafe_allow_html=True)

ICONS = {
 "net": '<path d="M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0"/><circle cx="12" cy="19.5" r="1"/><path d="M2 9a15 15 0 0 1 20 0"/>',
 "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
 "auto": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
 "hw": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
 "geo": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>'}

def heading(icon, text):
    st.markdown(f'<div class="h2"><svg viewBox="0 0 24 24">{ICONS[icon]}</svg>{text}</div>', unsafe_allow_html=True)

def row(label, ratio=(1, 1.6)):
    c1, c2 = st.columns(ratio, vertical_alignment="center")
    c1.markdown(f'<span class="lbl">{label}</span>', unsafe_allow_html=True)
    return c2

# ---------- callbacks ----------
def on_min():
    if s.min_m >= s.max_m - 5:
        s.max_m = min(90, s.min_m + 5)

def on_max():
    if s.max_m <= s.min_m + 5:
        s.max_m = s.min_m + 5

def connect():
    if not s.ssid.strip():
        st.toast("Enter a network name first", icon="⚠️"); return
    if len(s.pw) < 8:
        st.toast("Password must be at least 8 characters", icon="⚠️"); return
    st.toast(f"Connecting to {s.ssid}…")
    time.sleep(1.4)
    s.wifi = ("ok", f"Connected to {s.ssid}")
    st.toast("Network updated", icon="✅")

def toggle_manual():
    if s.manual_end:
        s.manual_end = None; st.toast("Manual watering stopped")
    else:
        s.manual_end = time.time() + max(1, min(120, int(s.man))) * 60
        st.toast("Manual watering started")

def calibrate(i):
    st.toast(f"Calibrating {HW[i][0]}…")
    time.sleep(1.6)
    s.cal[i] = "Last calibrated just now"
    st.toast(f"{HW[i][0]} calibrated", icon="✅")

def save():
    if s.min_m >= s.max_m:
        st.toast("Minimum must be below maximum", icon="⚠️"); return
    if not s.dname.strip():
        st.toast("Enter a device name", icon="⚠️"); return
    try:
        SAVE_FILE.write_text(json.dumps({k: s[k] for k in DEFAULTS}))
    except Exception:
        pass
    st.toast("Settings saved", icon="✅")

def reset():
    s.update(DEFAULTS)
    st.toast("Defaults restored – save to keep them")

# ---------- header ----------
if st.button("← Back to Dashboard"):
    st.switch_page("pages/6_Dashboard.py")
    
st.markdown("""<div class="top"><h1> Settings</h1>
<div class="user"><div class="av"><svg width="22" height="22" viewBox="0 0 24 24" fill="#fff"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7z"/></svg></div>Alice Green</div></div>""", unsafe_allow_html=True)

# ---------- network + device ----------
left, right = st.columns([7, 5], gap="medium")
with left:
    with st.container(key="card_net"):
        heading("net", "System &amp; Network")
        with row("Network name (SSID)"):
            st.text_input("SSID", key="ssid", placeholder="SSID", label_visibility="collapsed")
        with row("Password"):
            st.text_input("Password", key="pw", type="password", placeholder="Password", label_visibility="collapsed")
        c1, c2 = st.columns([3, 2], vertical_alignment="center")
        state, msg = s.wifi
        c1.markdown(f'<div class="status"><i class="dot {state}"></i>{msg}</div>', unsafe_allow_html=True)
        c2.button("Connect / Update", type="primary", on_click=connect, use_container_width=True)
with right:
    with st.container(key="card_dev"):
        heading("info", "Device Information")
        with row("Device name"):
            st.text_input("Device name", key="dname", label_visibility="collapsed", max_chars=32)
        with row("Device ID"):
            st.markdown('<div class="ro">SIS-ALPHA-001</div>', unsafe_allow_html=True)
        with row("Firmware version"):
            st.markdown('<div class="ro">2.1.0</div>', unsafe_allow_html=True)
        with row("Battery level"):
            cls = "ok" if BATT >= 50 else "busy" if BATT >= 20 else "low"
            st.markdown(f'<div class="ro">{BATT}%<i class="dot {cls}"></i></div>', unsafe_allow_html=True)

# ---------- thresholds ----------
with st.container(key="card_auto"):
    heading("auto", "Thresholds &amp; Automation")
    a, b = st.columns([1.5, 1], gap="large")
    with a:
        st.slider("Minimum soil moisture (start watering)", 10, 50, key="min_m", on_change=on_min, format="%d%%")
        st.slider("Maximum soil moisture (stop watering)", 50, 90, key="max_m", on_change=on_max, format="%d%%")
    with b:
        with row("Rain threshold (mm)", (1.4, 1)):
            st.number_input("Rain", 0, 50, key="rain", label_visibility="collapsed")
        with row("Forecast buffer (hours)", (1.4, 1)):
            st.number_input("Buffer", 0, 48, key="buf", label_visibility="collapsed")
        with st.container(key="mode_box"):
            with row("Manual override (min)", (1.4, 1)):
                st.number_input("Manual", 1, 120, key="man", label_visibility="collapsed")
            st.button("Stop watering" if s.manual_end else "Start manual watering", type="primary", on_click=toggle_manual)

            @st.fragment(run_every="1s" if s.manual_end else None)
            def countdown():
                if s.manual_end:
                    left_s = int(s.manual_end - time.time())
                    if left_s <= 0:
                        s.manual_end = None
                        st.toast("Manual watering finished")
                        st.rerun()
                    st.caption(f"Watering – {left_s // 60}:{left_s % 60:02d} left")
            countdown()

# ---------- hardware ----------
with st.container(key="card_hw"):
    heading("hw", "Sensors &amp; Hardware")
    for i, (name, _) in enumerate(HW):
        with st.container(key=f"hw_{i}"):
            c1, c2, c3 = st.columns([6, 2, 0.5], vertical_alignment="center")
            c1.markdown(f'<div class="hwn">{name}<small>{s.cal[i]}</small></div>', unsafe_allow_html=True)
            c2.button("Calibrate", key=f"cal_{i}", type="primary", on_click=calibrate, args=(i,), use_container_width=True)
            c3.markdown('<i class="dot ok"></i>', unsafe_allow_html=True)

# ---------- units ----------
with st.container(key="card_units"):
    heading("geo", "Units &amp; Local")
    u1, u2, u3 = st.columns(3, gap="large")
    u1.selectbox("Temperature unit", UNITS, key="unit")
    u2.selectbox("Language", LANGS, key="lang")
    u3.selectbox("Time zone", ZONES, key="tz")

# ---------- actions ----------
_, r1, r2 = st.columns([6, 1.6, 1.6])
r1.button("Reset to defaults", on_click=reset, use_container_width=True)
r2.button("Save changes", type="primary", on_click=save, use_container_width=True)