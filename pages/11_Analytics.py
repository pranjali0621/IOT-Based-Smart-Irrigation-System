"""
AquaSmart Analytics — Streamlit version
Recreates the standalone analytics page (no sidebar): background image,
Analytics Overview stats, Predictive Soil Moisture Trend, Weather Analysis,
Water vs. Energy Efficiency, and Cost Analysis.

Cards are rendered as self-contained HTML (own CSS + own copy of Plotly)
via st.components.v1.html, so the white background / green border always
look the same regardless of which Streamlit version renders the page.

Run with:
    pip install -r requirements.txt
    streamlit run app.py

Keep background.png next to this file (or in an assets/static/images folder).
"""

import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Analytics", page_icon="🌿", layout="wide")

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
        "background.png not found — place it next to app.py, or in an "
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
st.markdown("<h1 class='app-title'>🌿Analytics</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='app-sub'>Sense. Analyze. Irrigate.</p>",
    unsafe_allow_html=True,
)
st.write("")

# ---------------------------------------------------------------------------
# Card shell — every card is one fully self-contained HTML document.
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
    padding: 18px 20px;
    height: calc(100vh - 6px);
    overflow: hidden;
  }
  .title {
    display: flex; align-items: center; gap: 8px;
    font-weight: 600; font-size: 15px; color: #1f4d3a; margin-bottom: 10px;
  }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: #5fa93a; }
  .stat-row { display: flex; justify-content: space-between; gap: 12px; margin-top: 14px; }
  .stat { flex: 1; text-align: left; }
  .stat label { display: block; font-size: 12px; color: #66786f; margin-bottom: 6px; }
  .stat .val { font-size: 26px; font-weight: 700; color: #2e7d54; }
  #chart { width: 100%; height: calc(100% - 34px); }
</style>
"""

PLOTLY_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"


def render_chart_card(title: str, fig_data: list, layout: dict, height: int = 340) -> None:
    """Render a card containing a Plotly chart as one self-contained HTML doc."""
    layout = {
        "margin": dict(l=10, r=10, t=6, b=6),
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"size": 12, "color": "#66786f"},
        "legend": {"orientation": "h", "y": -0.25, "x": 0.5, "xanchor": "center"},
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


def render_overview_card(stats: list, height: int = 190) -> None:
    stat_html = "".join(
        f"<div class='stat'><label>{label}</label><div class='val'>{value}</div></div>"
        for label, value in stats
    )
    html = f"""
    <html><head>{CARD_CSS}</head>
    <body>
      <div class="card">
        <div class="title"><span class="dot"></span>Analytics Overview</div>
        <div class="stat-row">{stat_html}</div>
      </div>
    </body></html>
    """
    components.html(html, height=height)


# ---------------------------------------------------------------------------
# Analytics Overview
# ---------------------------------------------------------------------------
render_overview_card([
    ("System Efficiency Index", "87.5%"),
    ("Predicted Water Savings", "$1,500"),
    ("Predicted Water Used", "4 hhm"),
    ("Predicted Deviation", "0.0%"),
])

st.write("")

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]

# ---------------------------------------------------------------------------
# Row 1: Moisture trend | Weather analysis
# ---------------------------------------------------------------------------
row1_left, row1_right = st.columns(2)

with row1_left:
    render_chart_card(
        "Predictive Soil Moisture Trend",
        [
            {"x": DAYS, "y": [45, 60, 55, 70, 50, 40, 35], "name": "Zone 1",
             "mode": "lines", "line": {"color": "#2e7d54", "shape": "spline"},
             "fill": "tozeroy", "fillcolor": "rgba(46,125,84,0.15)"},
            {"x": DAYS, "y": [30, 42, 50, 65, 58, 48, 44], "name": "Zone 2",
             "mode": "lines", "line": {"color": "#4CAF7D", "shape": "spline"},
             "fill": "tozeroy", "fillcolor": "rgba(76,175,125,0.12)"},
            {"x": DAYS, "y": [55, 48, 60, 52, 66, 60, 52], "name": "Zone 3",
             "mode": "lines", "line": {"color": "#9ccc9a", "shape": "spline"},
             "fill": "tozeroy", "fillcolor": "rgba(156,204,154,0.1)"},
        ],
        {"yaxis": {"range": [0, 100], "gridcolor": "#eef4f0"}},
    )

with row1_right:
    render_chart_card(
        "Weather Analysis",
        [
            {"x": DAYS, "y": [10, 25, 15, 30, 20, 18, 22], "name": "Rainfall (mm)",
             "mode": "lines", "line": {"color": "#3a9668", "shape": "spline"}},
            {"x": DAYS, "y": [20, 18, 28, 22, 30, 26, 24], "name": "Soil Moisture",
             "mode": "lines", "line": {"color": "#e0a530", "dash": "dash", "shape": "spline"}},
        ],
        {},
    )

st.write("")

# ---------------------------------------------------------------------------
# Row 2: Water vs. Energy | Cost analysis
# ---------------------------------------------------------------------------
row2_left, row2_right = st.columns(2)

with row2_left:
    render_chart_card(
        "Water vs. Energy Efficiency",
        [
            {"x": MONTHS, "y": [1200, 900, 1350, 1000, 1500, 1100, 1600, 1250],
             "name": "Water Used (L)", "type": "bar", "marker": {"color": "#3a9668"}},
            {"x": MONTHS, "y": [300, 220, 340, 260, 380, 290, 400, 310],
             "name": "Energy Cost ($)", "type": "bar", "marker": {"color": "#bfe8cf"}},
        ],
        {"barmode": "group"},
    )

with row2_right:
    render_chart_card(
        "Cost Analysis",
        [
            {
                "type": "pie",
                "labels": ["Water Saved", "Energy Used", "Maintenance"],
                "values": [55, 30, 15],
                "hole": 0.6,
                "marker": {"colors": ["#2e7d54", "#e0a530", "#bfe8cf"]},
            }
        ],
        {"legend": {"orientation": "h", "y": -0.15, "x": 0.5, "xanchor": "center"}},
    )