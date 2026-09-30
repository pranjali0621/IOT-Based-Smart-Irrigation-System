import base64
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Create Your Garden", layout="wide")

st.session_state.setdefault("auth_token", None)

# Guard: ensure user is logged in
if not st.session_state.get("auth_token"):
    st.warning("You must log in to access the Create page.")
    if st.button("Go to Login"):
        st.switch_page("pages/2_Login.py")
    st.stop()

# Auto-redirect for admin
if st.session_state.get("is_admin"):
    st.switch_page("pages/9_Admin.py")

import requests

BACKEND_URL = "http://localhost:8000"
token = st.session_state.get("auth_token")

# Step 1 & 2: Check if user has plants
def check_user_plants():
    try:
        res = requests.get(f"{BACKEND_URL}/api/plants/my-plants", headers={"Authorization": f"Bearer {token}"}, timeout=5)
        if res.status_code == 200:
            plants = res.json().get("plants", [])
            return len(plants) > 0
    except:
        pass
    return False

st.session_state.has_plants = check_user_plants()

# ---- Path to the background image (lives in the "assets" folder) ----
BG_IMAGE_PATH = Path(__file__).parent / "assets" / "create.png"


def get_base64(path) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


bg_base64 = get_base64(BG_IMAGE_PATH)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,700;1,800&display=swap');

    #MainMenu, header, footer {{visibility: hidden;}}

    html, body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        height: 100%;
    }}

    [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        overflow: hidden !important;
        height: 100vh !important;
    }}

    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh !important;
        overflow: hidden !important;
    }}

    .stApp {{
        background-image: url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        height: 100vh;
        width: 100vw;
        overflow: hidden;
        position: fixed;
        top: 0;
        left: 0;
    }}

    .st-key-button_wrapper {{
        position: fixed;
        left: 38.7%;
        top: 72.8%;
        width: 26.5%;
        z-index: 10;
    }}

    /* Streamlit wraps buttons in multiple divs. We want them stacked with a gap */
    .st-key-button_wrapper > div > div {{
        display: flex;
        flex-direction: column;
        gap: 1.5vh;
    }}

    div[data-testid="stButton"] {{
        width: 100%;
    }}

    div[data-testid="stButton"] > button {{
        width: 100%;
        padding: 0.7vw 0;
        font-family: 'Playfair Display', Georgia, 'Times New Roman', serif !important;
        font-style: italic !important;
        font-weight: 800 !important;
        font-size: 2.35vw !important;
        white-space: nowrap !important;
        letter-spacing: 0.5px;
        color: #ffffff;
        background: linear-gradient(180deg, #9ed15a 0%, #6fae2e 100%);
        border: none;
        border-radius: 4vw;
        box-shadow: 0 6px 0 rgba(90, 140, 40, 0.6), 0 10px 18px rgba(0,0,0,0.15);
        cursor: pointer;
        transition: transform 0.15s ease;
    }}

    div[data-testid="stButton"] > button p {{
        font-family: 'Playfair Display', Georgia, 'Times New Roman', serif !important;
        font-style: italic !important;
        font-weight: 800 !important;
        font-size: 2.35vw !important;
        white-space: nowrap !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        transform: translateY(-2px);
        color: #ffffff;
    }}

    div[data-testid="stButton"] > button:active {{
        transform: translateY(2px);
        box-shadow: 0 3px 0 rgba(90, 140, 40, 0.6), 0 6px 10px rgba(0,0,0,0.15);
    }}

    .garden-quote {{
        position: fixed;
        top: 89%;
        left: 0;
        width: 100%;
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-weight: 600;
        font-size: 1.35vw;
        color: #5a9c3e;
        z-index: 20;
        pointer-events: none;
    }}
    </style>

    <div class="garden-quote">Listening to your plants, byte by byte...</div>
    """,
    unsafe_allow_html=True,
)

# Step 3: Show different button based on has_plants
with st.container(key="button_wrapper"):
    if st.session_state.has_plants:
        if st.button("📊 Go to Dashboard", key="go_dashboard_btn"):
            st.switch_page("pages/6_Dashboard.py")
        if st.button("🌱 Add Another Plant", key="create_garden_btn"):
            st.switch_page("pages/5_Garden.py")
    else:
        if st.button("🌱 Add Your First Plant", key="create_garden_btn"):
            st.switch_page("pages/5_Garden.py")

# Optional header
def add_header():
    if st.session_state.has_plants:
        st.title("Welcome back!")
        st.write("Go to your dashboard to monitor your plants.")
    else:
        st.title("Welcome! Ready to grow?")
        st.write("Set up your first plant to get started")
add_header()