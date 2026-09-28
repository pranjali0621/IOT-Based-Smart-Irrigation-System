import base64, math
from datetime import datetime
from pathlib import Path
import streamlit as st

try:
    st.set_page_config(page_title="Smart Irrigation System – Weather Forecast", page_icon="🌦️", layout="wide")
except st.errors.StreamlitAPIException:
    pass  # already set by app.py

BASE = Path(__file__).parent


# ---------- background (same image as the other pages) ----------
def find_background():
    for folder in (BASE / "assets", BASE.parent / "assets", BASE, BASE.parent):
        for name in ("background.png", "background.jpg", "background.jpeg"):
            if (folder / name).exists():
                return folder / name
    return None

@st.cache_data
def encode(path: str, mtime: float) -> str:
    f = Path(path)
    mime = "png" if f.suffix.lower() == ".png" else "jpeg"
    return f"data:image/{mime};base64," + base64.b64encode(f.read_bytes()).decode()

bg_file = find_background()
BG = f"url({encode(str(bg_file), bg_file.stat().st_mtime)}) center/cover fixed," if bg_file else ""

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');
:root{--ink:#1f3a17;--mute:#5d7455;--g:#5a8a2c;--g2:#7fb03a;--line:#6f9a3d;--field:#fff;--trk:#d3dfc9;--chip:#dff0bd;--sun:#e0a020}
html,body,.stApp,.stApp div,.stApp p,.stApp label,.stApp input,.stApp button{font-family:'Outfit',system-ui,sans-serif}
[data-testid="stIconMaterial"],[data-testid="stIconMaterial"] *{font-family:"Material Symbols Rounded","Material Symbols Outlined","Material Icons"!important}
.stApp{background:__BG__#eef8ea;color:var(--ink)}
header[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}
.block-container{max-width:1100px;padding:1.8rem 1.2rem 3rem}
.t{font-size:clamp(1.7rem,4vw,2.6rem);font-weight:700;letter-spacing:-.02em;line-height:1.2;color:var(--ink)}
.mute{color:var(--mute)}
[data-testid="stSelectbox"]>:last-child{background:#fff!important;border:2px solid var(--line)!important;border-radius:20px!important;overflow:hidden;box-shadow:none!important}
[data-testid="stSelectbox"]>:last-child *{background:transparent!important;border-color:transparent!important;box-shadow:none!important}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:20px;align-items:stretch;margin-top:8px}
.card{background:rgba(255,255,255,.72);backdrop-filter:blur(6px);border:2px solid var(--line);border-radius:26px;padding:22px 24px;box-shadow:0 6px 18px rgba(60,90,30,.12);color:var(--ink)}
.c7{grid-column:span 7}.c5{grid-column:span 5}.c8{grid-column:span 8}.c4{grid-column:span 4}.c12{grid-column:span 12}
.h2{display:flex;align-items:center;gap:12px;font-size:1.3rem;margin:0 0 16px;font-weight:600}
.h2 svg{width:28px;height:28px;stroke:var(--g);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}
.wi{stroke:var(--g);fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}
.now{display:flex;align-items:center;gap:22px;flex-wrap:wrap}
.now .big{font-size:clamp(4rem,10vw,6rem);font-weight:700;line-height:1;letter-spacing:-.04em}
.now .cond{font-size:1.4rem;font-weight:600}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:20px}
.tile{background:var(--field);border:2px solid var(--line);border-radius:18px;padding:10px 12px}
.tile span{display:block;color:var(--mute);font-size:.85rem}.tile b{font-size:1.2rem;font-weight:600}
.adv{display:flex;flex-direction:column;gap:14px}
.verdict{background:var(--chip);border:2px solid var(--line);border-radius:20px;padding:14px 16px;font-size:1.15rem;font-weight:600}
.verdict small{display:block;font-weight:400;color:var(--mute);font-size:.92rem;margin-top:4px}
.kv{display:flex;justify-content:space-between;padding:10px 0;border-bottom:2px dotted var(--line)}.kv:last-child{border:0}
.hours{display:flex;gap:12px;overflow-x:auto;padding-bottom:8px}
.h{flex:0 0 84px;text-align:center;background:var(--field);border:2px solid var(--line);border-radius:22px;padding:12px 6px;display:flex;flex-direction:column;align-items:center;gap:6px}
.h.first{background:linear-gradient(#c9e68a,var(--g2))}
.h b{font-size:1.15rem;font-weight:600}.h span{font-size:.85rem;color:var(--mute)}.h.first span{color:var(--ink)}
.day{display:grid;grid-template-columns:70px 32px 46px 38px 1fr 38px;align-items:center;gap:10px;padding:10px 0;border-bottom:2px dotted var(--line)}.day:last-child{border:0}
.day .d{font-weight:600}.day .r{color:var(--mute);font-size:.9rem}.day .tt{text-align:right;font-weight:500}
.bar{height:8px;border-radius:8px;background:var(--trk);position:relative}.bar i{position:absolute;top:0;bottom:0;border-radius:8px;background:linear-gradient(90deg,var(--g2),var(--sun))}
.det{display:grid;grid-template-columns:1fr 1fr;gap:10px}.full{grid-column:1/-1}
.tile.ring{display:flex;align-items:center;gap:8px;padding:8px}.tile.ring span{font-size:.8rem}.tile.ring b{font-size:1rem}
.uv{height:10px;border-radius:10px;background:linear-gradient(90deg,#5fbf4a,#e6d23a,#f0a030,#e05a3a,#9a4bd0);position:relative;margin:12px 0 4px}
.uv i{position:absolute;top:-5px;width:6px;height:20px;background:var(--ink);border:2px solid var(--field);border-radius:4px;transform:translateX(-50%)}
.mini{height:6px;border-radius:6px;background:var(--trk);margin-top:8px}.mini i{display:block;height:100%;border-radius:6px;background:var(--g2)}
.note{color:var(--mute);font-size:.85rem;text-align:center;margin-top:22px}
@media(max-width:820px){.c7,.c5,.c8,.c4{grid-column:span 12}.tiles{grid-template-columns:1fr 1fr}.day{grid-template-columns:56px 28px 40px 34px 1fr 34px;gap:6px}}
</style>""".replace("__BG__", BG)
st.markdown(CSS, unsafe_allow_html=True)

# ---------- data ----------
ICONS = {
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/>',
 "cloud": '<path d="M7 18h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 11a3.5 3.5 0 0 0 1 7z"/>',
 "rain": '<path d="M7 15h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 8a3.5 3.5 0 0 0 1 7z"/><path d="M8 18l-1 3M12 18l-1 3M16 18l-1 3"/>',
 "part": '<circle cx="8" cy="8" r="3"/><path d="M8 2v1M2 8h1M3.8 3.8l.7.7M12.2 3.8l-.7.7"/><path d="M9 20h8a3.5 3.5 0 0 0 .4-7A5 5 0 0 0 8 14a3 3 0 0 0 1 6z"/>',
 "storm": '<path d="M7 14h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 7a3.5 3.5 0 0 0 1 7z"/><path d="M12 14l-2 4h3l-2 4"/>'}
NAME = {"sun": "Sunny", "part": "Partly cloudy", "cloud": "Cloudy", "rain": "Rain showers", "storm": "Thunderstorms"}
PCT = {"sun": 5, "part": 15, "cloud": 30, "rain": 75, "storm": 85}
CITIES = {"Mumbai": dict(t=30, h=78, w=14, d=["rain", "rain", "storm", "part", "rain", "cloud", "part"]),
          "Pune": dict(t=27, h=60, w=10, d=["part", "sun", "sun", "cloud", "rain", "part", "sun"]),
          "Delhi": dict(t=33, h=45, w=12, d=["sun", "sun", "part", "sun", "cloud", "part", "sun"]),
          "Bengaluru": dict(t=26, h=65, w=11, d=["cloud", "rain", "part", "rain", "cloud", "part", "sun"])}
DN = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
HEAD = {"cur": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/>',
        "adv": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
        "hrs": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "days": '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>',
        "det": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>'}

def rnd(x): return int(math.floor(x + 0.5))
def ic(k, s=30): return f'<svg class="wi" width="{s}" height="{s}" viewBox="0 0 24 24">{ICONS[k]}</svg>'
def head(k, text): return f'<div class="h2"><svg viewBox="0 0 24 24">{HEAD[k]}</svg>{text}</div>'
def tile(a, b): return f'<div class="tile"><span>{a}</span><b>{b}</b></div>'
def kv(a, b): return f'<div class="kv"><span class="mute">{a}</span><b>{b}</b></div>'
def hr(h): return f"{h % 12 or 12}" + (" AM" if h % 24 < 12 else " PM")
def temp_at(c, h): return c["t"] - 3 + 6 * math.sin((h - 9) / 24 * 2 * math.pi)

# ---------- header + controls ----------
now = datetime.now()
H0 = now.hour
left, mid, right = st.columns([5, 2, 1.3], vertical_alignment="center", gap="medium")
left.markdown(f'<div class="t">Weather Forecast</div><div class="mute">{now:%A}, {now.day} {now:%B}</div>', unsafe_allow_html=True)
city = mid.selectbox("City", list(CITIES), key="city", label_visibility="collapsed")
try:
    unit = right.segmented_control("Unit", ["°C", "°F"], default="°C", key="unit", label_visibility="collapsed") or "°C"
except AttributeError:  # older Streamlit
    unit = right.radio("Unit", ["°C", "°F"], horizontal=True, key="unit", label_visibility="collapsed")
UNIT_C = unit == "°C"
def T(c): return f"{rnd(c if UNIT_C else c * 9 / 5 + 32)}°"

# ---------- calculations ----------
c = CITIES[city]
k0 = c["d"][0]
cur = temp_at(c, H0)
hrs = []
for i in range(12):
    h = (H0 + i) % 24
    p = max(2, min(95, PCT[k0] + rnd(20 * math.sin(i / 2))))
    k = "rain" if p >= 60 else "cloud" if p >= 30 else "part" if p >= 12 else "sun"
    hrs.append(dict(h=h, p=p, t=temp_at(c, h), k=k, mm=round(p / 100 * 3, 1) if p >= 60 else 0))
rain6 = round(sum(x["mm"] for x in hrs[:6]), 1)
hot = max(x["t"] for x in hrs) >= 32
if rain6 >= 5:
    verdict, why = "Pause watering", "Enough rain is expected in the next 6 hours."
elif rain6 >= 2:
    verdict, why = "Shorten the cycle", "Light rain is on the way, so the soil will get some water."
elif hot:
    verdict, why = "Water at dawn or dusk", "High heat today. Avoid midday watering."
else:
    verdict, why = "Follow the normal schedule", "No significant rain is expected soon."

offs = [0, -1, -2, 1, -2, 0, 1]
days = []
for i, k in enumerate(c["d"]):
    hi = c["t"] + offs[i] + (2 if k == "sun" else -2 if k in ("rain", "storm") else 0)
    days.append(dict(k=k, hi=hi, lo=hi - 6 - (2 if k == "sun" else 0), p=PCT[k] + (i * 7) % 10))
mn, mx = min(d["lo"] for d in days), max(d["hi"] for d in days)

# ---------- cards ----------
cur_card = (f'<div class="card c7">{head("cur", "Current Conditions")}<div class="now"><div>{ic(k0, 84)}</div>'
            f'<div class="big">{T(cur)}</div><div><div class="cond">{NAME[k0]}</div>'
            f'<div class="mute">Feels like {T(cur + (3 if c["h"] > 60 else 0))}</div></div></div>'
            f'<div class="tiles">{tile("Humidity", str(c["h"]) + "%")}{tile("Wind", str(c["w"]) + " km/h")}{tile("Rain chance", str(PCT[k0]) + "%")}</div></div>')

adv_card = (f'<div class="card c5">{head("adv", "Irrigation Advice")}<div class="adv"><div class="verdict">{verdict}<small>{why}</small></div><div>'
            f'{kv("Rain in next 6 hours", f"{rain6} mm")}{kv("Rain threshold", "5 mm")}{kv("Forecast buffer", "6 hours")}{kv("Soil moisture now", "42%")}</div></div></div>')

hour_cells = "".join(
    f'<div class="h{"" if i else " first"}"><span>{hr(x["h"]) if i else "Now"}</span>{ic(x["k"], 32)}<b>{T(x["t"])}</b><span>{x["p"]}%</span></div>'
    for i, x in enumerate(hrs))
hours_card = f'<div class="card c12">{head("hrs", "Next 12 Hours")}<div class="hours">{hour_cells}</div></div>'

day_rows = "".join(
    f'<div class="day"><span class="d">{"Today" if i == 0 else DN[(now.weekday() + 1 + i) % 7]}</span>{ic(d["k"], 28)}<span class="r">{d["p"]}%</span>'
    f'<span class="tt mute">{T(d["lo"])}</span><div class="bar"><i style="left:{(d["lo"] - mn) / (mx - mn) * 100:.1f}%;right:{100 - (d["hi"] - mn) / (mx - mn) * 100:.1f}%"></i></div>'
    f'<span class="tt">{T(d["hi"])}</span></div>' for i, d in enumerate(days))
days_card = f'<div class="card c8">{head("days", "7-Day Forecast")}<div>{day_rows}</div></div>'

# details: sun arc, UV meter, humidity ring, visibility bar
RISE, SET = 6.53, 18.68
now_h = H0 + now.minute / 60
f = max(0, min(1, (now_h - RISE) / (SET - RISE)))
daytime = RISE <= now_h <= SET
sx, sy = 120 - 100 * math.cos(math.pi * f), 95 - 90 * math.sin(math.pi * f)
rays = "".join(f'<line x1="{sx + 11 * math.cos(math.radians(a)):.1f}" y1="{sy + 11 * math.sin(math.radians(a)):.1f}" '
               f'x2="{sx + 16 * math.cos(math.radians(a)):.1f}" y2="{sy + 16 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 45)) if daytime else ""
uv = {"sun": 8, "part": 6, "cloud": 3}.get(k0, 2)
uv_name = "Low" if uv < 3 else "Moderate" if uv < 6 else "High" if uv < 8 else "Very high" if uv < 11 else "Extreme"
vis = 6 if c["h"] > 70 else 10
dew = cur - (100 - c["h"]) / 5
ring = 163.4 * c["h"] / 100
hum_word = "Humid" if c["h"] > 70 else "Comfortable" if c["h"] > 50 else "Dry"
sun_x, sun_y = (sx, sy) if daytime else ((20 if now_h < RISE else 220), 95)
sun_svg = (f'<svg viewBox="0 0 240 118" width="100%" role="img" aria-label="Sun position">'
           f'<path d="M20 95A100 90 0 0 1 220 95" fill="none" stroke="#6f9a3d" stroke-width="2" stroke-dasharray="4 6"/>'
           f'<line x1="8" y1="95" x2="232" y2="95" stroke="#6f9a3d" stroke-width="2"/>'
           f'<g stroke="#e0a020" stroke-width="2" stroke-linecap="round">{rays}</g>'
           f'<circle cx="{sun_x:.1f}" cy="{sun_y:.1f}" r="8" fill="{"#e0a020" if daytime else "#d3dfc9"}" stroke="#6f9a3d" stroke-width="2"/>'
           f'<text x="20" y="113" font-size="11" fill="#5d7455" text-anchor="middle">6:32 AM</text>'
           f'<text x="220" y="113" font-size="11" fill="#5d7455" text-anchor="middle">6:41 PM</text>'
           f'<text x="120" y="80" font-size="12" fill="#5d7455" text-anchor="middle">Sunrise · Sunset</text></svg>')
ring_svg = (f'<svg width="62" height="62" viewBox="0 0 62 62"><circle cx="31" cy="31" r="26" fill="none" stroke="#d3dfc9" stroke-width="7"/>'
            f'<circle cx="31" cy="31" r="26" fill="none" stroke="#7fb03a" stroke-width="7" stroke-linecap="round" stroke-dasharray="{ring:.1f} 163.4" transform="rotate(-90 31 31)"/>'
            f'<text x="31" y="35" font-size="13" font-weight="600" fill="#1f3a17" text-anchor="middle">{c["h"]}%</text></svg>')
det_card = (f'<div class="card c4">{head("det", "Details")}<div class="det"><div class="full">{sun_svg}</div>'
            f'<div class="full tile"><span>UV index</span><b>{uv} · {uv_name}</b><div class="uv"><i style="left:{min(uv, 11) / 11 * 100:.1f}%"></i></div></div>'
            f'<div class="tile ring">{ring_svg}<div><span>Humidity</span><b>{hum_word}</b></div></div>'
            f'<div class="tile"><span>Visibility</span><b>{vis} km</b><div class="mini"><i style="width:{vis * 10}%"></i></div></div>'
            f'{tile("Pressure", "1008 hPa")}{tile("Dew point", T(dew))}</div></div>')

# one HTML block (no indentation or blank lines, so Markdown does not treat it as code)
st.markdown(f'<div class="grid">{cur_card}{adv_card}{hours_card}{days_card}{det_card}</div>'
            '<div class="note">Sample forecast data for design preview. Connect a weather service to show live values.</div>',
            unsafe_allow_html=True)