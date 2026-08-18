import streamlit as st
import os
import random

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="About | FloraPulse",
    page_icon="🌱",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────
# CSS INJECTION — fonts, colors, cards, buttons, animations
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&family=Comfortaa:wght@300;400;500;600;700&display=swap');

/* ── CSS Variables ── */
:root {
    --sage-green: #5F8D4E;
    --sage-green-light: #7BAF6A;
    --sage-green-dark: #4A7340;
    --cream: #FFFDF7;
    --soft-blush: #F5E6D3;
    --warm-gold: #D4AF37;
    --pastel-blue: #A8D5E2;
    --text-dark: #2C3E2D;
    --text-muted: #5A6B5C;
    --card-shadow: 0 4px 20px rgba(95, 141, 78, 0.12);
    --card-hover-shadow: 0 8px 32px rgba(95, 141, 78, 0.22);
}

/* ── Global overrides ── */
.stApp {
    background: linear-gradient(180deg, var(--cream) 0%, #F0F7EC 40%, var(--cream) 100%) !important;
}

/* Hide default Streamlit header & footer */
header[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Typography ── */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Quicksand', sans-serif !important;
    color: var(--text-dark) !important;
}

p, span, li, div,
.stMarkdown p, .stMarkdown span, .stMarkdown li {
    font-family: 'Comfortaa', sans-serif !important;
    color: var(--text-dark) !important;
}

/* ── Ghibli Card ── */
.ghibli-card {
    border-radius: 16px;
    padding: 28px 24px;
    box-shadow: var(--card-shadow);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(95, 141, 78, 0.08);
    position: relative;
    overflow: hidden;
}
.ghibli-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--sage-green), var(--warm-gold), var(--pastel-blue));
    opacity: 0;
    transition: opacity 0.35s ease;
}
.ghibli-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--card-hover-shadow);
}
.ghibli-card:hover::before {
    opacity: 1;
}

/* Card color variants */
.ghibli-card.sage {
    background: linear-gradient(135deg, #EAF2E5 0%, #F5FAF2 100%);
}
.ghibli-card.cream-bg {
    background: linear-gradient(135deg, #FFFDF7 0%, #FFF9EC 100%);
}
.ghibli-card.blush {
    background: linear-gradient(135deg, #FBF0E5 0%, #FFF5ED 100%);
}

/* ── Pill Badge ── */
.pill-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--sage-green), var(--sage-green-light));
    color: #ffffff !important;
    padding: 8px 24px;
    border-radius: 50px;
    font-family: 'Comfortaa', sans-serif !important;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(95, 141, 78, 0.25);
    animation: badgePulse 3s ease-in-out infinite;
}
@keyframes badgePulse {
    0%, 100% { box-shadow: 0 2px 12px rgba(95, 141, 78, 0.25); }
    50% { box-shadow: 0 4px 20px rgba(95, 141, 78, 0.4); }
}

/* ── Hero Section ── */
.hero-section {
    text-align: center;
    padding: 40px 20px 30px;
}
.hero-section h1 {
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, var(--sage-green) 0%, var(--sage-green-dark) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 12px !important;
    line-height: 1.3 !important;
}
.hero-subtitle {
    font-size: 1.15rem !important;
    color: var(--text-muted) !important;
    max-width: 680px;
    margin: 0 auto 30px !important;
    line-height: 1.8 !important;
    font-weight: 400;
}

/* ── Hero Image ── */
.hero-image-wrapper {
    max-width: 600px;
    margin: 0 auto;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 8px 40px rgba(95, 141, 78, 0.18);
    border: 3px solid rgba(95, 141, 78, 0.1);
    transition: transform 0.4s ease, box-shadow 0.4s ease;
}
.hero-image-wrapper:hover {
    transform: scale(1.02);
    box-shadow: 0 12px 48px rgba(95, 141, 78, 0.28);
}
.hero-image-wrapper img {
    width: 100%;
    display: block;
}

/* ── Section Headers ── */
.section-header {
    text-align: center;
    margin: 50px 0 30px;
}
.section-header h2 {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--sage-green) !important;
    margin-bottom: 8px !important;
}
.section-header p {
    color: var(--text-muted) !important;
    font-size: 0.95rem !important;
}

/* ── Story Block ── */
.story-block {
    max-width: 780px;
    margin: 0 auto;
    background: linear-gradient(135deg, #FFFDF7 0%, #F5FAF2 50%, #FFF9EC 100%);
    border-radius: 20px;
    padding: 36px 40px;
    box-shadow: 0 4px 24px rgba(95, 141, 78, 0.1);
    border: 1px solid rgba(95, 141, 78, 0.08);
    position: relative;
}
.story-block::before {
    content: '🌿';
    position: absolute;
    top: -14px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 28px;
    background: var(--cream);
    padding: 0 12px;
}
.story-block p {
    font-size: 1rem !important;
    line-height: 1.9 !important;
    color: var(--text-dark) !important;
    margin-bottom: 16px !important;
}
.story-block p:last-child {
    margin-bottom: 0 !important;
}

/* ── Mission Cards ── */
.mission-emoji {
    font-size: 2.5rem;
    margin-bottom: 12px;
    display: block;
}
.mission-title {
    font-family: 'Quicksand', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: var(--text-dark) !important;
    margin-bottom: 8px !important;
}
.mission-desc {
    font-size: 0.9rem !important;
    color: var(--text-muted) !important;
    line-height: 1.7 !important;
}

/* ── Team Cards ── */
.team-card {
    text-align: center;
}
.team-emoji-avatar {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 auto 16px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
}
.team-emoji-avatar.sage-bg { background: linear-gradient(135deg, #C5E1B5, #A8D5A0); }
.team-emoji-avatar.cream-team-bg { background: linear-gradient(135deg, #FFE8C8, #FFD9A8); }
.team-emoji-avatar.blush-bg { background: linear-gradient(135deg, #F5D5C8, #FCCAB7); }

.team-name {
    font-family: 'Quicksand', sans-serif !important;
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    color: var(--sage-green) !important;
    margin-bottom: 4px !important;
}
.team-title {
    font-size: 0.8rem !important;
    color: var(--warm-gold) !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 14px !important;
}
.team-bio {
    font-size: 0.88rem !important;
    color: var(--text-dark) !important;
    line-height: 1.7 !important;
    margin-bottom: 14px !important;
}
.team-quote {
    font-style: italic;
    font-size: 0.85rem !important;
    color: var(--sage-green) !important;
    padding: 10px 16px;
    border-left: 3px solid var(--warm-gold);
    background: rgba(212, 175, 55, 0.06);
    border-radius: 0 8px 8px 0;
    margin-bottom: 12px !important;
    text-align: left;
}
.team-fun-fact {
    font-size: 0.78rem !important;
    color: var(--text-muted) !important;
    background: rgba(95, 141, 78, 0.06);
    padding: 8px 14px;
    border-radius: 10px;
    display: inline-block;
}

/* ── Tabs Styling ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Comfortaa', sans-serif !important;
    border-radius: 12px;
    padding: 10px 20px;
    background: rgba(95, 141, 78, 0.06);
    border: 1px solid rgba(95, 141, 78, 0.12);
    transition: all 0.3s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(95, 141, 78, 0.12);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--sage-green), var(--sage-green-light)) !important;
    color: white !important;
    border-color: var(--sage-green) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: transparent !important;
}
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

/* ── Vibe Tab Content ── */
.vibe-content {
    background: linear-gradient(135deg, #F5FAF2 0%, #FFFDF7 100%);
    border-radius: 16px;
    padding: 30px 36px;
    margin-top: 16px;
    box-shadow: 0 2px 16px rgba(95, 141, 78, 0.08);
    border: 1px solid rgba(95, 141, 78, 0.06);
    min-height: 120px;
}
.vibe-content p {
    font-size: 1rem !important;
    line-height: 1.9 !important;
}

/* ── Interactive Mood Picker ── */
.mood-result {
    background: linear-gradient(135deg, #EAF2E5 0%, #F5FAF2 50%, #FFFDF7 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-top: 20px;
    box-shadow: 0 4px 20px rgba(95, 141, 78, 0.12);
    border: 1px solid rgba(95, 141, 78, 0.1);
    text-align: center;
}
.mood-result p {
    font-size: 1rem !important;
    line-height: 1.8 !important;
}

/* ── CTA Section ── */
.cta-section {
    text-align: center;
    background: linear-gradient(135deg, #EAF2E5 0%, #F0F7EC 50%, #FFFDF7 100%);
    border-radius: 24px;
    padding: 48px 40px;
    margin: 40px auto;
    max-width: 800px;
    box-shadow: 0 6px 30px rgba(95, 141, 78, 0.14);
    border: 1px solid rgba(95, 141, 78, 0.08);
}
.cta-section h2 {
    font-size: 2rem !important;
    margin-bottom: 16px !important;
}
.cta-section p {
    font-size: 1rem !important;
    line-height: 1.8 !important;
    max-width: 600px;
    margin: 0 auto 28px !important;
    color: var(--text-muted) !important;
}

/* ── Streamlit Button Override ── */
.stButton > button {
    font-family: 'Comfortaa', sans-serif !important;
    background: linear-gradient(135deg, var(--sage-green), var(--sage-green-light)) !important;
    color: var(--cream) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 32px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    box-shadow: 0 3px 12px rgba(95, 141, 78, 0.25) !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.3px;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(95, 141, 78, 0.35) !important;
    background: linear-gradient(135deg, var(--sage-green-light), var(--sage-green)) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Footer ── */
.footer-section {
    text-align: center;
    padding: 30px 20px 20px;
    margin-top: 40px;
    border-top: 2px solid rgba(95, 141, 78, 0.15);
    background: linear-gradient(180deg, transparent, rgba(240, 247, 236, 0.5));
}
.footer-main {
    font-family: 'Comfortaa', sans-serif !important;
    font-size: 1rem !important;
    color: var(--text-dark) !important;
    margin-bottom: 8px !important;
}
.footer-credits {
    font-family: 'Comfortaa', sans-serif !important;
    font-size: 0.78rem !important;
    color: var(--text-muted) !important;
    margin-bottom: 12px !important;
}
.footer-icons {
    font-size: 1.3rem;
    letter-spacing: 12px;
}

/* ── Decorative Floating Leaves ── */
@keyframes floatLeaf {
    0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.6; }
    25% { transform: translateY(-8px) rotate(5deg); opacity: 0.8; }
    50% { transform: translateY(-4px) rotate(-3deg); opacity: 0.7; }
    75% { transform: translateY(-10px) rotate(4deg); opacity: 0.9; }
}
.floating-leaf {
    position: fixed;
    font-size: 1.2rem;
    animation: floatLeaf 6s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
}
.leaf-1 { top: 15%; left: 3%; animation-delay: 0s; }
.leaf-2 { top: 35%; right: 4%; animation-delay: 1.5s; }
.leaf-3 { top: 60%; left: 5%; animation-delay: 3s; }
.leaf-4 { top: 80%; right: 3%; animation-delay: 4.5s; }

/* ── Radio Button Styling ── */
.stRadio > div {
    background: rgba(95, 141, 78, 0.04);
    border-radius: 16px;
    padding: 16px 20px;
}
.stRadio label {
    font-family: 'Comfortaa', sans-serif !important;
}

/* ── Divider ── */
.gentle-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--sage-green), var(--warm-gold), var(--pastel-blue), transparent);
    border: none;
    margin: 50px auto;
    max-width: 400px;
    border-radius: 2px;
    opacity: 0.4;
}

/* ── Responsive ── */
@media (max-width: 768px) {
    .hero-section h1 {
        font-size: 1.8rem !important;
    }
    .hero-subtitle {
        font-size: 0.95rem !important;
    }
    .story-block {
        padding: 24px 20px;
    }
    .cta-section {
        padding: 32px 20px;
    }
    .ghibli-card {
        padding: 20px 16px;
    }
    .section-header h2 {
        font-size: 1.5rem !important;
    }
    .vibe-content {
        padding: 20px;
    }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# FLOATING DECORATIVE LEAVES
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="floating-leaf leaf-1">🍃</div>
<div class="floating-leaf leaf-2">🌿</div>
<div class="floating-leaf leaf-3">☘️</div>
<div class="floating-leaf leaf-4">🍂</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# 1. HERO SECTION
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-section">
    <div class="pill-badge">🍃 low-stress plant parenting • 100% cozy vibes only ✨</div>
    <h1>Welcome to Our Little Green Corner 🌱</h1>
    <p class="hero-subtitle">
        Where your plant babies get main character energy, zero guilt,
        and all the love they deserve.
    </p>
</div>
""", unsafe_allow_html=True)

# Hero illustration
hero_img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "hero_illustration.jpg")
if os.path.exists(hero_img_path):
    col_left, col_img, col_right = st.columns([1, 3, 1])
    with col_img:
        st.markdown('<div class="hero-image-wrapper">', unsafe_allow_html=True)
        st.image(hero_img_path, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="gentle-divider"></div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# 2. "WHY THIS EXISTS" — Origin Story
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <h2>Our Little Story 💚</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="story-block">
    <p>
        It all started at 2 AM during a motivation burst. We bought 12 houseplants.
        By day 2, we'd killed 3. By day 5, the fern fainted dramatically. Sound familiar?
    </p>
    <p>
        We realized: plant care shouldn't feel like anxiety. It should feel like self-care.
        Like that cozy feeling of watering your plants with a warm cup of tea, knowing
        they're thriving not just surviving.
    </p>
    <p>
        So we built <strong>FloraPulse</strong> to turn guesswork into peaceful daily rituals.
        No guilt. No dead ferns. Just plants that love you back. 🌿
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="gentle-divider"></div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# 3. MISSION — Cozy Green Manifesto
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <h2>What We Believe In 🌿</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="ghibli-card sage">
        <span class="mission-emoji">🪴</span>
        <div class="mission-title">Zero-Guilt Plant Parenting</div>
        <div class="mission-desc">
            No judgment, only second chances and thriving leaves.
            Every plant deserves a comeback story.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="ghibli-card cream-bg">
        <span class="mission-emoji">🍵</span>
        <div class="mission-title">Micro-Dosing Peace</div>
        <div class="mission-desc">
            Bringing the calming rhythm of a countryside morning
            into your modern room. One watering ritual at a time.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="ghibli-card blush">
        <span class="mission-emoji">🌍</span>
        <div class="mission-title">Mindful & Sustainable Living</div>
        <div class="mission-desc">
            Happy plants, cleaner indoor air, and respect for
            nature's gentle pace. Small acts, big impact.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="gentle-divider"></div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# 4. "WHO IS IT FOR?" — The Vibe Tribe
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <h2>Which Plant Parent Are You? ✨</h2>
    <p>Find your vibe. No wrong answers here.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🌿 The Redemption Arc",
    "🎨 The Aesthete",
    "🎧 The Lo-Fi Dreamer",
    "🏢 The Busy Hustler",
])

with tab1:
    st.markdown("""
    <div class="vibe-content">
        <p>
            <strong>🌿 The Serial Plant Killer on a Redemption Arc</strong>
        </p>
        <p>
            You mean well, but you forget. Your track record: brown leaves, withered stems,
            guilty vibes. We're here to break that cycle. Second chances only. 💚
        </p>
        <p>
            FloraPulse remembers so you don't have to. Think of it as a gentle nudge from your
            plant bestie who actually knows what they're doing.
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="vibe-content">
        <p>
            <strong>🎨 The Aesthetic Room Decorator</strong>
        </p>
        <p>
            Your space is a Pinterest board, and your plants are the main character. You want
            them thriving AND looking like they walked out of a magazine. We got the assist.
        </p>
        <p>
            Because nothing kills the aesthetic faster than a yellowing leaf. Let's keep your
            green babies looking their absolute best. 📸
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="vibe-content">
        <p>
            <strong>🎧 The Lo-Fi & Rainy Day Dreamer</strong>
        </p>
        <p>
            Plant care is your comfort ritual. Watering feels like meditation. You want gentle
            reminders, real-time vibes, and the satisfaction of watching your green babies glow up.
        </p>
        <p>
            FloraPulse turns plant care into the peaceful moment you deserve.
            Put on those lo-fi beats, grab your watering can, and enjoy. 🎵
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div class="vibe-content">
        <p>
            <strong>🏢 The Busy Hustler with 99 Tabs Open</strong>
        </p>
        <p>
            You love your plants but forget they exist. You're juggling deadlines, meetings,
            and life and somehow your pothos is supposed to survive too?
        </p>
        <p>
            We handle the reminders, the weather checks, and the peace of mind.
            Your plants won't dry out while you're grinding. Promise. 💪
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="gentle-divider"></div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# 5. TEAM INTRODUCTION — The Garden Guardians
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <h2>Meet the Plant Whisperers Behind FloraPulse 🌱</h2>
    <p>Three friends, too many plants, and one shared dream.</p>
</div>
""", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3, gap="medium")

with t1:
    st.markdown("""
    <div class="ghibli-card sage team-card">
        <div class="team-emoji-avatar sage-bg">🎨</div>
        <div class="team-name">Pranjali</div>
        <div class="team-title">Chief Vibe Curator & Backend Orchestrator</div>
        <div class="team-bio">
            Pranjali turns chaos into elegant code and vibes into magic.
            When not debugging, she's teaching her pothos the art of thriving.
            <br><em>Emotional support plant: Monstera 'Bartholomew' 🪴</em>
        </div>
        <div class="team-quote">
            "Good code is like a well-watered plant clean, purposeful, and thriving."
        </div>
        <div class="team-fun-fact">
            😤 Pet peeve: people pouring cold coffee into plant pots
        </div>
    </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown("""
    <div class="ghibli-card cream-bg team-card">
        <div class="team-emoji-avatar cream-team-bg">🌿</div>
        <div class="team-name">Shreeya</div>
        <div class="team-title">Lead Chaos Wrangler & Greenery Aestheticist</div>
        <div class="team-bio">
            Shreeya believes plants are tiny therapists. She designs systems
            that make sense to humans (and plants). Found frequently talking to succulents.
            <br><em>Emotional support plant: String of pearls 'Luna' 📿</em>
        </div>
        <div class="team-quote">
            "Every plant deserves to feel loved, even the dramatic ones."
        </div>
        <div class="team-fun-fact">
            😤 Pet peeve: plant names that are just numbers
        </div>
    </div>
    """, unsafe_allow_html=True)

with t3:
    st.markdown("""
    <div class="ghibli-card blush team-card">
        <div class="team-emoji-avatar blush-bg">✨</div>
        <div class="team-name">Isheka</div>
        <div class="team-title">Senior Overthinker & Pixel Florist</div>
        <div class="team-bio">
            Isheka translates plant dreams into pixels. She obsesses over
            experience, plant health, and the perfect shade of green.
            Her room looks like a secret garden.
            <br><em>Emotional support plant: Calathea 'Whisper' 🌸</em>
        </div>
        <div class="team-quote">
            "A good interface is like a plant-parent intuitive, responsive, and always listening."
        </div>
        <div class="team-fun-fact">
            😤 Pet peeve: interfaces that don't have dark mode
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="gentle-divider"></div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# 6. INTERACTIVE COZY ELEMENT — Plant Energy Picker
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <h2>What's Your Plant Energy Today? 🌱✨</h2>
    <p>Pick a vibe and receive your plant blessing.</p>
</div>
""", unsafe_allow_html=True)

# Mood options and responses
mood_responses = {
    "Thriving Energy ✨": {
        "emoji": "✨🌱💚",
        "blessing": (
            "**✨ Your plant energy today: Unstoppable!**\n\n"
            "Keep it up! Your greenery is giving main character energy. "
            "Water when the soil feels dry to the touch. "
            "Recommended vibe: play lo-fi beats while watering 🎧\n\n"
            "*Lucky plant: Monstera because you're thriving and you know it.*"
        ),
    },
    "Needs Water Vibes 💧": {
        "emoji": "💧🪴💙",
        "blessing": (
            "**💧 Your plant energy today: Time for some TLC.**\n\n"
            "You and your plants could both use a nice long drink of water. "
            "Take a deep breath, fill that watering can, and give yourself "
            "permission to slow down today.\n\n"
            "*Lucky plant: Peace Lily she gets it, she's dramatic too.*"
        ),
    },
    "Recovery Arc 🌿": {
        "emoji": "🌿🩹💪",
        "blessing": (
            "**🌿 Your plant energy today: Bounce-back mode activated!**\n\n"
            "Some leaves fell, but new ones are coming. You're in your "
            "growth era. Be patient with yourself and your plants — "
            "healing isn't linear, and neither is root growth.\n\n"
            "*Lucky plant: Pothos literally impossible to kill. Your spirit animal.*"
        ),
    },
    "Sunday Lo-Fi Feels 🎧": {
        "emoji": "🎧☕🍃",
        "blessing": (
            "**🎧 Your plant energy today: Cozy and content.**\n\n"
            "Today is about gentle rhythms. Mist your ferns, "
            "rearrange your plant shelf, and pretend you live in a "
            "Ghibli countryside cottage. You've earned this peace.\n\n"
            "*Lucky plant: Boston Fern soft, whimsical, main character vibes.*"
        ),
    },
}

# Center the radio in a narrower column
pick_left, pick_center, pick_right = st.columns([1, 2, 1])
with pick_center:
    mood = st.radio(
        "Choose your vibe:",
        list(mood_responses.keys()),
        index=None,
        label_visibility="collapsed",
    )

if mood:
    response = mood_responses[mood]
    st.markdown(f"""
    <div class="mood-result">
        <p style="font-size: 2rem !important; margin-bottom: 12px !important;">{response["emoji"]}</p>
    </div>
    """, unsafe_allow_html=True)
    st.success(response["blessing"])

    # Fun confetti-like CSS animation on selection
    confetti_emojis = ["🌿", "🍃", "🌱", "✨", "💚", "🪴", "☘️", "🌸"]
    confetti_divs = []
    for i, emoji in enumerate(confetti_emojis):
        left = random.randint(5, 95)
        delay = round(random.uniform(0, 2), 1)
        duration = round(random.uniform(2, 4), 1)
        confetti_divs.append(
            f'<div style="position:fixed;top:-20px;left:{left}%;font-size:1.5rem;z-index:9999;animation:confettiFall {duration}s ease-in {delay}s 1 forwards;pointer-events:none;">{emoji}</div>'
        )
    confetti_joined = "".join(confetti_divs)
    st.markdown(
        "<style>@keyframes confettiFall{0%{transform:translateY(0) rotate(0deg);opacity:1}100%{transform:translateY(100vh) rotate(720deg);opacity:0}}</style>"
        + confetti_joined,
        unsafe_allow_html=True,
    )

st.markdown('<div class="gentle-divider"></div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# 7. CALL TO ACTION
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="cta-section">
    <h2>Ready to Grow Smarter? 💚</h2>
    <p>
        Join thousands of plant parents who've ditched the guilt and embraced thriving.
        Your plants deserve better. <em>You</em> deserve better.
        Let's make plant care feel like self-care.
    </p>
</div>
""", unsafe_allow_html=True)

cta_left, cta_spacer, cta_right = st.columns([2, 1, 2])

with cta_left:
    if st.button("🌿  View Live Dashboard", key="btn_dashboard", use_container_width=True):
        try:
            st.switch_page("pages/1_Dashboard.py")
        except Exception:
            st.info("Dashboard page coming soon! 🚀")

with cta_right:
    if st.button("🌸  Check Out Plant Info", key="btn_plantinfo", use_container_width=True):
        try:
            st.switch_page("pages/2_Plant_UI.py")
        except Exception:
            st.info("Plant Info page coming soon! 🌱")


# ═════════════════════════════════════════════════════════════
# 8. FOOTER
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer-section">
    <p class="footer-main">Brewed with matcha, lo-fi beats, and warm sunshine 🍵✨</p>
    <p class="footer-credits">FloraPulse © 2026 &nbsp;|&nbsp; Made with 💚 by Pranjali, Shreeya & Isheka</p>
    <div class="footer-icons">🌿 🎵 ☀️ 💚</div>
</div>
""", unsafe_allow_html=True)
