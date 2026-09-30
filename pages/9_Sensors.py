"""
AquaSmart Sensors — Streamlit page
Shows Sensor ID, type, reading and status for every plant, plus overall
sensor health. Same visual system as the Analytics page: watercolor
background, white cards with a green border, all rendered as self-contained
HTML via st.components.v1.html so styling is consistent across Streamlit
versions.

Run with:
    pip install -r requirements.txt
    streamlit run sensors.py

Keep background.png next to this file (or in an assets/static/images folder).
"""

import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Sensors", page_icon="🌿", layout="wide")

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
if BG_PATH is None:
    st.warning(
        "background.png not found — place it next to sensors.py, or in an "
        "assets/, static/, or images/ subfolder."
    )

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
# Header
# ---------------------------------------------------------------------------
if st.button("← Back to Dashboard"):
    st.switch_page("pages/6_Dashboard.py")

st.markdown("<h1 class='app-title'>🌿Sensors</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='app-sub'>Hardware tuned to nature's frequency</p>",
    unsafe_allow_html=True,
)
st.write("")

# ---------------------------------------------------------------------------
# Shared card shell
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
  .badge.good  { background: #e3f6ea; color: #2e7d54; }
  .badge.low   { background: #fdf1de; color: #b9781f; }
  .badge.crit  { background: #fbe7e6; color: #c0433f; }
</style>
"""

PLOTLY_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"

BADGE_CLASS = {"Good": "good", "Low": "low", "Critical": "crit"}


def render_overview_card(stats: list, height: int = 190) -> None:
    stat_html = "".join(
        f"<div class='stat'><label>{label}</label><div class='val'>{value}</div></div>"
        for label, value in stats
    )
    html = f"""
    <html><head>{CARD_CSS}</head>
    <body>
      <div class="card">
        <div class="title"><span class="dot"></span>Sensor Overview</div>
        <div class="stat-row">{stat_html}</div>
      </div>
    </body></html>
    """
    components.html(html, height=height)


def render_table_card(title: str, headers: list, rows: list, height: int = 420) -> None:
    head_html = "".join(f"<th>{h}</th>" for h in headers)
    body_html = ""
    for row in rows:
        cells = "".join(
            f"<td><span class='badge {BADGE_CLASS.get(cell, 'good')}'>{cell}</span></td>"
            if i == len(row) - 1 else f"<td>{cell}</td>"
            for i, cell in enumerate(row)
        )
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
# Data (swap in live values from your device/DB layer)
# ---------------------------------------------------------------------------
SENSORS = [
    # Plant, Sensor ID, Type, Reading, Status
    ["Monstera",         "SNS-001", "Soil Moisture", "42%",      "Good"],
    ["Monstera",         "SNS-002", "Light",         "850 lux",  "Good"],
    ["Fiddle Leaf Fig",  "SNS-003", "Soil Moisture", "18%",      "Low"],
    ["Fiddle Leaf Fig",  "SNS-004", "Temperature",   "24°C",     "Good"],
    ["Snake Plant",      "SNS-005", "Soil Moisture", "65%",      "Good"],
    ["Snake Plant",      "SNS-006", "Humidity",      "38%",      "Good"],
    ["Peace Lily",       "SNS-007", "Soil Moisture", "12%",      "Critical"],
    ["Peace Lily",       "SNS-008", "Light",         "210 lux",  "Low"],
]

CALIBRATION = [
    ["SNS-001", "94% battery", "3 days ago", "Good"],
    ["SNS-002", "88% battery", "3 days ago", "Good"],
    ["SNS-003", "61% battery", "9 days ago", "Low"],
    ["SNS-004", "97% battery", "1 day ago",  "Good"],
    ["SNS-005", "72% battery", "5 days ago", "Good"],
    ["SNS-006", "80% battery", "5 days ago", "Good"],
    ["SNS-007", "23% battery", "21 days ago", "Critical"],
    ["SNS-008", "55% battery", "12 days ago", "Low"],
]

total = len(SENSORS)
good = sum(1 for s in SENSORS if s[-1] == "Good")
low = sum(1 for s in SENSORS if s[-1] == "Low")
crit = sum(1 for s in SENSORS if s[-1] == "Critical")

# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
render_overview_card([
    ("Total Sensors", str(total)),
    ("Healthy", str(good)),
    ("Needs Attention", str(low)),
    ("Critical", str(crit)),
])

st.write("")

# ---------------------------------------------------------------------------
# Per-plant sensor table (full width)
# ---------------------------------------------------------------------------
render_table_card(
    "Sensor Readings by Plant",
    ["Plant", "Sensor ID", "Type", "Reading", "Status"],
    SENSORS,
    height=420,
)

st.write("")

# ---------------------------------------------------------------------------
# Sensor health: distribution + calibration/battery detail
# ---------------------------------------------------------------------------
health_left, health_right = st.columns([1, 1.4])

with health_left:
    render_chart_card(
        "Sensor Health",
        [
            {
                "type": "pie",
                "labels": ["Good", "Low", "Critical"],
                "values": [good, low, crit],
                "hole": 0.6,
                "marker": {"colors": ["#2e7d54", "#e0a530", "#c0433f"]},
            }
        ],
        {"legend": {"orientation": "h", "y": -0.15, "x": 0.5, "xanchor": "center"}},
        height=340,
    )

with health_right:
    render_table_card(
        "Battery & Calibration",
        ["Sensor ID", "Battery", "Last Calibrated", "Status"],
        CALIBRATION,
        height=340,
    )