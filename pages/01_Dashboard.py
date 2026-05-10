# 01_Dashboard.py
import streamlit as st
import plotly.graph_objects as go
from utils.navbar import show_navbar
from utils.dashboard_data import (
    get_delay_by_hour,
    get_delay_by_weekday,
    get_delay_by_airline,
)

# ── Seitenkonfiguration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard – CatchYourFlight",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("<style>[data-testid='stSidebar'],[data-testid='collapsedControl']{display:none!important}</style>", unsafe_allow_html=True)

# ── Navbar anzeigen ───────────────────────────────────────────────────────────
show_navbar()

# ── Titel ─────────────────────────────────────────────────────────────────────
st.title("Dashboard")
st.markdown("Delay statistics for the 5 busiest US airports (ATL · ORD · JFK · LAX · DEN) — 2015 data.")
st.markdown("---")

# ── Daten laden ───────────────────────────────────────────────────────────────
# Aggregierte Verspätungsstatistiken aus utils/dashboard_data.py laden
df_hour    = get_delay_by_hour()
df_weekday = get_delay_by_weekday()
df_airline = get_delay_by_airline()

# Gemeinsame Farben für alle Charts
COLOR_LINE = "#3B82F6"   # Blau für Linien
COLOR_BAR  = "#6366F1"   # Lila für Balken
COLOR_GRID = "#f0f0f0"   # Hellgrau für Gitternetz

# ── CHART 1: VERSPÄTUNGEN NACH TAGESZEIT (Liniendiagramm) ─────────────────────
st.subheader("Delays by Time of Day")
st.caption("On average delays accumulate over the course of the day.")

# Stundenbeschriftungen für X-Achse (z.B. "06:00")
hour_labels = [f"{h:02d}:00" for h in df_hour["hour"]]

# Liniendiagramm mit gefülltem Bereich unter der Kurve aufbauen
fig_hour = go.Figure()

# Gefüllter Bereich unter der Linie für bessere Lesbarkeit
fig_hour.add_trace(go.Scatter(
    x=hour_labels,
    y=df_hour["delay_pct"],
    mode="lines",                       # Nur Linie, keine Punkte
    line=dict(color=COLOR_LINE, width=2.5, shape="spline"),  # Glatte Kurve
    fill="tozeroy",                     # Fläche bis zur X-Achse füllen
    fillcolor="rgba(59,130,246,0.12)",  # Sehr helles Blau als Füllung
    name="Delay rate",
))

# Layout des Liniendiagramms konfigurieren
fig_hour.update_layout(
    height=320,
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    xaxis=dict(
        title="Departure Hour",
        tickangle=0,
        gridcolor=COLOR_GRID,
        showline=True,
        linecolor="#e5e7eb",
        # Nur jede zweite Stunde beschriften damit es nicht zu voll wird
        tickvals=hour_labels[::2],
        ticktext=hour_labels[::2],
    ),
    yaxis=dict(
        title="% Flights Delayed",
        gridcolor=COLOR_GRID,
        ticksuffix="%",
        range=[0, 45],
    ),
    showlegend=False,
)

st.plotly_chart(fig_hour, use_container_width=True)

st.markdown("---")

# ── CHART 2: VERSPÄTUNGEN NACH WOCHENTAG (Balkendiagramm) ─────────────────────
st.subheader("Delays by Day of Week")
st.caption("Friday usually is the day with the biggest cumulated delay.")

# Farben: Freitag rot hervorheben, alle anderen lila
bar_colors_weekday = [
    "#EF4444" if day == "Fri" else COLOR_BAR
    for day in df_weekday["day"]
]

# Balkendiagramm aufbauen
fig_weekday = go.Figure()

fig_weekday.add_trace(go.Bar(
    x=df_weekday["day"],
    y=df_weekday["delay_pct"],
    marker_color=bar_colors_weekday,    # Freitag rot, Rest lila
    marker_line_width=0,                # Kein Rahmen um die Balken
    text=[f"{v}%" for v in df_weekday["delay_pct"]],  # Prozentangabe auf dem Balken
    textposition="outside",             # Beschriftung über dem Balken
    textfont=dict(size=12, color="#333333"),
))

# Layout des Balkendiagramms konfigurieren
fig_weekday.update_layout(
    height=320,
    margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    xaxis=dict(
        title="Day of Week",
        gridcolor=COLOR_GRID,
        showline=True,
        linecolor="#e5e7eb",
    ),
    yaxis=dict(
        title="% Flights Delayed",
        gridcolor=COLOR_GRID,
        ticksuffix="%",
        range=[0, 30],
    ),
    showlegend=False,
    bargap=0.35,                        # Abstand zwischen den Balken
)

st.plotly_chart(fig_weekday, use_container_width=True)

st.markdown("---")

# ── CHART 3: VERSPÄTUNGEN NACH AIRLINE (horizontales Balkendiagramm) ──────────
st.subheader("Delays by Airline")
st.caption("Sorted from most to least punctual - Hawaiian Airlines has the least delay of all.")

# Farben je nach Verspätungsrate: grün (gut) → gelb → rot (schlecht)
def airline_color(pct: float) -> str:
    """Gibt eine Farbe abhängig von der Verspätungsrate zurück."""
    if pct < 16:   return "#10B981"   # Grün: unter 16% = sehr pünktlich
    elif pct < 22: return "#F59E0B"   # Gelb: 16–22% = durchschnittlich
    else:          return "#EF4444"   # Rot: über 22% = viele Verspätungen

bar_colors_airline = [airline_color(p) for p in df_airline["delay_pct"]]

# Horizontales Balkendiagramm aufbauen (Airlines auf Y-Achse)
fig_airline = go.Figure()

fig_airline.add_trace(go.Bar(
    x=df_airline["delay_pct"],
    y=df_airline["airline"],
    orientation="h",                    # Horizontal ausrichten
    marker_color=bar_colors_airline,
    marker_line_width=0,
    text=[f"{v}%" for v in df_airline["delay_pct"]],  # Prozent rechts vom Balken
    textposition="outside",
    textfont=dict(size=11, color="#333333"),
))

# Layout des horizontalen Balkendiagramms konfigurieren
fig_airline.update_layout(
    height=420,
    margin=dict(l=0, r=60, t=10, b=0),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    xaxis=dict(
        title="% Flights Delayed",
        gridcolor=COLOR_GRID,
        ticksuffix="%",
        range=[0, 34],
    ),
    yaxis=dict(
        title="",
        gridcolor=COLOR_GRID,
        automargin=True,                # Automatisch Platz für lange Airline-Namen
    ),
    showlegend=False,
    bargap=0.25,
)

st.plotly_chart(fig_airline, use_container_width=True)

# ── Fussnote ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Source: Bureau of Transportation Statistics (BTS) · 2015 US Domestic Flights · Airports: ATL, ORD, JFK, LAX, DEN")
