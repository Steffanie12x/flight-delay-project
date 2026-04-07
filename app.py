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
</style>
""", unsafe_allow_html=True)

# ── Hero-Sektion mit Hintergrundbild ─────────────────────────────────────────
# Zeigt ein Flugzeug-Bild (Unsplash) über die volle Breite ohne Rahmen
st.markdown("""
<div style="
    position: relative;
    overflow: hidden;
    margin: -1rem -4rem 2.5rem -4rem;
    height: 340px;
">
    <!-- Hintergrundbild -->
    <img
        src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80"
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
        background: linear-gradient(90deg, rgba(5,10,30,0.92) 40%, rgba(5,10,30,0.5) 100%);
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
            Analysiere Verspätungsmuster ab Zürich — nach Airline, Uhrzeit und Destination.
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
        Warum dieses Tool?
    </div>
    <div style="color:#333333; font-size:0.9rem; line-height:2.1;">
        ✈ &nbsp; Der Freitagsflug nach Mallorca um 08:00 ist oft verspätet — lieber einen anderen Tag buchen.<br>
        🔗 &nbsp; Anschlussflug geplant? Prüfe das Risiko und plane genug Puffer ein.<br>
        📊 &nbsp; Welche Airline ist am zuverlässigsten auf deiner Strecke?
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

# ── Footer ────────────────────────────────────────────────────────────────────
# Fügt Abstand ein und zeigt Projektinfo zentriert am Seitenende
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #e0e0e0; padding-top:1rem; text-align:center;
    color:#aaaaaa; font-size:0.72rem;">
    CS Project · University of St. Gallen · Zurich Airport Flight Data · 2026
</div>
""", unsafe_allow_html=True)
