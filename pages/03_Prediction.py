"""
pages/03_Prediction.py
======================
ML-Vorhersage-Seite der Flight Delay App.

ÄNDERUNGEN gegenüber Version 1:
- Weisser Text in der Ergebnis-Box
- 33% Benchmark Anzeigelogik
- Alle Kategorien mit Wahrscheinlichkeiten anzeigen
- Stündliche Wetterdaten
"""

import streamlit as st
from datetime import date
from utils.navbar import show_navbar
from utils.weather import get_weather, classify_weather_condition, get_airport_list
from model.predict import predict_delay, get_airline_options, get_destination_options

# ── Seitenkonfiguration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prediction – Flight Delay",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

show_navbar()

# ── Design & Font ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Inter Font von Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Gesamte App auf Inter umstellen */
html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, p, div {
    font-family: 'Inter', sans-serif !important;
}

/* Titel grösser und schärfer */
h1 { font-weight: 700 !important; letter-spacing: -0.02em !important; }
h2 { font-weight: 600 !important; letter-spacing: -0.01em !important; }
h3 { font-weight: 600 !important; }

/* Labels über Inputs etwas heller und grösser */
.stSelectbox label, .stDateInput label, .stSlider label {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    opacity: 0.7 !important;
}

/* Trennlinien subtiler */
hr { opacity: 0.15 !important; }

/* Metriken schöner */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* Weisser Text in allen Dropdown-Feldern */
div[data-baseweb="select"] * { color: #ffffff !important; }
li[role="option"] *, li[role="option"] { color: #ffffff !important; }
div[data-baseweb="input"] * { color: #ffffff !important; }
input { color: #ffffff !important; }
div[data-baseweb="calendar"] *, div[data-baseweb="datepicker"] * { color: #ffffff !important; }
div[data-baseweb="select"] svg path { fill: #ffffff !important; stroke: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("Prediction Tool")
st.markdown("Enter your flight details to get a delay probability estimate.")
st.markdown("---")

# ── EINGABE-FORMULAR ──────────────────────────────────────────────────────────
st.subheader("Your Flight Details")

col1, col2 = st.columns(2, gap="large")

with col1:
    airport_options = get_airport_list()
    origin_name = st.selectbox(
        "Departure Airport",
        options=list(airport_options.keys()),
        index=2,
    )
    origin_code = airport_options[origin_name]

    airline_options = get_airline_options()
    airline_name = st.selectbox("Airline", options=list(airline_options.keys()))
    airline_code = airline_options[airline_name]

with col2:
    dest_options = get_destination_options(origin_code)
    dest_name = st.selectbox("Destination Airport", options=list(dest_options.keys()))
    dest_code = dest_options[dest_name]

    flight_date = st.date_input(
        "Flight Date",
        value=date.today(),
        min_value=date(2020, 1, 1),
    )

dep_hour = st.slider("Departure Hour", min_value=0, max_value=23, value=12, format="%d:00")

st.markdown("---")

predict_btn = st.button("✈ Predict Delay", type="primary", use_container_width=True)

if predict_btn:

    # ── Wetterdaten laden ─────────────────────────────────────────────────────
    with st.spinner("Loading weather data..."):
        try:
            date_str   = flight_date.strftime("%Y-%m-%d")
            weather_df = get_weather(origin_code, date_str)
        except Exception as e:
            st.error(f"Could not load weather data: {e}")
            st.stop()

    # ── ML Vorhersage ─────────────────────────────────────────────────────────
    with st.spinner("Running prediction model..."):
        result = predict_delay(
            airline     = airline_code,
            origin      = origin_code,
            destination = dest_code,
            flight_date = flight_date,
            dep_hour    = dep_hour,
            weather_df  = weather_df,
        )

    if "error" in result:
        st.error(result["error"])
        st.stop()

    st.markdown("---")
    st.subheader("Prediction Result")

    risk_color = result["risk_color"]
    risk_level = result["risk_level"]

    # ── HAUPTERGEBNIS BOX ─────────────────────────────────────────────────────
    if result["display_mode"] == "low_risk":
        # Unter 33% — kein Delay erwartet
        st.markdown(f"""
        <div style="
            background: {risk_color};
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1.5rem;
        ">
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.85);
                        letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.5rem;">
                Delay Risk — {risk_level}
            </div>
            <div style="font-size:3rem; font-weight:700; color:#ffffff; line-height:1.1;">
                No Delay
            </div>
            <div style="font-size:1rem; color:rgba(255,255,255,0.9); margin-top:0.75rem;">
                Only <strong style="color:#ffffff">{result["delay_probability_pct"]}</strong> probability of any delay
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Über 33% — wahrscheinlichste Delay-Kategorie anzeigen
        st.markdown(f"""
        <div style="
            background: {risk_color};
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1.5rem;
        ">
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.85);
                        letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.5rem;">
                Delay Risk — {risk_level}
            </div>
            <div style="font-size:3rem; font-weight:700; color:#ffffff; line-height:1.1;">
                {result["display_category"]}
            </div>
            <div style="font-size:1rem; color:rgba(255,255,255,0.9); margin-top:0.75rem;">
                {result["delay_probability_pct"]} probability of any delay
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── METRIKEN ──────────────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric("Flight",    f"{airline_code} · {origin_code} → {dest_code}")
    m2.metric("Departure", f"{flight_date.strftime('%b %d, %Y')} · {dep_hour:02d}:00")
    m3.metric("Distance",  f"{result['distance_km']:,} km")

    # ── WETTER ANZEIGEN ───────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader(f"Weather at {origin_name} – {flight_date.strftime('%B %d, %Y')}")

    # Wetter zur Abflugstunde
    weather_at_hour = weather_df[weather_df["hour"] == dep_hour].iloc[0]
    condition       = classify_weather_condition(weather_at_hour)

    condition_icons = {
        "Heavy Snow": "❄️ Heavy Snow", "Light Snow":  "🌨️ Light Snow",
        "Heavy Rain": "🌧️ Heavy Rain", "Light Rain":  "🌦️ Light Rain",
        "Strong Wind":"💨 Strong Wind", "Overcast":    "☁️ Overcast",
        "Good":       "☀️ Good",
    }
    condition_label = condition_icons.get(condition, condition)
    st.markdown(f"**Condition at {dep_hour:02d}:00:** {condition_label}")

    w1, w2, w3, w4 = st.columns(4)
    w1.metric("🌡️ Temperature", f"{weather_at_hour['temperature']} °C")
    w2.metric("🌧️ Precipitation", f"{weather_at_hour['precipitation']} mm")
    w3.metric("❄️ Snowfall", f"{weather_at_hour['snowfall']} cm")
    w4.metric("💨 Wind Speed", f"{weather_at_hour['windspeed']} km/h")

    st.markdown("---")

    # ── TAGESÜBERSICHT — nur bei echten stündlichen Daten anzeigen ────────────
    # Wenn alle Temperaturwerte gleich sind = Tagesdurchschnitt → nicht anzeigen
    is_daily_avg = weather_df["temperature"].nunique() == 1

    if not is_daily_avg:
        st.subheader("Full Day Weather Overview")

        display_df = weather_df.copy()

        def hour_label(h):
            if h < 6:    return f"🌙 {h:02d}:00"
            elif h < 12: return f"🌅 {h:02d}:00"
            elif h < 19: return f"☀️ {h:02d}:00"
            else:        return f"🌆 {h:02d}:00"

        display_df["hour"]      = display_df["hour"].apply(hour_label)
        display_df["condition"] = weather_df.apply(classify_weather_condition, axis=1).map(condition_icons)
        display_df = display_df[["hour", "condition", "temperature", "precipitation", "snowfall", "windspeed", "cloudcover"]]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "hour":          st.column_config.TextColumn("🕐 Hour"),
                "condition":     st.column_config.TextColumn("Condition"),
                "temperature":   st.column_config.NumberColumn("🌡️ Temp",  format="%.1f °C"),
                "precipitation": st.column_config.NumberColumn("🌧️ Rain",  format="%.1f mm"),
                "snowfall":      st.column_config.NumberColumn("❄️ Snow",  format="%.1f cm"),
                "windspeed":     st.column_config.NumberColumn("💨 Wind",  format="%.1f km/h"),
                "cloudcover":    st.column_config.ProgressColumn(
                    "☁️ Clouds", format="%d%%", min_value=0, max_value=100
                ),
            }
        )
    else:
        st.caption("📅 Weather based on historical daily average (same day, last 3 years) — hourly breakdown not available for dates beyond 16 days.")

    # ── MODEL INFO + QUELLEN ──────────────────────────────────────────────────
    st.markdown("---")

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("**Model Input Variables**")
        w = result["weather_used"]
        st.markdown(f"""
        | Variable | Value | Description |
        |---|---|---|
        | Month | {flight_date.month} | Month of departure |
        | Day of Week | {flight_date.isoweekday()} | 1=Mon, 7=Sun |
        | Departure Hour | {dep_hour}:00 | Scheduled departure time |
        | Airline | {airline_code} | Airline code |
        | Origin | {origin_code} | Departure airport |
        | Destination | {dest_code} | Arrival airport |
        | Distance | {result['distance_km']:,} km | Flight distance |
        | Temperature | {w['TEMP']} °C | Temp at departure time |
        | Precipitation | {w['PRCP_H']} mm | Rain at departure time |
        | Snowfall | {w['SNOW_H']} cm | Snow at departure time |
        | Wind | {round(w['WIND'], 1)} m/s | Wind at departure time |
        | Cloud Cover | {w['CLOUD']} % | Clouds at departure time |
        """)

    with col_b:
        st.markdown("**Data Sources**")
        st.markdown("""
        | Source | Usage |
        |---|---|
        | [Kaggle – US Flight Delays 2015](https://www.kaggle.com/datasets/usdot/flight-delays) | Training data (5.8M flights) |
        | [Open-Meteo Archive API](https://open-meteo.com) | Historical weather (training + past dates) |
        | [Open-Meteo Forecast API](https://open-meteo.com) | Weather forecast (< 16 days) |

        **Model**
        | | |
        |---|---|
        | Algorithm | XGBoost |
        | Training flights | 879,956 |
        | Binary accuracy | 68.8% |
        | Multiclass accuracy | 79.8% |
        | Delay threshold | ≥ 15 minutes |
        """)
