import base64
import os
import streamlit as st
import requests
import time

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Add Plants to Your Garden",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================================================
# PATHS
# ==================================================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BACKGROUND_PATH = os.path.join(APP_DIR, "assets", "garden_bg.png")

BACKEND_URL = "http://localhost:8000"


def get_base64(path: str) -> str:
    """Read a local file and return its base64 encoding, or '' if missing."""
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


bg_b64 = get_base64(BACKGROUND_PATH)
bg_css_rule = (
    f'background-image: url("data:image/png;base64,{bg_b64}");'
    if bg_b64
    else "background-color: #EAF7E6;"
)

# ==================================================
# SESSION STATE
# ==================================================
if "plant_added" not in st.session_state:
    st.session_state.plant_added = False
if "last_sensor_id" not in st.session_state:
    st.session_state.last_sensor_id = ""
if "plant_image_b64" not in st.session_state:
    st.session_state.plant_image_b64 = ""
if "plant_image_mime" not in st.session_state:
    st.session_state.plant_image_mime = "image/png"
if "plant_image_name" not in st.session_state:
    st.session_state.plant_image_name = ""
if "plant_image_size_kb" not in st.session_state:
    st.session_state.plant_image_size_kb = 0.0
if "uploader_version" not in st.session_state:
    st.session_state.uploader_version = 0
if "error_message" not in st.session_state:
    st.session_state.error_message = ""

# ==================================================
# CSS
# ==================================================
# ================= Auth Guard =================
if st.session_state.get("auth_token") is None:
    st.markdown("<div class='error-text'>You must login first.</div>", unsafe_allow_html=True)
    if st.button("Go to Login", key="login_redirect_btn"):
        st.switch_page("pages/2_Login.py")
    st.stop()

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Kalam:wght@400;700&display=swap');

    /* ---- Hide default Streamlit chrome (no sidebar in this build) ---- */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    div[data-testid="stToolbar"] {{visibility: hidden; height: 0; position: fixed;}}
    div[data-testid="stDecoration"] {{visibility: hidden;}}
    div[data-testid="stStatusWidget"] {{visibility: hidden;}}
    section[data-testid="stSidebar"] {{display: none;}}

    .block-container {{
        padding-top: 64px;
        padding-bottom: 2rem;
        padding-left: 103px;
        padding-right: 103px;
        max-width: 1366px;
    }}

    /* ---- Background ---- */
    .stApp {{
        {bg_css_rule}
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    html, body, [class*="css"] {{
        font-family: 'Patrick Hand', 'Kalam', cursive;
    }}

    /* ---- Two-column stage: cards forced side-by-side, exact 61px gap ---- */
    div[data-testid="stHorizontalBlock"] {{
        display: flex;
        flex-wrap: nowrap;
        gap: 61px;
        align-items: flex-start;
        width: 100%;
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) {{
        flex: 0 0 519px;
        max-width: 519px;
        min-width: 519px;
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {{
        flex: 0 0 520px;
        max-width: 520px;
        min-width: 520px;
        margin-top: 6px; /* right card sits 6px lower in the reference */
    }}

    /* ---- Card container ---- */
    .st-key-left_card, .st-key-right_card {{
        box-sizing: border-box;
        width: 100%;
        background-color: #EAF7E6;
        border: 2px solid #7ED321;
        border-radius: 32px;
        box-shadow: 0 12px 24px rgba(50, 70, 40, 0.22);
        padding: 30px 40px 36px 40px;
    }}
    .st-key-left_card {{ min-height: 632px; }}
    .st-key-right_card {{ min-height: 626px; }}

    .card-heading {{
        color: #087522;
        font-size: 30px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 16px;
    }}

    .field-label {{
        color: #2E7D32;
        font-size: 22px;
        margin-bottom: 2px;
        margin-top: 8px;
    }}

    /* The bordered box lives on stTextInput/stTextArea itself — the one
       outer wrapper Streamlit always tags with this testid, regardless of
       version — rather than on BaseWeb's internal input wrapper, whose
       exact attribute apparently didn't match here and produced no
       border at all. The label above is already collapsed to zero
       height, so this box wraps only the visible input area. */
    div[data-testid="stTextInput"],
    div[data-testid="stTextArea"] {{
        width: 100% !important;
        max-width: 440px !important;
        box-sizing: border-box !important;
        background-color: #F3FBEF !important;
        border: 2px solid #A9DD9B !important;
        border-radius: 17px !important;
        box-shadow: 0 10px 16px rgba(50, 70, 40, 0.20) !important;
        overflow: hidden !important;
    }}
    div[data-testid="stTextInput"]:focus-within,
    div[data-testid="stTextArea"]:focus-within {{
        border: 2px solid #7ED321 !important;
        box-shadow: 0 0 0 3px rgba(169, 221, 155, 0.45) !important;
    }}
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label {{
        display: none !important;
    }}
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextArea"] > div,
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextArea"] div[data-baseweb="textarea"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {{
        width: 100% !important;
        height: 52px !important;
        box-sizing: border-box !important;
        background-color: transparent !important;
        border: none !important;
        font-family: 'Patrick Hand', cursive !important;
        font-size: 18px !important;
        color: #2E7D32 !important;
        padding: 8px 16px !important;
    }}
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {{
        outline: none !important;
    }}

    /* ---- File uploader dropzone (only shown before a photo exists) ---- */
    div[data-testid="stFileUploader"],
    div[data-testid="stFileUploader"] * {{
        font-family: 'Patrick Hand', cursive !important;
    }}
    div[data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploader"] section {{
        width: 100% !important;
        max-width: 440px !important;
        min-height: 52px !important;
        box-sizing: border-box !important;
        background-color: #F3FBEF !important;
        border: 2px dashed #7ED321 !important;
        border-radius: 17px !important;
        box-shadow: 0 8px 14px rgba(50, 70, 40, 0.15) !important;
        padding: 4px 10px !important;
    }}
    /* The dropzone shows exactly one "Upload" label, drawn once via a
       single ::after on the OUTER container itself — never on the native
       button — which is what guarantees it can never appear twice no
       matter how many internal button/text elements Streamlit renders.
       All of Streamlit's own text/icon/button visuals are made invisible
       (not display:none, so the area stays clickable and drag-and-drop
       still works), then this one decorative label is layered on top. */
    div[data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploader"] section {{
        position: relative !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button,
    section[data-testid="stFileUploaderDropzone"] button,
    div[data-testid="stFileUploader"] section button,
    div[data-testid="stFileUploaderDropzone"] button *,
    section[data-testid="stFileUploaderDropzone"] button *,
    div[data-testid="stFileUploader"] section button *,
    section[data-testid="stFileUploaderDropzoneInstructions"],
    section[data-testid="stFileUploaderDropzoneInstructions"] *,
    div[data-testid="stFileUploader"] section span,
    div[data-testid="stFileUploader"] section small,
    div[data-testid="stFileUploader"] section p,
    div[data-testid="stFileUploaderDropzone"] svg,
    section[data-testid="stFileUploaderDropzone"] svg {{
        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;
        visibility: hidden !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button::before,
    div[data-testid="stFileUploaderDropzone"] button::after,
    section[data-testid="stFileUploaderDropzone"] button::before,
    section[data-testid="stFileUploaderDropzone"] button::after,
    div[data-testid="stFileUploader"] section button::before,
    div[data-testid="stFileUploader"] section button::after {{
        content: none !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button,
    section[data-testid="stFileUploaderDropzone"] button,
    div[data-testid="stFileUploader"] section button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    div[data-testid="stFileUploaderDropzone"]::after,
    section[data-testid="stFileUploaderDropzone"]::after,
    div[data-testid="stFileUploader"] section::after {{
        content: "Upload" !important;
        position: absolute !important;
        top: 50% !important;
        left: 14px !important;
        transform: translateY(-50%) !important;
        visibility: visible !important;
        pointer-events: none !important;
        background: transparent !important;
        border: 1px solid #7ED321 !important;
        border-radius: 10px !important;
        padding: 6px 22px !important;
        color: #2E7D32 !important;
        font-family: 'Patrick Hand', cursive !important;
        font-size: 15px !important;
        line-height: 1.4 !important;
    }}

    /* ---- Custom "file chip" shown once a photo has been uploaded,
       replacing the native uploader widget entirely so no browse/upload
       button can ever appear again alongside it. ---- */
    .uploaded-chip {{
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;
        max-width: 440px;
        box-sizing: border-box;
        min-height: 52px;
        background-color: #F3FBEF;
        border: 2px dashed #7ED321;
        border-radius: 17px;
        box-shadow: 0 8px 14px rgba(50, 70, 40, 0.15);
        padding: 8px 16px;
        margin-bottom: 4px;
    }}
    .uploaded-chip-icon {{
        width: 32px;
        height: 32px;
        border-radius: 8px;
        overflow: hidden;
        flex: 0 0 32px;
        background-color: #cfe9c3;
    }}
    .uploaded-chip-icon img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }}
    .uploaded-chip-text {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        line-height: 1.2;
    }}
    .uploaded-chip-name {{
        color: #2E7D32;
        font-size: 15px;
        font-family: 'Patrick Hand', cursive;
    }}
    .uploaded-chip-size {{
        color: #6BA05A;
        font-size: 12px;
        font-family: 'Patrick Hand', cursive;
    }}

    /* ---- Add Plant button: 377 x 63 ---- */
    div[data-testid="stButton"] button,
    div.stButton > button {{
        width: 100% !important;
        max-width: 377px !important;
        height: 63px !important;
        min-height: 63px !important;
        box-sizing: border-box !important;
        border-radius: 32px !important;
        border: none !important;
        background: linear-gradient(90deg, #8DDB4E 0%, #C9E75B 100%) !important;
        color: white !important;
        font-family: 'Patrick Hand', cursive !important;
        font-size: 26px !important;
        line-height: 1 !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 18px rgba(50, 70, 40, 0.28) !important;
        margin: 18px auto 0 auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 24px !important;
    }}
    div[data-testid="stButton"] button p {{
        font-size: 26px !important;
        line-height: 1 !important;
    }}
    div[data-testid="stButton"] button:hover {{
        background: linear-gradient(90deg, #7fcf3e 0%, #bcd94a 100%) !important;
        color: white !important;
    }}
    div[data-testid="stButton"] {{
        display: flex !important;
        justify-content: center !important;
    }}

    /* ---- Remove-photo link button: small, text-only ---- */
    .st-key-remove_photo_wrap div[data-testid="stButton"] {{
        display: block !important;
        justify-content: flex-start !important;
    }}
    .st-key-remove_photo_wrap div[data-testid="stButton"] button {{
        all: unset !important;
        cursor: pointer !important;
        color: #B3261E !important;
        font-family: 'Patrick Hand', cursive !important;
        font-size: 15px !important;
        text-decoration: underline !important;
        margin: 6px 0 0 4px !important;
    }}
    .st-key-remove_photo_wrap div[data-testid="stButton"] button p {{
        font-size: 15px !important;
        color: #B3261E !important;
    }}

    /* ---- Preview box (right card): 230 x 228 ---- */
    .preview-box {{
        width: 230px;
        height: 228px;
        box-sizing: border-box;
        margin: 4px auto 20px auto;
        background-color: #EEF9EA;
        border: 2px solid #7ED321;
        border-radius: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }}
    .preview-box img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }}
    .no-plant-text {{
        color: #6BA05A;
        font-size: 16px;
        text-align: center;
        font-family: 'Patrick Hand', cursive;
    }}
    .status-text {{
        color: #087522;
        font-size: 25px;
        text-align: center;
        margin-top: 4px;
    }}
    .error-text {{
        color: #B3261E;
        font-size: 18px;
        text-align: center;
        margin-top: 8px;
        font-family: 'Patrick Hand', cursive;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# ADD PLANT PAGE (only page in this build)
# ==================================================
left_col, right_col = st.columns(2, gap="small")

# -------------------- LEFT CARD --------------------
with left_col:
    with st.container(key="left_card"):
        st.markdown(
            '<div class="card-heading">Add Plants to Your Garden</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="field-label">Plant Name</div>', unsafe_allow_html=True)
        plant_name = st.text_input(
            "Plant Name", key="plant_name_input", label_visibility="collapsed"
        )

        st.markdown('<div class="field-label">Sensor ID</div>', unsafe_allow_html=True)
        sensor_id = st.text_input(
            "Sensor ID", key="sensor_id_input", label_visibility="collapsed"
        )

        st.markdown(
            '<div class="field-label">Plant Description</div>', unsafe_allow_html=True
        )
        plant_description = st.text_input(
            "Plant Description",
            key="plant_description_input",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="field-label">Upload Plant Photo</div>', unsafe_allow_html=True
        )

        # Only render the uploader widget while there is NOT already a
        # stored photo. Once a photo exists we render a plain, static
        # "file chip" instead — this is what guarantees the browse/upload
        # button can never reappear or duplicate itself next to an
        # already-uploaded image, without relying on fragile CSS tricks
        # to hide Streamlit's internal buttons.
        if not st.session_state.plant_image_b64:
            uploaded_file = st.file_uploader(
                "Upload Plant Photo",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"photo_uploader_{st.session_state.uploader_version}",
                label_visibility="collapsed",
            )
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                st.session_state.plant_image_b64 = base64.b64encode(file_bytes).decode()
                st.session_state.plant_image_mime = uploaded_file.type or "image/png"
                st.session_state.plant_image_name = uploaded_file.name
                st.session_state.plant_image_size_kb = len(file_bytes) / 1024
                st.rerun()
        else:
            st.markdown(
                f"""
                <div class="uploaded-chip">
                    <div class="uploaded-chip-icon">
                        <img src="data:{st.session_state.plant_image_mime};base64,
                        {st.session_state.plant_image_b64}" alt="thumbnail" />
                    </div>
                    <div class="uploaded-chip-text">
                        <div class="uploaded-chip-name">{st.session_state.plant_image_name}</div>
                        <div class="uploaded-chip-size">{st.session_state.plant_image_size_kb:.1f}KB</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.session_state.plant_image_b64:
            with st.container(key="remove_photo_wrap"):
                if st.button("✕ Remove photo", key="remove_photo_btn"):
                    st.session_state.plant_image_b64 = ""
                    st.session_state.plant_image_mime = "image/png"
                    st.session_state.plant_image_name = ""
                    st.session_state.plant_image_size_kb = 0.0
                    st.session_state.uploader_version += 1
                    st.rerun()

        def handle_add_plant():
            """Validate input and send plant data to backend."""
            if not plant_name.strip():
                st.session_state.error_message = "Please enter a plant name."
                return

            if not sensor_id.strip():
                st.session_state.error_message = "Please enter a sensor ID."
                return

            data = {
                "name": plant_name.strip(),
                "sensor_id": sensor_id.strip(),
                "description": plant_description.strip(),
            }

            # Prepare photo for multipart upload if one exists.
            files = None
            if st.session_state.get("plant_image_b64"):
                photo_bytes = base64.b64decode(st.session_state.plant_image_b64)
                files = {
                    "photo": (
                        st.session_state.plant_image_name,
                        photo_bytes,
                        st.session_state.plant_image_mime,
                    )
                }

            headers = {
                "Authorization": f"Bearer {st.session_state.auth_token}"
            }

            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/plants/create",
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=10,
                )

                if response.status_code == 200:
                    st.session_state.error_message = ""
                    st.session_state.plant_added = True
                    st.session_state.last_sensor_id = sensor_id.strip()
                    st.session_state.pop("plants", None)  # clear cached plants
                    st.toast("Plant added! ✅")
                    time.sleep(1)
                    st.switch_page("pages/6_Dashboard.py")
                else:
                    try:
                        msg = response.json().get("detail", response.text)
                    except Exception:
                        msg = response.text
                    st.session_state.error_message = f"Error: {msg}"
                    st.session_state.plant_added = False

            except requests.RequestException as e:
                st.session_state.error_message = f"Exception: {e}"
                st.session_state.plant_added = False

        add_clicked = st.button("Add Plant", key="add_plant_btn")

        if add_clicked:
            handle_add_plant()

        if st.session_state.error_message:
            st.markdown(
                f'<div class="error-text">{st.session_state.error_message}</div>',
                unsafe_allow_html=True,
            )

# -------------------- RIGHT CARD --------------------
with right_col:
    with st.container(key="right_card"):
        st.markdown('<div class="card-heading">Plant Preview</div>', unsafe_allow_html=True)

        if st.session_state.plant_image_b64:
            preview_inner = (
                f'<img src="data:{st.session_state.plant_image_mime};base64,'
                f'{st.session_state.plant_image_b64}" alt="Plant photo" />'
            )
        else:
            preview_inner = '<div class="no-plant-text">No image yet</div>'

        st.markdown(
            f'<div class="preview-box">{preview_inner}</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.plant_added:
            st.markdown(
                '<div class="status-text">Plant added to the garden.</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="status-text">Sensor {st.session_state.last_sensor_id} linked</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-text">No plant added yet.</div>',
                unsafe_allow_html=True,
            )
# Navigation buttons
col1, col2 = st.columns(2, gap="small")
with col1:
    if st.button("Go to Dashboard", key="dashboard_btn"):
        st.switch_page("pages/6_Dashboard.py")
with col2:
    if st.button("About", key="about_btn"):
        st.switch_page("pages/7_About.py")