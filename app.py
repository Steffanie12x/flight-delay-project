# Streamlit-Bibliothek importieren (Web-App-Framework)
import streamlit as st
import plotly.graph_objects as go

# Gemeinsame Navbar-Funktion importieren
from utils.navbar import show_navbar

# Aggregierte Delay-Daten für die Charts importieren
from utils.dashboard_data import get_delay_by_hour, get_delay_by_weekday, get_delay_by_airline

# ── Seitenkonfiguration ───────────────────────────────────────────────────────
# Setzt Titel, Icon, Layout und Sidebar-Status der App
st.set_page_config(
    page_title="Flight Delay – USA",
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
            ATL · ORD · JFK · LAX · DEN
        </div>
        <h1 style="font-size:3rem; font-weight:700; color:#ffffff; margin:0 0 0.75rem; line-height:1.1; letter-spacing:-0.02em;">
            Flight Delay
        </h1>
        <p style="color:#ffffff; font-size:1rem; margin:0 0 1.5rem; max-width:480px; line-height:1.6;">
            Analyze delay patterns from the 5 busiest US airports — by airline, time and destination.
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
    probability for a specific flight from one of the 5 busiest US airports."</em>
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


# ── About Us & Stay Informed ──────────────────────────────────────────────────
# Zwei klickbare Buttons zentriert, öffnen jeweils ein Modal-Fenster

@st.dialog("About Us")
def show_about():
    # Informationen über das Projektteam und das Projekt
    st.markdown("""
    **Flight Delay USA** is a student project developed at the University of St. Gallen.

    Our goal is to make flight delay data from the 5 busiest US airports (ATL, ORD, JFK, LAX, DEN) accessible and understandable —
    helping travelers make smarter booking decisions.

    ---
    **Team**
    - Placeholder Name · Data & Backend
    - Placeholder Name · Analysis & Visualization
    - Placeholder Name · ML & Prediction

    ---
    **Data Source**
    Historical flight data from ATL, ORD, JFK, LAX and DEN, combined with weather data from Open-Meteo.
    """)

@st.dialog("Stay Informed")
def show_newsletter():
    # Formular zur Newsletter-Anmeldung für Verspätungsbenachrichtigungen
    st.markdown("Get notified about major delays at US airports directly in your inbox.")
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

# ── DELAY CHARTS ─────────────────────────────────────────────────────────────
# Drei interaktive Diagramme basierend auf 2015 BTS-Flugdaten
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div style='border-top:1px solid #e0e0e0; margin-bottom:2rem;'></div>", unsafe_allow_html=True)

# Daten laden
df_hour    = get_delay_by_hour()
df_weekday = get_delay_by_weekday()
df_airline = get_delay_by_airline()

# Gemeinsame Farben und Stil-Einstellungen für alle Charts
COLOR_LINE = "#3B82F6"
COLOR_BAR  = "#6366F1"
COLOR_GRID = "#f0f0f0"
LAYOUT_BASE = dict(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font=dict(family="sans-serif", size=12, color="#333333"),
)

# ── Chart 1: Verspätungen nach Tageszeit ──────────────────────────────────────
st.subheader("Delays by Time of Day")
st.caption("Share of flights delayed > 15 min — delays accumulate over the course of the day.")

# Stundenbeschriftungen für die X-Achse
hour_labels = [f"{h:02d}:00" for h in df_hour["hour"]]

fig_hour = go.Figure()
# Gefüllte Fläche unter der Kurve für bessere Lesbarkeit
fig_hour.add_trace(go.Scatter(
    x=hour_labels,
    y=df_hour["delay_pct"],
    mode="lines",
    line=dict(color=COLOR_LINE, width=2.5, shape="spline"),
    fill="tozeroy",
    fillcolor="rgba(59,130,246,0.12)",
    hovertemplate="%{x}: %{y}%<extra></extra>",
))
fig_hour.update_layout(
    **LAYOUT_BASE,
    height=300,
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(
        title="Departure Hour",
        gridcolor=COLOR_GRID,
        tickvals=hour_labels[::2],   # Nur jede zweite Stunde anzeigen
        ticktext=hour_labels[::2],
    ),
    yaxis=dict(title="% Flights Delayed", gridcolor=COLOR_GRID, ticksuffix="%", range=[0, 45]),
    showlegend=False,
)
st.plotly_chart(fig_hour, use_container_width=True)

st.markdown("---")

# ── Chart 2: Verspätungen nach Wochentag ──────────────────────────────────────
st.subheader("Delays by Day of Week")
st.caption("Friday has the highest delay rate — busiest travel day with cumulative delays.")

# Freitag rot hervorheben, alle anderen lila
bar_colors_weekday = ["#EF4444" if d == "Fri" else COLOR_BAR for d in df_weekday["day"]]

fig_weekday = go.Figure()
fig_weekday.add_trace(go.Bar(
    x=df_weekday["day"],
    y=df_weekday["delay_pct"],
    marker_color=bar_colors_weekday,
    marker_line_width=0,
    text=[f"{v}%" for v in df_weekday["delay_pct"]],
    textposition="outside",
    hovertemplate="%{x}: %{y}%<extra></extra>",
))
fig_weekday.update_layout(
    **LAYOUT_BASE,
    height=300,
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(title="Day of Week", gridcolor=COLOR_GRID),
    yaxis=dict(title="% Flights Delayed", gridcolor=COLOR_GRID, ticksuffix="%", range=[0, 30]),
    showlegend=False,
    bargap=0.35,
)
st.plotly_chart(fig_weekday, use_container_width=True)

st.markdown("---")

# ── Chart 3: Verspätungen nach Airline ────────────────────────────────────────
st.subheader("Delays by Airline")
st.caption("Sorted from most to least punctual — green < 16%, yellow 16–22%, red > 22%.")

# Farbe je nach Verspätungsrate: grün → gelb → rot
def airline_color(pct):
    if pct < 16:   return "#10B981"
    elif pct < 22: return "#F59E0B"
    else:          return "#EF4444"

fig_airline = go.Figure()
fig_airline.add_trace(go.Bar(
    x=df_airline["delay_pct"],
    y=df_airline["airline"],
    orientation="h",
    marker_color=[airline_color(p) for p in df_airline["delay_pct"]],
    marker_line_width=0,
    text=[f"{v}%" for v in df_airline["delay_pct"]],
    textposition="outside",
    hovertemplate="%{y}: %{x}%<extra></extra>",
))
fig_airline.update_layout(
    **LAYOUT_BASE,
    height=420,
    margin=dict(l=0, r=50, t=30, b=0),
    xaxis=dict(title="% Flights Delayed", gridcolor=COLOR_GRID, ticksuffix="%", range=[0, 34]),
    yaxis=dict(title="", gridcolor=COLOR_GRID, automargin=True),
    showlegend=False,
    bargap=0.25,
)
st.plotly_chart(fig_airline, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
# Zeigt Projektinfo zentriert am Seitenende
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #e0e0e0; padding-top:1rem; text-align:center;
    color:#aaaaaa; font-size:0.72rem;">
    CS Project · University of St. Gallen · US Airport Flight Data · 2026 · Source: BTS 2015
</div>
""", unsafe_allow_html=True)

# ── About Us & Stay Informed Buttons ─────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
_, btn_col1, btn_col2, _ = st.columns([2, 1, 1, 2])

with btn_col1:
    if st.button("About Us", use_container_width=True):
        show_about()

with btn_col2:
    if st.button("Stay Informed", use_container_width=True):
        show_newsletter()