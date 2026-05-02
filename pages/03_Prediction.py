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

# ── Weisser Text in Eingabefeldern ───────────────────────────────────────────
st.markdown("""
<style>
/* Weisser Text in Dropdown-Feldern */
div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] div[class*="singleValue"] {
    color: #ffffff !important;
}
/* Weisser Text im Datums-Feld */
div[data-baseweb="input"] input {
    color: #ffffff !important;
}
/* Weisser Pfeil im Dropdown */
div[data-baseweb="select"] svg {
    fill: #ffffff !important;
}
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
    # 33% Benchmark Logik:
    # Unter 33% → "Low Risk, wahrscheinlich kein Delay"
    # Über 33%  → wahrscheinlichste Kategorie anzeigen

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
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.8);
                        letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.5rem;">
                Delay Risk — {risk_level}
            </div>
            <div style="font-size:3rem; font-weight:700; color:#ffffff; line-height:1;">
                ✅ No Delay Expected
            </div>
            <div style="font-size:1rem; color:rgba(255,255,255,0.9); margin-top:0.5rem;">
                Only <strong style="color:#ffffff">{result["delay_probability_pct"]}</strong> probability of delay
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Über 33% — wahrscheinlichste Kategorie anzeigen
        st.markdown(f"""
        <div style="
            background: {risk_color};
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1.5rem;
        ">
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.8);
                        letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.5rem;">
                Delay Risk — {risk_level}
            </div>
            <div style="font-size:3rem; font-weight:700; color:#ffffff; line-height:1;">
                {result["display_category"]}
            </div>
            <div style="font-size:1rem; color:rgba(255,255,255,0.9); margin-top:0.5rem;">
                Most likely delay · <strong style="color:#ffffff">{result["delay_probability_pct"]}</strong> chance of any delay
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── METRIKEN ──────────────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric("Flight",     f"{airline_code} · {origin_code} → {dest_code}")
    m2.metric("Departure",  f"{flight_date.strftime('%b %d, %Y')} · {dep_hour:02d}:00")
    m3.metric("Distance",   f"{result['distance_km']:,} km")

    # ── ALLE KATEGORIEN ANZEIGEN ──────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Delay Probability by Category")
    st.caption("Breakdown of probabilities across all delay categories")

    # Kategorien in gewünschter Reihenfolge
    category_order = ["No Delay", "15-30 min", "30-45 min", "45-60 min", "60-90 min", "90+ min"]
    all_cats = result["all_categories"]

    for cat in category_order:
        if cat in all_cats:
            prob = all_cats[cat]
            # Farbe je nach Kategorie
            if cat == "No Delay":
                bar_color = "#10B981"
            elif cat in ["15-30 min", "30-45 min"]:
                bar_color = "#F59E0B"
            else:
                bar_color = "#EF4444"

            # Highlight die wahrscheinlichste Kategorie
            is_best = (cat == result["display_category"] and result["display_mode"] == "show_category")
            weight  = "700" if is_best else "400"
            marker  = " ◀ most likely" if is_best else ""

            st.markdown(f"""
            <div style="margin-bottom:0.5rem;">
                <div style="display:flex; justify-content:space-between;
                            font-size:0.85rem; margin-bottom:0.2rem;">
                    <span style="font-weight:{weight}; color:#111111;">{cat}{marker}</span>
                    <span style="font-weight:{weight}; color:#111111;">{prob:.0%}</span>
                </div>
                <div style="background:#f0f0f0; border-radius:4px; height:8px;">
                    <div style="background:{bar_color}; width:{prob*100:.1f}%;
                                height:8px; border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

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

    # ── TAGESÜBERSICHT ────────────────────────────────────────────────────────
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

    # ── MODEL INFO ────────────────────────────────────────────────────────────
    st.markdown("---")
    w = result["weather_used"]
    st.caption(
        f"Model inputs at {dep_hour:02d}:00 — "
        f"Temp={w['TEMP']}°C · Rain={w['PRCP_H']}mm · "
        f"Snow={w['SNOW_H']}cm · Wind={w['WIND']}m/s · Cloud={w['CLOUD']}% · "
        f"Trained on 2015 US flight data (XGBoost)"
    )
