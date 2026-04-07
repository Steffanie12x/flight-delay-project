# Streamlit-Bibliothek importieren (Web-App-Framework)
import streamlit as st

# Gemeinsame Navbar-Funktion importieren
from utils.navbar import show_navbar

# ── Seitenkonfiguration ───────────────────────────────────────────────────────
# Setzt Titel, Icon, Layout und Sidebar-Status der App
st.set_page_config(
    page_title="Flight Delay – ZRH",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Navbar anzeigen ───────────────────────────────────────────────────────────
# Zeigt die Navigationsleiste mit Flight Delay · ZRH und den Seiten-Links
show_navbar()

# ── CSS-Ausnahme: Hero-Text weiß ─────────────────────────────────────────────
# Überschreibt die globale Schwarz-Regel speziell für den Hero-Bereich
st.markdown("""
<style>
.hero-text h1, .hero-text p, .hero-text div, .hero-text span {
    color: #ffffff !important;
}
.hero-text .hero-label {
    color: #60A5FA !important;
}

/* Dialog-Fenster: weißer Hintergrund, schwarze Schrift */
[data-testid="stDialog"] > div,
[data-testid="stDialog"] [role="dialog"] {
    background-color: #ffffff !important;
}
[data-testid="stDialog"] [role="dialog"] *,
[data-testid="stDialog"] p,
[data-testid="stDialog"] h1,
[data-testid="stDialog"] h2,
[data-testid="stDialog"] h3,
[data-testid="stDialog"] li,
[data-testid="stDialog"] label,
[data-testid="stDialog"] span,
[data-testid="stDialog"] div {
    color: #111111 !important;
    background-color: transparent !important;
}
/* Input-Felder und Dropdowns im Dialog */
[data-testid="stDialog"] input,
[data-testid="stDialog"] textarea,
[data-testid="stDialog"] select,
[data-testid="stDialog"] [data-baseweb="select"] *,
[data-testid="stDialog"] [data-baseweb="input"] *,
[data-testid="stDialog"] [data-testid="stSelectbox"] *,
[data-testid="stDialog"] [data-testid="stTextInput"] * {
    background-color: #f9fafb !important;
    color: #111111 !important;
    border-color: #d1d5db !important;
}
/* Dropdown-Liste */
[data-baseweb="popover"] *,
[data-baseweb="menu"] * {
    background-color: #ffffff !important;
    color: #111111 !important;
}

/* Buttons: weißer Hintergrund, schwarze Schrift, grauer Rahmen */
[data-testid="stButton"] button {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 1px solid #d1d5db !important;
    font-weight: 600 !important;
}
[data-testid="stButton"] button:hover {
    background-color: #f3f4f6 !important;
    border-color: #9ca3af !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero-Sektion mit Hintergrundbild ─────────────────────────────────────────
# Zeigt ein Flugzeug-Bild über die volle Breite ohne Rahmen
import base64, pathlib
_hero_b64 = base64.b64encode(pathlib.Path("hero.png").read_bytes()).decode()
_hero_src = f"data:image/png;base64,{_hero_b64}"
st.markdown(f"""
<div style="
    position: relative;
    overflow: hidden;
    margin: -1rem -4rem 2.5rem -4rem;
    height: 340px;
">
    <!-- Hintergrundbild -->
    <img
        src="{_hero_src}"
        style="
            position: absolute; top: 0; left: 0;
            width: 100%; height: 100%;
            object-fit: cover;
            object-position: center 40%;
        "
    />
    <!-- Dunkler Overlay -->
    <div style="
        position: absolute; top: 0; left: 0;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, rgba(5,10,30,0.45) 40%, rgba(5,10,30,0.1) 100%);
    "></div>
    <!-- Text darüber -->
    <div class="hero-text" style="
        position: relative; z-index: 2;
        padding: 3rem 3rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        color: #ffffff;
    ">
        <div class="hero-label" style="font-size:0.7rem; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:0.75rem;">
            Zurich Airport · ZRH
        </div>
        <h1 style="font-size:3rem; font-weight:700; color:#ffffff; margin:0 0 0.75rem; line-height:1.1; letter-spacing:-0.02em;">
            Flight Delay
        </h1>
        <p style="color:#ffffff; font-size:1rem; margin:0 0 1.5rem; max-width:480px; line-height:1.6;">
            Analyze delay patterns from Zurich — by airline, time and destination.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Problem Statement ─────────────────────────────────────────────────────────
# Zeigt den Projektzweck als kursives Zitat mit blauem linken Rand
st.markdown("""
<div style="
    background: #f8f9fa;
    border-left: 3px solid #3B82F6;
    padding: 1rem 1.25rem;
    margin-bottom: 2rem;
    color: #333333;
    font-size: 0.95rem;
    line-height: 1.7;
    border-radius: 0 8px 8px 0;
">
    <em>„Passengers often do not know how risky a planned flight is in terms of delays.
    Our website helps them understand historical delay patterns and estimates the delay
    probability for a specific flight from Zurich Airport."</em>
</div>
""", unsafe_allow_html=True)

# ── Use Cases ─────────────────────────────────────────────────────────────────
# Listet drei konkrete Anwendungsfälle für das Tool auf
st.markdown("""
<div style="
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 2rem;
">
    <div style="font-size:0.7rem; color:#888888; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.75rem;">
        Why this tool?
    </div>
    <div style="color:#333333; font-size:0.9rem; line-height:2.1;">
        ✈ &nbsp; The Friday flight to Mallorca at 08:00 is often delayed — consider booking a different day.<br>
        🔗 &nbsp; Got a connecting flight? Check the risk and plan enough buffer time.<br>
        📊 &nbsp; Which airline is the most reliable on your route?
    </div>
</div>
""", unsafe_allow_html=True)

# ── 3 Seiten-Cards ────────────────────────────────────────────────────────────
# Erstellt drei gleichbreite Spalten für die Navigations-Karten
col1, col2, col3 = st.columns(3, gap="medium")

# Card 1: Dashboard-Seite (blauer Akzent)
with col1:
    st.markdown("""
    <div style="
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-top: 2px solid #3B82F6;
        border-radius: 0 0 12px 12px;
        padding: 1.25rem;
        height: 130px;
    ">
        <div style="font-size:0.7rem; color:#3B82F6; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem;">
            01 — Dashboard
        </div>
        <div style="color:#111111; font-weight:600; margin-bottom:0.4rem;">Überblick & Key Metrics</div>
        <div style="color:#666666; font-size:0.82rem; line-height:1.5;">
            Verspätungsrate, beste & schlechteste Airlines, Delay nach Monat und Wochentag.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Card 2: Analysis-Seite (lila Akzent)
with col2:
    st.markdown("""
    <div style="
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-top: 2px solid #6366F1;
        border-radius: 0 0 12px 12px;
        padding: 1.25rem;
        height: 130px;
    ">
        <div style="font-size:0.7rem; color:#6366F1; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem;">
            02 — Analysis
        </div>
        <div style="color:#111111; font-weight:600; margin-bottom:0.4rem;">Interaktive Diagramme</div>
        <div style="color:#666666; font-size:0.82rem; line-height:1.5;">
            Delay nach Airline, Uhrzeit, Wochentag, Destination — filterbar und interaktiv.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Card 3: Prediction-Seite (grüner Akzent)
with col3:
    st.markdown("""
    <div style="
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-top: 2px solid #10B981;
        border-radius: 0 0 12px 12px;
        padding: 1.25rem;
        height: 130px;
    ">
        <div style="font-size:0.7rem; color:#10B981; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem;">
            03 — Prediction
        </div>
        <div style="color:#111111; font-weight:600; margin-bottom:0.4rem;">ML-Prognose</div>
        <div style="color:#666666; font-size:0.82rem; line-height:1.5;">
            Airline, Destination und Datum eingeben — Delay-Wahrscheinlichkeit berechnen.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── About Us & Stay Informed ──────────────────────────────────────────────────
# Zwei klickbare Buttons zentriert, öffnen jeweils ein Modal-Fenster

@st.dialog("About Us")
def show_about():
    # Informationen über das Projektteam und das Projekt
    st.markdown("""
    **Flight Delay ZRH** is a student project developed at the University of St. Gallen.

    Our goal is to make flight delay data from Zurich Airport accessible and understandable —
    helping travelers make smarter booking decisions.

    ---
    **Team**
    - Placeholder Name · Data & Backend
    - Placeholder Name · Analysis & Visualization
    - Placeholder Name · ML & Prediction

    ---
    **Data Source**
    Historical flight data from Zurich Airport (ZRH), combined with weather data from Open-Meteo.
    """)

@st.dialog("Stay Informed")
def show_newsletter():
    # Formular zur Newsletter-Anmeldung für Verspätungsbenachrichtigungen
    st.markdown("Get notified about major delays at Zurich Airport directly in your inbox.")
    st.markdown("<br>", unsafe_allow_html=True)
    email = st.text_input("Your email address", placeholder="you@example.com")
    st.selectbox("Airline you fly most often (optional)", [
        "— no preference —", "Swiss", "Lufthansa", "easyJet", "LATAM", "British Airways",
        "Air France", "KLM", "Iberia", "Turkish Airlines", "Other"
    ])
    if st.button("Subscribe", type="primary"):
        if email and "@" in email:
            st.success(f"Thanks! We'll notify {email} about major delays.")
        else:
            st.error("Please enter a valid email address.")

# Abstand vor den Buttons
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div style='border-top:1px solid #e0e0e0; margin-bottom:2rem;'></div>", unsafe_allow_html=True)

# Buttons zentriert in der Mitte der Seite
_, btn_col1, btn_col2, _ = st.columns([2, 1, 1, 2])

with btn_col1:
    if st.button("About Us", use_container_width=True):
        show_about()

with btn_col2:
    if st.button("Stay Informed", use_container_width=True):
        show_newsletter()

# ── Footer ────────────────────────────────────────────────────────────────────
# Zeigt Projektinfo zentriert am Seitenende
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #e0e0e0; padding-top:1rem; text-align:center;
    color:#aaaaaa; font-size:0.72rem;">
    CS Project · University of St. Gallen · Zurich Airport Flight Data · 2026
</div>
""", unsafe_allow_html=True)
