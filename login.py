import base64
import re
from pathlib import Path

import streamlit as st

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
ASSET_DIR = Path(__file__).parent / "assets"
BG_STEM = "background"
REF_W, REF_H = 1366, 768          # size of the background design

# name: (x, y, width)  -> pixels on the 1366 x 768 design, top-left origin
LAYOUT = {
    "lbl_user":   (415, 197, None),
    "login_user": (408, 231, 509),
    "lbl_pwd":    (416, 299, None),
    "login_pwd":  (408, 334, 509),
    "forgot_btn": (420, 406, None),
    "login_btn":  (517, 448, 254),
    "signup_btn": (499, 525, 298),
}

st.set_page_config(
    page_title="PlantPulse | Login",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------------------------------------------------------
# ASSET HELPERS
# ----------------------------------------------------------------------------
def find_background():
    for folder in (ASSET_DIR, Path(__file__).parent):
        for ext in ("png", "jpg", "jpeg", "webp"):
            path = folder / f"{BG_STEM}.{ext}"
            if path.exists():
                return path
    return None


@st.cache_data(show_spinner=False)
def image_data_uri(path_str: str) -> str:
    path = Path(path_str)
    mime = {".png": "image/png", ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", ".webp": "image/webp"}[path.suffix.lower()]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


# ----------------------------------------------------------------------------
# STYLES
# ----------------------------------------------------------------------------
# "@{N}" = N pixels of the 1366-wide design, converted to cqw (1cqw = 1% of the
# stage width) so fonts, borders and sizes scale together with the background.
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

:root {
    --leaf: #8fd44f;
    --leaf-soft: #72b062;
    --leaf-dark: #2d5a12;
    --paper: #ecf8e9;
    --hand: 'Patrick Hand', 'Comic Sans MS', cursive;
}

/* ---------- page shell ---------- */
.stApp, [data-testid="stAppViewContainer"] { background: #ecf8e9; font-family: var(--hand); }
header[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], footer, #MainMenu { display: none !important; }
.block-container, [data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    padding: 0 !important;
}

/* ---------- stage: the background image, scaled to COVER the whole screen ---------- */
/* Same maths as background-size: cover, but on a box the widgets are pinned to,
   so the labels / inputs / buttons stay exactly inside the card. */
.st-key-stage {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: min(max(100vw, calc(100vh * 1366 / 768)), 179vw);
    aspect-ratio: 1366 / 768;
    margin: 0;
    gap: 0;
    background-image: %%BG%%;
    background-size: 100% 100%;
    background-repeat: no-repeat;
    container-type: inline-size;
}

/* ---------- labels ---------- */
.st-key-stage .pp-label {
    font-family: var(--hand);
    font-size: @{26};
    line-height: 1;
    white-space: nowrap;
    color: var(--leaf-soft);
}
.st-key-lbl_user [data-testid="stMarkdownContainer"],
.st-key-lbl_pwd  [data-testid="stMarkdownContainer"] { margin: 0; padding: 0; }

/* ---------- inputs: green rounded border ---------- */
.st-key-login_user, .st-key-login_pwd {
    box-sizing: border-box;
    height: @{50};
    display: flex;
    align-items: center;
    background: var(--paper);
    border: max(2px, @{2.5}) solid var(--leaf);
    border-radius: @{16};
    box-shadow: @{9} @{10} @{12} rgba(0, 0, 0, 0.22);
    transition: border-color 0.15s;
}
.st-key-login_user:focus-within, .st-key-login_pwd:focus-within { border-color: #5fb82c; }

/* strip Streamlit's own field chrome so only the green border shows */
:is(.st-key-login_user, .st-key-login_pwd) :is([data-testid="stTextInput"],
    [data-testid="stTextInputRootElement"], [data-baseweb="input"], [data-baseweb="base-input"]) {
    width: 100%;
    height: @{44};
    min-height: 0;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
    border-radius: @{14};
}
:is(.st-key-login_user, .st-key-login_pwd) input {
    height: 100%;
    padding: 0 @{16};
    font-family: var(--hand);
    font-size: @{21};
    color: var(--leaf-dark);
}
/* keep the (visually hidden) labels for screen readers */
:is(.st-key-login_user, .st-key-login_pwd) [data-testid="stWidgetLabel"] {
    position: absolute; width: 1px; height: 1px; margin: 0; padding: 0;
    overflow: hidden; clip: rect(0 0 0 0);
}
:is(.st-key-login_user, .st-key-login_pwd) button,          /* password "eye" icon */
:is(.st-key-login_user, .st-key-login_pwd) [data-testid="InputInstructions"] { display: none !important; }

/* ---------- forgot password ---------- */
.st-key-forgot_btn button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    min-height: 0 !important;
}
.st-key-forgot_btn button p {
    margin: 0;
    font-family: var(--hand);
    font-size: @{22};
    line-height: 1;
    font-weight: 700;
    color: var(--leaf-dark);
}
.st-key-forgot_btn button:hover p { text-decoration: underline; }

/* ---------- login button ---------- */
.st-key-login_btn [data-testid="stButton"],
.st-key-signup_btn [data-testid="stButton"] { width: 100%; }
.st-key-login_btn button {
    width: 100%;
    height: @{57};
    min-height: 0;
    padding: 0;
    border: none !important;
    border-radius: 999px;
    background: linear-gradient(90deg, #8fdc55 0%, #c9e25f 100%) !important;
    box-shadow: @{8} @{10} @{14} rgba(0, 0, 0, 0.26);
}
.st-key-login_btn button p {
    margin: 0;
    font-family: var(--hand);
    font-size: @{29};
    line-height: 1;
    color: #fff;
}
.st-key-login_btn button:hover { filter: brightness(1.06); }
.st-key-login_btn button:active { transform: translateY(1px); }

/* ---------- sign-up button ---------- */
.st-key-signup_btn button {
    width: 100%;
    height: @{49};
    min-height: 0;
    padding: 0;
    border: max(2px, @{3}) solid var(--leaf) !important;
    border-radius: 0;
    background: var(--paper) !important;
    box-shadow: @{8} @{10} @{14} rgba(0, 0, 0, 0.22);
}
.st-key-signup_btn button p {
    margin: 0;
    font-family: var(--hand);
    font-size: @{22};
    line-height: 1;
    color: var(--leaf-soft);
    white-space: nowrap;
}
.st-key-signup_btn button:hover { background: #e0f4da !important; }

/* ---------- simple pages (reset-password placeholder) ---------- */
.st-key-plain { max-width: 560px; margin: 12vh auto 0; padding: 0 1rem; }
</style>
"""


def layout_css() -> str:
    """Absolute position of every element, as % of the stage."""
    rules = []
    for name, (x, y, w) in LAYOUT.items():
        width = f"width: {w / REF_W * 100:.4f}%;" if w else ""
        rules.append(
            f".st-key-{name} {{ position: absolute; margin: 0; "
            f"left: {x / REF_W * 100:.4f}%; top: {y / REF_H * 100:.4f}%; {width} }}"
        )
    return "<style>" + "\n".join(rules) + "</style>"


def inject_styles(bg_uri=None) -> None:
    css = BASE_CSS.replace("%%BG%%", f'url("{bg_uri}")' if bg_uri else "none")
    css = re.sub(
        r"@\{(\d+(?:\.\d+)?)\}",
        lambda m: f"{float(m.group(1)) / REF_W * 100:.4f}cqw",
        css,
    )
    st.markdown(css + layout_css(), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# ACTIONS
# ----------------------------------------------------------------------------
def go(page: str) -> None:
    st.session_state.page = page


def handle_login() -> None:
    user = st.session_state.get("login_user", "").strip()
    pwd = st.session_state.get("login_pwd", "")
    if not user or not pwd:
        st.toast("Please enter your username/email and password.", icon="🌱")
        return

    # TODO: replace with real authentication (database / API / hashed check)
    st.session_state.user = user
    st.switch_page("create.py")


def go_to_signup() -> None:
    st.switch_page("signup.py")


# ----------------------------------------------------------------------------
# PAGES
# ----------------------------------------------------------------------------
def login_page() -> None:
    bg = find_background()
    if bg is None:
        st.error(f"Background image not found. Save it as '{BG_STEM}.png' in: {ASSET_DIR}")
        st.stop()
    inject_styles(image_data_uri(str(bg)))

    with st.container(key="stage"):
        with st.container(key="lbl_user"):
            st.markdown('<div class="pp-label">Enter Username or Email</div>',
                        unsafe_allow_html=True)
        st.text_input("Username or email", key="login_user",
                      label_visibility="collapsed")

        with st.container(key="lbl_pwd"):
            st.markdown('<div class="pp-label">Enter Password</div>',
                        unsafe_allow_html=True)
        st.text_input("Password", type="password", key="login_pwd",
                      label_visibility="collapsed")

        st.button("Forgot password?", key="forgot_btn", on_click=go, args=("forgot",))
        st.button("Login", key="login_btn", on_click=handle_login)
        st.button("Create account ? Sign up ➔", key="signup_btn",
                  on_click=go_to_signup)


def simple_page(title: str, message: str) -> None:
    # this page doesn't use the stage, so only the base shell styles apply
    inject_styles()
    with st.container(key="plain"):
        st.title(title)
        st.write(message)
        st.button("← Back to login", key="back_btn", on_click=go, args=("login",))


# ----------------------------------------------------------------------------
# ROUTER
# ----------------------------------------------------------------------------
st.session_state.setdefault("page", "login")
page = st.session_state.page

if page == "forgot":
    simple_page("Reset your password", "Password-reset form goes here.")
else:
    login_page()
 
 