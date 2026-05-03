"""
pages/03_Prediction.py
======================
ML-Vorhersage-Seite der Flight Delay App.
Nutzer gibt Flugdetails ein und bekommt Delay-Wahrscheinlichkeit zurück.
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

# ── Navbar ────────────────────────────────────────────────────────────────────
show_navbar()

# ── Titel ─────────────────────────────────────────────────────────────────────
st.title("Prediction Tool")
st.markdown("Enter your flight details to get a delay probability estimate.")
st.markdown("---")

# ── EINGABE-FORMULAR ──────────────────────────────────────────────────────────
st.subheader("Your Flight Details")

col1, col2 = st.columns(2, gap="large")

with col1:
    # Abflughafen Dropdown
    airport_options = get_airport_list()   # {"Atlanta (ATL)": "ATL", ...}
    origin_name = st.selectbox(
        "Departure Airport",
        options=list(airport_options.keys()),
        index=2,   # JFK als Standard
    )
    origin_code = airport_options[origin_name]

    # Airline Dropdown
    airline_options = get_airline_options()  # {"American Airlines": "AA", ...}
    airline_name = st.selectbox(
        "Airline",
        options=list(airline_options.keys()),
    )
    airline_code = airline_options[airline_name]

with col2:
    # Zielflughafen (ohne Abflughafen)
    dest_options = get_destination_options(origin_code)
    dest_name = st.selectbox(
        "Destination Airport",
        options=list(dest_options.keys()),
    )
    dest_code = dest_options[dest_name]

    # Datum
    flight_date = st.date_input(
        "Flight Date",
        value=date.today(),
        min_value=date(2020, 1, 1),
    )

# Abflugzeit als Slider über volle Breite
dep_hour = st.slider(
    "Departure Hour",
    min_value=0,
    max_value=23,
    value=12,
    format="%d:00",
)

st.markdown("---")

# ── VORHERSAGE BUTTON ─────────────────────────────────────────────────────────
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

    # Fehler abfangen
    if "error" in result:
        st.error(result["error"])
        st.stop()

    st.markdown("---")

    # ── ERGEBNIS ANZEIGEN ─────────────────────────────────────────────────────
    st.subheader("Prediction Result")

    # Hauptergebnis: grosse farbige Box
    risk_color = result["risk_color"]
    prob_pct   = result["delay_probability_pct"]
    category   = result["delay_category"]
    risk_level = result["risk_level"]

    st.markdown(f"""
    <div style="
        background: {risk_color}18;
        border: 2px solid {risk_color};
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
    ">
        <div style="font-size: 0.75rem; color: {risk_color}; letter-spacing: 0.1em;
                    text-transform: uppercase; margin-bottom: 0.5rem;">
            Delay Risk — {risk_level}
        </div>
        <div style="font-size: 3.5rem; font-weight: 700; color: {risk_color}; line-height: 1;">
            {prob_pct}
        </div>
        <div style="font-size: 1rem; color: #666666; margin-top: 0.5rem;">
            probability of delay · expected: <strong>{category}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Drei Metriken nebeneinander
    m1, m2, m3 = st.columns(3)
    m1.metric("Flight", f"{airline_code} · {origin_code} → {dest_code}")
    m2.metric("Departure", f"{flight_date.strftime('%b %d, %Y')} · {dep_hour:02d}:00")
    m3.metric("Distance", f"{result['distance_km']:,} km")

    st.markdown("---")

    # ── WETTER ANZEIGEN ───────────────────────────────────────────────────────
    st.subheader(f"Weather at {origin_name} – {flight_date.strftime('%B %d, %Y')}")

    # Wetter zur Abflugstunde
    weather_at_hour = weather_df[weather_df["hour"] == dep_hour].iloc[0]
    condition       = classify_weather_condition(weather_at_hour)

    condition_icons = {
        "Heavy Snow":    "❄️ Heavy Snow",
        "Light Snow":    "🌨️ Light Snow",
        "Heavy Rain":    "🌧️ Heavy Rain",
        "Light Rain":    "🌦️ Light Rain",
        "Strong Wind":   "💨 Strong Wind",
        "Overcast":      "☁️ Overcast",
        "Good":          "☀️ Good",
    }
    condition_label = condition_icons.get(condition, condition)
    st.markdown(f"**Condition at {dep_hour:02d}:00:** {condition_label}")

    # Vier Wetter-Metriken
    w1, w2, w3, w4 = st.columns(4)
    w1.metric("🌡️ Temperature", f"{weather_at_hour['temperature']} °C")
    w2.metric("🌧️ Precipitation", f"{weather_at_hour['precipitation']} mm")
    w3.metric("❄️ Snowfall", f"{weather_at_hour['snowfall']} cm")
    w4.metric("💨 Wind Speed", f"{weather_at_hour['windspeed']} km/h")

    st.markdown("---")

    # ── TAGESÜBERSICHT ────────────────────────────────────────────────────────
    st.subheader("Full Day Weather Overview")

    display_df = weather_df.copy()

    # Tageszeit-Icon
    def hour_label(h):
        if h < 6:    return f"🌙 {h:02d}:00"
        elif h < 12: return f"🌅 {h:02d}:00"
        elif h < 19: return f"☀️ {h:02d}:00"
        else:         return f"🌆 {h:02d}:00"

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

    # ── MODEL INFO ────────────────────────────────────────────────────────────
    st.markdown("---")
    w = result["weather_used"]
    st.caption(
        f"Model inputs: PRCP={w['PRCP']}mm · SNOW={w['SNOW']}mm · "
        f"TMAX={w['TMAX']}°C · TMIN={w['TMIN']}°C · AWND={w['AWND']}m/s · "
        f"Trained on 2015 US flight data (XGBoost, 69.1% accuracy)"
    )
