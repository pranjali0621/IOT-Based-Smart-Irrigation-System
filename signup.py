"""
Nature-themed Sign Up page (Streamlit) - pixel-matched to the 1366x768 design.

Folder layout:
    app.py
    assets/signup.png     <- background (leafy card, vines, grass) WITHOUT the form
    .streamlit/config.toml

Run:
    streamlit run app.py

How the "exact match" works
---------------------------
The background is stretched to the viewport (100% x 100%), and every size and
position below is written in units of the original 1366x768 design:
    X(n) = n px of the design, horizontally  ->  n * 100vw / 1366
    Y(n) = n px of the design, vertically    ->  n * 100vh / 768
so the form scales together with the artwork at any window size.
"""
import base64
import re
from pathlib import Path

import streamlit as st

BACKGROUND_PATH = Path(__file__).parent / "assets" / "signup.png"

st.set_page_config(
    page_title="Sign Up",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def image_to_base64(path: str) -> str | None:
    p = Path(path)
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None


def inject_css() -> None:
    b64 = image_to_base64(str(BACKGROUND_PATH))
    if b64:
        bg = f'url("data:image/png;base64,{b64}") center / 100% 100% no-repeat fixed'
    else:
        bg = "linear-gradient(160deg, #e9f7df 0%, #f3fbee 50%, #d8f0c4 100%)"

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Itim&display=swap');

:root {{
    --x: calc(100vw / 1366);          /* 1 design-pixel, horizontal */
    --y: calc(100vh / 768);           /* 1 design-pixel, vertical   */
    --label:  #64a84a;
    --border: #9ad650;
    --fill:   #eef8eb;
    --terms:  #4f7a00;
    --forest: #006400;
    --check:  #6aaa4a;
}}

/* ---------- page ---------- */
html, body, .stApp, .stApp *:not([data-testid="stIconMaterial"]) {{ font-family: 'Itim', 'Comic Sans MS', cursive; }}
[data-testid="stIconMaterial"] {{ font-family: 'Material Symbols Rounded' !important; }}
.stApp {{ background: {bg}; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {{ display: none; }}

.block-container, [data-testid="stMainBlockContainer"] {{
    max-width: 100% !important;
    padding: calc(var(--y) * 112) 0 0 0 !important;   /* first label starts at y=112 */
}}
[data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
[data-testid="stHorizontalBlock"] {{ gap: 0 !important; flex-wrap: nowrap !important; }}
[data-testid="stColumn"] {{ min-width: 0 !important; }}

/* ---------- sidebar (collapsed by default) ---------- */
[data-testid="stSidebar"] {{
    background: rgba(233, 247, 223, .95);
    border-right: 2px solid var(--border);
}}
[data-testid="stSidebar"] * {{ color: var(--terms) !important; }}
[data-testid="stSidebar"] img {{ border-radius: 14px; border: 2px solid var(--border); }}

/* ---------- labels ---------- */
[data-testid="stWidgetLabel"] {{
    height: calc(var(--y) * 28);
    min-height: 0 !important;
    margin: 0 0 calc(var(--y) * 6) 0 !important;
    padding: 0 !important;
    display: flex; align-items: center;
}}
[data-testid="stWidgetLabel"] p {{
    font-size: calc(var(--x) * 25) !important;
    line-height: 1 !important;
    color: var(--label) !important;
    margin: 0 0 0 calc(var(--x) * 12) !important;
}}

/* ---------- text inputs: green border, rounded, soft drop shadow ---------- */
[data-testid="stTextInput"] {{ margin-bottom: calc(var(--y) * 17); }}
[data-testid="stTextInputRootElement"],
[data-testid="stTextInput"] [data-baseweb="input"] {{
    height: calc(var(--y) * 50);
    min-height: 0;
    background: var(--fill) !important;
    border: 2.5px solid var(--border) !important;          /* green border */
    border-radius: calc(var(--x) * 17) !important;
    box-shadow: calc(var(--x) * 10) calc(var(--y) * 12) calc(var(--x) * 12) rgba(0, 0, 0, .26);
    overflow: hidden;
}}
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextInput"] input {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #3d6b1f;
    font-size: calc(var(--x) * 22);
    padding-left: calc(var(--x) * 16);
}}
[data-testid="stTextInputRootElement"]:focus-within {{
    border-color: #6fc13a !important;
    box-shadow: calc(var(--x) * 10) calc(var(--y) * 12) calc(var(--x) * 12) rgba(0, 0, 0, .26),
                0 0 0 3px rgba(154, 214, 80, .35);
}}
[data-testid="InputInstructions"] {{ display: none; }}                 /* "Press Enter to apply" */

/* show / hide password (eye icon) */
[data-testid="stTextInputRootElement"] button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin-right: calc(var(--x) * 8);
    color: var(--label) !important;
}}
[data-testid="stTextInputRootElement"] button:hover {{ color: #3d6b1f !important; }}
[data-testid="stTextInputRootElement"] button svg,
[data-testid="stTextInputRootElement"] button [data-testid="stIconMaterial"] {{
    color: inherit !important;
    fill: currentColor;
    width: calc(var(--x) * 24);
    height: calc(var(--x) * 24);
    font-size: calc(var(--x) * 24);
}}

/* ---------- checkbox: green square with white tick ---------- */
[data-testid="stCheckbox"] {{
    margin: calc(var(--y) * -2) 0 0 calc(var(--x) * 10);
    min-height: 0;
}}
[data-testid="stCheckbox"] label {{ align-items: center; }}
[data-testid="stCheckbox"] label > span:first-child {{
    width: calc(var(--x) * 30);
    height: calc(var(--x) * 30);
    border-radius: calc(var(--x) * 6);
    background-color: var(--fill) !important;
    border: 2px solid var(--check) !important;
}}
[data-testid="stCheckbox"] label:has(input:checked) > span:first-child {{
    background-color: var(--check) !important;
    border-color: var(--check) !important;
}}
[data-testid="stCheckbox"] label p {{
    font-size: calc(var(--x) * 24) !important;
    color: var(--terms) !important;
    margin-left: calc(var(--x) * 4);
}}

/* ---------- buttons (centred in the form column, nudged right like the design) ---------- */
[data-testid="stButton"] {{
    display: flex;
    justify-content: center;
    width: 100%;
    padding-left: calc(var(--x) * 48);
}}
[data-testid="stButton"] button p {{ white-space: nowrap; overflow: visible; }}

/* Sign Up: smaller pill, green -> lime gradient */
[data-testid="stButton"] button[kind="primary"] {{
    width: calc(var(--x) * 190);
    height: calc(var(--y) * 52);
    margin-top: calc(var(--y) * 19);
    border: none;
    border-radius: 999px;
    background: linear-gradient(90deg, #7ad84f 0%, #c9e35f 100%);
    box-shadow: calc(var(--x) * 7) calc(var(--y) * 10) calc(var(--x) * 10) rgba(0, 0, 0, .26);
    transition: transform .15s ease;
}}
[data-testid="stButton"] button[kind="primary"] p {{
    font-size: calc(var(--x) * 26);
    color: #fff !important;
}}
[data-testid="stButton"] button[kind="primary"]:hover {{ transform: translateY(-2px); }}

/* Continue with Google: bold dark-green text link, never truncated */
[data-testid="stButton"] button[kind="secondary"] {{
    width: auto;
    min-width: max-content;
    height: calc(var(--y) * 44);
    margin-top: calc(var(--y) * 16);
    padding: 0 calc(var(--x) * 8);
    background: transparent;
    border: none;
    box-shadow: none;
}}
[data-testid="stButton"] button[kind="secondary"] p {{
    font-size: calc(var(--x) * 27);
    font-weight: 700;
    color: var(--forest) !important;
}}
[data-testid="stButton"] button[kind="secondary"]:hover p {{ text-decoration: underline; }}

/* ---------- messages (shown below the form) ---------- */
[data-testid="stAlert"] {{ margin-top: calc(var(--y) * 10); border-radius: 14px; }}
</style>
""",
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?\d{7,15}$")


def validate(identifier: str, pw: str, confirm: str, accepted: bool) -> list[str]:
    errors = []
    ident = identifier.strip()
    if not ident:
        errors.append("Enter your email or phone number.")
    elif not (EMAIL_RE.match(ident) or PHONE_RE.match(re.sub(r"[\s-]", "", ident))):
        errors.append("That doesn't look like a valid email or phone number.")
    if len(pw) < 8:
        errors.append("Password must be at least 8 characters.")
    if pw != confirm:
        errors.append("Passwords don't match.")
    if not accepted:
        errors.append("Accept the terms and conditions to continue.")
    return errors


# ----------------------------------------------------------------------------
# Page
# ----------------------------------------------------------------------------
def signup_page() -> None:
    # widths from the design: 382px blank | 508px form | 476px blank
    _, form, _ = st.columns([382, 508, 476])

    with form:
        identifier = st.text_input("Enter Email or Phone no.", key="su_ident")
        password = st.text_input("Set Password", type="password", key="su_pw")
        confirm = st.text_input("Confirm Password", type="password", key="su_confirm")
        accepted = st.checkbox("I have accepted all terms and conditions.", value=True, key="su_terms")

        signed_up = st.button("Sign Up", type="primary", key="su_submit")
        google = st.button("Continue with Google", key="su_google")

        if signed_up:
            errors = validate(identifier, password, confirm, accepted)
            if errors:
                st.toast("\n\n".join(errors), icon="⚠️")
            else:
                st.session_state.user = identifier.strip()
                st.toast("Welcome aboard! Your account has been created.", icon="🌱")
                st.switch_page("create.py")
        if google:
            st.toast("Google sign-in isn't connected yet. Add your OAuth flow here.", icon="ℹ️")


inject_css()

# Sidebar navigation (collapsed by default so the page matches the design)
with st.sidebar:
    if BACKGROUND_PATH.exists():
        st.image(str(BACKGROUND_PATH))
    st.radio("Navigate", ["🌱 Sign Up"], label_visibility="collapsed")

signup_page()