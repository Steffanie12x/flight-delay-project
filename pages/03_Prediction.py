"""
pages/03_Prediction.py
======================
ML-Vorhersage-Seite der Flight Delay App.
"""

import streamlit as st
from datetime import date
from utils.navbar import show_navbar
from utils.weather import get_weather, classify_weather_condition, get_airport_list
from model.predict import predict_delay, get_airline_options, get_destination_options

st.set_page_config(
    page_title="Prediction – Flight Delay",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

show_navbar()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, p, div {
    font-family: 'Inter', sans-serif !important;
}
h1 { font-weight: 700 !important; letter-spacing: -0.02em !important; }
h2 { font-weight: 600 !important; letter-spacing: -0.01em !important; }
h3 { font-weight: 600 !important; }
.stSelectbox label, .stDateInput label, .stSlider label {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    opacity: 0.7 !important;
}
hr { opacity: 0.15 !important; }
</style>
""", unsafe_allow_html=True)

st.title("Prediction Tool")
st.markdown("Enter your flight details to get a delay probability estimate.")
st.markdown("---")

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
    date_str = flight_date.strftime("%Y-%m-%d")
    with st.spinner("Loading weather & running prediction..."):
        try:
            weather_df = get_weather(origin_code, date_str)
        except Exception as e:
            st.error(f"Could not load weather data: {e}")
            st.stop()

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

    risk_color = result["risk_color"]
    prob_pct   = result["delay_probability_pct"]
    category   = result["display_category"]
    risk_level = result["risk_level"]
    factors    = result["top_factors"]

    condition_icons = {
        "Heavy Snow":  "❄️ Heavy Snow",
        "Light Snow":  "🌨️ Light Snow",
        "Heavy Rain":  "🌧️ Heavy Rain",
        "Light Rain":  "🌦️ Light Rain",
        "Strong Wind": "💨 Strong Wind",
        "Overcast":    "☁️ Overcast",
        "Good":        "☀️ Good",
    }

    st.markdown("---")

    # ── 1. THREE KPI CARDS ────────────────────────────────────────────────────
    st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.25rem;margin-bottom:2rem;">
<div style="background:#ffffff;border:1px solid #e5e7eb;border-top:3px solid {risk_color};border-radius:0 0 12px 12px;padding:1.75rem 1.5rem;text-align:center;">
<div style="font-size:0.65rem;color:#9ca3af;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.75rem;">Delay Probability</div>
<div style="font-size:3rem;font-weight:700;color:{risk_color};line-height:1;margin-bottom:0.25rem;">{prob_pct}</div>
<div style="font-size:0.8rem;color:#9ca3af;">chance of delay</div>
</div>
<div style="background:#ffffff;border:1px solid #e5e7eb;border-top:3px solid #6366F1;border-radius:0 0 12px 12px;padding:1.75rem 1.5rem;text-align:center;">
<div style="font-size:0.65rem;color:#9ca3af;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.75rem;">Expected Delay</div>
<div style="font-size:2rem;font-weight:700;color:#111111;line-height:1.2;margin-bottom:0.25rem;">{category}</div>
<div style="font-size:0.8rem;color:#9ca3af;">most likely category</div>
</div>
<div style="background:#ffffff;border:1px solid #e5e7eb;border-top:3px solid {risk_color};border-radius:0 0 12px 12px;padding:1.75rem 1.5rem;text-align:center;">
<div style="font-size:0.65rem;color:#9ca3af;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.75rem;">Risk Level</div>
<div style="display:inline-block;background:{risk_color}20;color:{risk_color};font-weight:700;font-size:1.4rem;padding:0.35rem 1.25rem;border-radius:20px;margin-top:0.25rem;">{risk_level}</div>
<div style="font-size:0.8rem;color:#9ca3af;margin-top:0.5rem;">{origin_code} → {dest_code}</div>
</div>
</div>
""", unsafe_allow_html=True)

    # ── 2. WEATHER AT DEPARTURE HOUR ──────────────────────────────────────────
    weather_at_hour = weather_df[weather_df["hour"] == dep_hour].iloc[0]
    condition       = classify_weather_condition(weather_at_hour)
    condition_label = condition_icons.get(condition, condition)

    st.markdown(f"""
<div style="background:#f8f9fa;border:1px solid #e5e7eb;border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;">
<div style="font-size:0.65rem;color:#9ca3af;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:1rem;">Weather at Departure · {dep_hour:02d}:00</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1rem;">
<div style="text-align:center;">
<div style="font-size:1.5rem;">🌡️</div>
<div style="font-size:0.7rem;color:#9ca3af;margin:0.25rem 0;">Temperature</div>
<div style="font-weight:600;color:#111111;">{weather_at_hour['temperature']} °C</div>
</div>
<div style="text-align:center;">
<div style="font-size:1.5rem;">🌧️</div>
<div style="font-size:0.7rem;color:#9ca3af;margin:0.25rem 0;">Precipitation</div>
<div style="font-weight:600;color:#111111;">{weather_at_hour['precipitation']} mm</div>
</div>
<div style="text-align:center;">
<div style="font-size:1.5rem;">💨</div>
<div style="font-size:0.7rem;color:#9ca3af;margin:0.25rem 0;">Wind Speed</div>
<div style="font-weight:600;color:#111111;">{weather_at_hour['windspeed']} km/h</div>
</div>
<div style="text-align:center;">
<div style="font-size:1.5rem;">☁️</div>
<div style="font-size:0.7rem;color:#9ca3af;margin:0.25rem 0;">Condition</div>
<div style="background:{risk_color}20;color:{risk_color};font-weight:600;font-size:0.8rem;padding:0.2rem 0.5rem;border-radius:10px;display:inline-block;">{condition_label}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    # ── 3. FULL DAY WEATHER OVERVIEW ──────────────────────────────────────────
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

    st.markdown("---")

    # ── 4. CONTRIBUTING FACTORS ───────────────────────────────────────────────
    st.subheader("Contributing Factors")

    if factors:
        _impact_colors = {"high": "#EF4444", "medium": "#F59E0B", "low": "#10B981"}
        _impact_labels = {"high": "high impact", "medium": "medium", "low": "low"}

        cells = ""
        for f in factors:
            color = _impact_colors.get(f["impact"], "#9ca3af")
            label = _impact_labels.get(f["impact"], f["impact"])
            cells += f"""
<div style="background:#f8f9fa;border:1px solid #e5e7eb;border-radius:10px;padding:0.85rem 1.1rem;display:flex;align-items:center;gap:0.75rem;">
<div style="width:10px;height:10px;border-radius:50%;background:{color};flex-shrink:0;"></div>
<div><span style="font-size:0.9rem;color:#111111;font-weight:500;">{f['label']}</span>
<span style="font-size:0.78rem;color:#9ca3af;margin-left:0.4rem;">({label})</span></div>
</div>"""
        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:1.5rem;">
{cells}
</div>
""", unsafe_allow_html=True)

    w = result["weather_used"]
    st.caption(
        f"Model inputs: TEMP={w['TEMP']}°C · PRCP={w['PRCP_H']}mm · "
        f"SNOW={w['SNOW_H']}cm · WIND={round(w['WIND'], 1)}m/s · CLOUD={w['CLOUD']}% · "
        f"Trained on 2015 US flight data (XGBoost, 68.8% accuracy)"
    )
