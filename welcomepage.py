import base64
from pathlib import Path

import streamlit as st

# Helper function to encode local background image to base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Set layout configurations
st.set_page_config(page_title="Smart Garden", page_icon="🌱", layout="wide")

# Load Background Image (lives in the "assets" folder next to this script)
ASSET_DIR = Path(__file__).parent / "assets"
img_base64 = get_base64_of_bin_file(str(ASSET_DIR / "welcome.jpg"))
if img_base64:
    bg_style = f'background-image: url("data:image/jpg;base64,{img_base64}");'
else:
    bg_style = 'background: linear-gradient(to bottom, #d6ebce, #e2f4df);'

# Inject external web font via link tag
st.markdown("""
<link rel="stylesheet" href="https://fonts.cdnfonts.com/css/apricots">
""", unsafe_allow_html=True)

# Inject Custom CSS
st.markdown(f"""
<style>
/* Set full background image */
.stApp {{
    {bg_style}
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

/* Hide default Streamlit header */
header {{
    visibility: hidden;
}}

/* Fix button position to bottom-center of screen */
div.stButton {{
    position: fixed !important;
    bottom: 80px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    z-index: 9999 !important;
    width: auto !important;
    text-align: center;
}}

/* Custom button styling with Drop Shadow Effect */
div.stButton > button {{
    background-color: #647d00 !important;
    color: #ffffff !important;
    font-family: 'Apricots', 'Caveat', cursive, sans-serif !important;
    font-size: 20px !important;
    font-weight: normal !important;
    padding: 6px 28px !important;
    border-radius: 18px !important;
    border: none !important;
    box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.3s ease-out !important;
    white-space: nowrap !important;
    position: relative;
    top: 0px;
}}

/* Inner button text font */
div.stButton > button p {{
    font-family: 'Apricots', 'Caveat', cursive, sans-serif !important;
    font-size: 20px !important;
    margin: 0 !important;
    color: #ffffff !important;
}}

/* Hover interaction */
div.stButton > button:hover {{
    background-color: #4e6200 !important;
    color: #ffffff !important;
    transform: scale(1.05) !important;
    top: -2px;
    box-shadow: 0px 12px 20px rgba(0, 0, 0, 0.5) !important;
}}

/* Active click interaction */
div.stButton > button:active {{
    top: 2px !important;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.1s ease-out !important;
}}

/* Style for the floating success toast message container */
.stToast {{
    position: fixed !important;
    bottom: 20px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    z-index: 10000 !important;
}}
</style>
""", unsafe_allow_html=True)

# Button click logic: show the toast, then move on to the login page
if st.button("Let's Start", key="lets_start_btn"):
    st.toast("🌱 Welcome to Smart Garden! Let's get started.", icon="✅")
    st.switch_page("login.py")
   