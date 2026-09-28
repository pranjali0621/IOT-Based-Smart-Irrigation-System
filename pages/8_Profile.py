import base64, json, re
from pathlib import Path
import streamlit as st

try:
    st.set_page_config(page_title="Smart Irrigation System – Profile", page_icon="💧", layout="wide")
except st.errors.StreamlitAPIException:
    pass  # already set by app.py

s = st.session_state
BASE = Path(__file__).parent
SAVE_FILE = BASE / "profile.json"
AVATAR = BASE / "assets" / "avatar.png"
DEFAULTS = dict(p_name="Pranjali Mahadik", p_email="mahadikpranjali37@gmail.com", p_phone="+91 98765 43210",
                p_city="Mumbai, India", p_alert_dry=True, p_alert_batt=True, p_alert_rain=False, p_weekly=True)

if "profile_init" not in s:
    saved = {}
    try:
        saved = json.loads(SAVE_FILE.read_text())
    except Exception:
        pass
    s.update({**DEFAULTS, **saved})
    s.profile_init = True


# ---------- background (same image as the settings page) ----------
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
bg = f"url({encode(str(bg_file), bg_file.stat().st_mtime)}) center/cover fixed," if bg_file else ""

# ---------- styling ----------
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');
:root{{--ink:#1f3a17;--mute:#5d7455;--g:#5a8a2c;--g2:#7fb03a;--line:#6f9a3d}}
html,body,.stApp,.stApp div,.stApp p,.stApp label,.stApp input,.stApp button{{font-family:'Outfit',system-ui,sans-serif}}
/* keep Streamlit's icon font so icons (eye, upload...) are not printed as words */
[data-testid="stIconMaterial"],[data-testid="stIconMaterial"] *{{font-family:"Material Symbols Rounded","Material Symbols Outlined","Material Icons"!important}}
.stApp{{background:{bg}#eef8ea;color:var(--ink)}}
header[data-testid="stHeader"]{{background:transparent}}
#MainMenu,footer{{visibility:hidden}}
.block-container{{max-width:1100px;padding:1.8rem 1.2rem 3rem}}
h1.t{{font-size:clamp(1.7rem,4vw,2.6rem);font-weight:700;letter-spacing:-.02em;margin:0;padding:0;color:var(--ink)}}

/* cards: equal height inside a row */
[data-testid="stHorizontalBlock"]{{align-items:stretch!important}}
[data-testid="stColumn"] div:has([class*="st-key-card_"]){{height:100%}}
[class*="st-key-card_"]{{position:relative;height:100%;background:rgba(255,255,255,.72);backdrop-filter:blur(6px);border:2px solid var(--line);border-radius:26px;padding:22px 24px;box-shadow:0 6px 18px rgba(60,90,30,.12)}}
.st-key-card_who{{align-items:stretch;justify-content:flex-start}}
.st-key-card_info>:last-child,.st-key-card_sec>:last-child{{margin-top:auto}}

.h2{{display:flex;align-items:center;gap:12px;font-size:1.3rem;font-weight:600;margin-bottom:.3rem}}
.h2 svg{{width:28px;height:28px;stroke:var(--g);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}

/* profile card */
.who{{text-align:center}}
.av{{width:132px;height:132px;border-radius:50%;margin:4px auto 14px;background:var(--g2) center/cover;border:4px solid #fff;box-shadow:0 0 0 2px var(--line);display:grid;place-items:center;color:#fff;font-size:2.8rem;font-weight:600}}
.who .n{{font-size:1.5rem;font-weight:600}}.who .e{{color:var(--mute);overflow-wrap:anywhere}}
.badge{{display:inline-block;margin-top:10px;background:#dff0bd;border:2px solid var(--line);border-radius:20px;padding:2px 14px;font-weight:500;font-size:.9rem}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:18px}}
.stats div{{background:#fff;border:2px solid var(--line);border-radius:18px;padding:8px 4px;text-align:center}}
.stats b{{display:block;font-size:1.3rem}}.stats span{{color:var(--mute);font-size:.8rem}}

/* camera button sitting on the avatar's bottom-right edge */
.st-key-photo_btn{{position:absolute;top:120px;left:calc(50% + 30px);width:38px;z-index:5}}
.st-key-photo_btn button{{width:38px;height:38px;min-height:0;padding:0;border-radius:50%;border:2px solid var(--line);background:linear-gradient(#c9e68a,#7fb03a)}}
.st-key-photo_btn button{{font-size:0;color:transparent;background-color:#7fb03a;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231f3a17' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 8h3l2-3h6l2 3h3v11H4z'/%3E%3Ccircle cx='12' cy='13' r='3.5'/%3E%3C/svg%3E"),linear-gradient(#c9e68a,#7fb03a);background-size:20px 20px,cover;background-repeat:no-repeat;background-position:center}}
.st-key-photo_btn button>*{{display:none!important}}

/* inputs, buttons */
/* fields: white with green outline, like the design */
[data-testid="stTextInput"]>:last-child,[data-testid="stNumberInput"]>:last-child,[data-testid="stSelectbox"]>:last-child{{background:#fff!important;border:2px solid var(--line)!important;border-radius:20px!important;overflow:hidden;box-shadow:none!important}}
[data-testid="stTextInput"]>:last-child *,[data-testid="stNumberInput"]>:last-child *,[data-testid="stSelectbox"]>:last-child *{{background:transparent!important;border-color:transparent!important;box-shadow:none!important}}
[data-testid="stTextInput"]>:last-child input,[data-testid="stNumberInput"]>:last-child input{{color:var(--ink)!important}}
[data-testid="stTextInput"]>:last-child:focus-within,[data-testid="stNumberInput"]>:last-child:focus-within,[data-testid="stSelectbox"]>:last-child:focus-within{{border-color:var(--g)!important;box-shadow:0 0 0 3px rgba(127,176,58,.35)!important}}
[data-testid="stWidgetLabel"] p{{font-weight:500;color:var(--mute)}}
.stButton>button{{font-weight:600;color:var(--ink);background:#fff;border:2px solid var(--line);border-radius:22px;padding:.4rem 1.1rem;transition:transform .1s}}
.stButton>button[kind="primary"]{{background:linear-gradient(#c9e68a,#7fb03a)}}
.stButton>button:hover{{border-color:var(--g);color:var(--ink)}}.stButton>button:active{{transform:scale(.96)}}
[data-testid="stFileUploader"] section{{border:2px dashed var(--line);border-radius:20px;background:#fff}}
.st-key-card_notif{{gap:0}}
.st-key-card_notif>:first-child{{margin-bottom:14px}}
[class*="st-key-tg_"]{{padding:16px 0;border-bottom:2px dotted var(--line)}}
.st-key-tg_week{{border-bottom:0;padding-bottom:6px}}
[class*="st-key-tg_"] [data-testid="stColumn"]:last-child{{display:flex;justify-content:flex-end;align-items:center}}
[class*="st-key-tg_"] [data-testid="stColumn"]:last-child *{{margin:0}}
.tgl{{font-size:1.2rem;font-weight:500;color:var(--ink);line-height:1.3}}
@media(max-width:820px){{.st-key-photo_btn{{top:120px}}}}
</style>""", unsafe_allow_html=True)

ICON = {"user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
        "lock": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
        "bell": '<path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4z"/><path d="M10 21h4"/>'}

def heading(key, text):
    st.markdown(f'<div class="h2"><svg viewBox="0 0 24 24">{ICON[key]}</svg>{text}</div>', unsafe_allow_html=True)

def initials(name):
    return "".join(w[0] for w in name.split()[:2]).upper() or "?"

# ---------- callbacks ----------
def go_back():
    try:
        st.switch_page("settings.py")
    except Exception:
        st.toast("Open settings.py from your app navigation")

def save_profile():
    if not s.p_name.strip():
        st.toast("Enter your full name", icon="⚠️"); return
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s.p_email):
        st.toast("Enter a valid email address", icon="⚠️"); return
    try:
        SAVE_FILE.write_text(json.dumps({k: s[k] for k in DEFAULTS}))
    except Exception:
        pass
    st.toast("Profile saved", icon="✅")

def change_password():
    if not s.p_cur:
        st.toast("Enter your current password", icon="⚠️")
    elif len(s.p_new) < 8:
        st.toast("New password must be at least 8 characters", icon="⚠️")
    elif s.p_new != s.p_conf:
        st.toast("New passwords don't match", icon="⚠️")
    else:
        # TODO: verify and update the password in your login.py / user store
        s.p_cur = s.p_new = s.p_conf = ""
        st.toast("Password updated", icon="✅")

def sign_out():
    for k in list(s.keys()):
        del s[k]
    st.toast("Signed out")

# ---------- header ----------
h1, h2 = st.columns([5, 1.4], vertical_alignment="center")
h1.markdown('<h1 class="t">My Profile</h1>', unsafe_allow_html=True)
h2.button("← Back to settings", on_click=go_back, use_container_width=True)

# ---------- row 1: profile card + personal information ----------
c1, c2 = st.columns([4, 8], gap="medium")
with c1:
    with st.container(key="card_who"):
        photo = None
        try:
            if AVATAR.exists():
                photo = "data:image/png;base64," + base64.b64encode(AVATAR.read_bytes()).decode()
        except Exception:
            pass
        style = f"background-image:url({photo})" if photo else ""
        st.markdown(f"""<div class="who"><div class="av" style="{style}">{"" if photo else initials(s.p_name)}</div>
<div class="n">{s.p_name}</div><div class="e">{s.p_email}</div><span class="badge">Garden owner</span>
<div class="stats"><div><b>3</b><span>Zones</span></div><div><b>1</b><span>Device</span></div><div><b>2024</b><span>Member since</span></div></div></div>""", unsafe_allow_html=True)
        with st.container(key="photo_btn"):
            with st.popover("Change photo"):
                up = st.file_uploader("Upload a photo (max 3 MB)", type=["png", "jpg", "jpeg"], key="p_photo")
                if up is not None and s.get("p_photo_done") != up.file_id:
                    if up.size > 3_000_000:
                        st.toast("Choose a photo under 3 MB", icon="⚠️")
                    else:
                        try:
                            AVATAR.parent.mkdir(exist_ok=True)
                            AVATAR.write_bytes(up.getvalue())
                            s.p_photo_done = up.file_id
                            st.rerun()
                        except Exception:
                            st.toast("Couldn't save the photo", icon="⚠️")
with c2:
    with st.container(key="card_info"):
        heading("user", "Personal Information")
        a, b = st.columns(2)
        a.text_input("Full name", key="p_name")
        b.text_input("Email", key="p_email")
        c, d = st.columns(2)
        c.text_input("Phone", key="p_phone")
        d.text_input("City", key="p_city")
        _, btn = st.columns([3, 1.4])
        btn.button("Save changes", type="primary", on_click=save_profile, use_container_width=True)

# ---------- row 2: password + notifications ----------
n1, n2 = st.columns(2, gap="medium")
with n1:
    with st.container(key="card_sec"):
        heading("lock", "Password")
        st.text_input("Current password", type="password", key="p_cur")
        st.text_input("New password", type="password", key="p_new")
        st.text_input("Confirm new password", type="password", key="p_conf")
        st.button("Update password", type="primary", on_click=change_password, use_container_width=True)
with n2:
    with st.container(key="card_notif"):
        heading("bell", "Notifications")
        for tid, label, key in (("dry", "Soil is too dry", "p_alert_dry"),
                                ("batt", "Battery below 20%", "p_alert_batt"),
                                ("rain", "Rain skips a watering", "p_alert_rain"),
                                ("week", "Weekly garden summary", "p_weekly")):
            with st.container(key=f"tg_{tid}"):
                t1, t2 = st.columns([5, 1], vertical_alignment="center")
                t1.markdown(f'<span class="tgl">{label}</span>', unsafe_allow_html=True)
                t2.toggle(label, key=key, label_visibility="collapsed")

# ---------- footer ----------
_, so = st.columns([6, 1.6])
so.button("Sign out", on_click=sign_out, use_container_width=True)