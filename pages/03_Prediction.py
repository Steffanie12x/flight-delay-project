"""
pages/03_Prediction.py
======================
ML-Vorhersage-Seite der Flight Delay App.
Mit Boarding Pass Upload als Alternative zu den Dropdowns.
"""

import streamlit as st
from datetime import date, datetime
import json
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

# ── SESSION STATE für Boarding Pass Daten ────────────────────────────────────
if "bp_airline" not in st.session_state:    st.session_state.bp_airline    = None
if "bp_origin"  not in st.session_state:    st.session_state.bp_origin     = None
if "bp_dest"    not in st.session_state:    st.session_state.bp_dest       = None
if "bp_date"    not in st.session_state:    st.session_state.bp_date       = None
if "bp_hour"    not in st.session_state:    st.session_state.bp_hour       = None
if "bp_scanned" not in st.session_state:    st.session_state.bp_scanned    = False

# ─────────────────────────────────────────────
# EINGABE-FORMULAR
# ─────────────────────────────────────────────
st.subheader("Your Flight Details")

airport_options    = get_airport_list()
airport_codes_list = list(airport_options.values())
airport_names_list = list(airport_options.keys())

# Default-Index aus Boarding Pass oder Standard
default_origin_idx = 2
if st.session_state.bp_origin and st.session_state.bp_origin in airport_codes_list:
    default_origin_idx = airport_codes_list.index(st.session_state.bp_origin)

col1, col2 = st.columns(2, gap="large")

with col1:
    origin_name = st.selectbox(
        "Departure Airport",
        options=airport_names_list,
        index=default_origin_idx,
    )
    origin_code = airport_options[origin_name]

    airline_options    = get_airline_options()
    DEFUNCT_NAMES = {"Spirit Air Lines", "US Airways", "Virgin America", "Atlantic Southeast Airlines"}
    airline_options    = {k: v for k, v in airline_options.items() if k not in DEFUNCT_NAMES}
    airline_names_list = list(airline_options.keys())
    default_airline_idx = 0
    if st.session_state.bp_airline:
        for i, (name, code) in enumerate(airline_options.items()):
            if code == st.session_state.bp_airline:
                default_airline_idx = i
                break
    airline_name = st.selectbox("Airline", options=airline_names_list, index=default_airline_idx)
    airline_code = airline_options[airline_name]

with col2:
    dest_options  = get_destination_options(origin_code)
    dest_names    = list(dest_options.keys())
    dest_codes    = list(dest_options.values())
    default_dest_idx = 0
    if st.session_state.bp_dest and st.session_state.bp_dest in dest_codes:
        default_dest_idx = dest_codes.index(st.session_state.bp_dest)
    dest_name = st.selectbox("Destination Airport", options=dest_names, index=default_dest_idx)
    dest_code = dest_options[dest_name]

    default_date = st.session_state.bp_date if st.session_state.bp_date else date.today()
    flight_date  = st.date_input("Flight Date", value=default_date, min_value=date(2020, 1, 1))

default_hour = st.session_state.bp_hour if st.session_state.bp_hour is not None else 12
dep_hour = st.slider("Departure Hour", min_value=0, max_value=23, value=default_hour, format="%d:00")

# ── BOARDING PASS UPLOAD ──────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:1rem;margin:1.5rem 0 0.5rem;">
    <div style="flex:1;height:1px;background:rgba(255,255,255,0.15);"></div>
    <div style="font-size:0.75rem;color:#9ca3af;letter-spacing:0.08em;white-space:nowrap;">
        or upload your boarding pass instead of selecting everything
    </div>
    <div style="flex:1;height:1px;background:rgba(255,255,255,0.15);"></div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📎 Drop your boarding pass here (photo or PDF) — we'll fill in the details automatically",
    type=["png", "jpg", "jpeg", "pdf"],
    label_visibility="visible",
)

if uploaded_file is not None and not st.session_state.bp_scanned:
    with st.spinner("Analyzing boarding pass with AI..."):
        try:
            import anthropic
            import base64

            file_bytes = uploaded_file.read()
            b64        = base64.standard_b64encode(file_bytes).decode("utf-8")
            media_type = "application/pdf" if uploaded_file.type == "application/pdf" else uploaded_file.type

            cclient = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            prompt = """Look at this boarding pass and extract the following information.
Return ONLY a JSON object with these exact keys (no other text):
{
  "airline_code": "2-letter IATA code (e.g. AA, DL, UA)",
  "origin": "3-letter airport code (e.g. JFK, LAX)",
  "destination": "3-letter airport code (e.g. ATL, ORD)",
  "date": "YYYY-MM-DD format",
  "departure_hour": integer 0-23
}
If you cannot find a value, use null."""

            if media_type == "application/pdf":
                content = [
                    {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
                    {"type": "text", "text": prompt}
                ]
            else:
                content = [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                    {"type": "text", "text": prompt}
                ]

            response  = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=300,
                messages=[{"role": "user", "content": content}]
            )

            raw       = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            extracted = json.loads(raw)

            st.session_state.bp_airline = extracted.get("airline_code")
            st.session_state.bp_origin  = extracted.get("origin")
            st.session_state.bp_dest    = extracted.get("destination")
            st.session_state.bp_hour    = extracted.get("departure_hour")
            st.session_state.bp_scanned = True

            if extracted.get("date"):
                try:
                    st.session_state.bp_date = datetime.strptime(extracted["date"], "%Y-%m-%d").date()
                except:
                    pass

            st.success("✅ Boarding pass scanned! Fields updated above — press Predict Delay.")
            st.rerun()

        except Exception as e:
            st.warning(f"Could not scan boarding pass automatically: {e}. Please fill in the details manually.")

elif st.session_state.bp_scanned:
    st.success("✅ Boarding pass scanned! Adjust if needed and press Predict Delay.")

# ── PREDICT BUTTON ────────────────────────────────────────────────────────────
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
        "Heavy Snow":  "❄️ Heavy Snow", "Light Snow":  "🌨️ Light Snow",
        "Heavy Rain":  "🌧️ Heavy Rain", "Light Rain":  "🌦️ Light Rain",
        "Strong Wind": "💨 Strong Wind", "Overcast":   "☁️ Overcast",
        "Good":        "☀️ Good",
    }

    st.markdown("---")

    # ── KPI CARDS ─────────────────────────────────────────────────────────────
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

    # ── WEATHER ───────────────────────────────────────────────────────────────
    weather_at_hour = weather_df[weather_df["hour"] == dep_hour].iloc[0]
    condition       = classify_weather_condition(weather_at_hour)
    condition_label = condition_icons.get(condition, condition)

    st.markdown(f"""
<div style="background:#f8f9fa;border:1px solid #e5e7eb;border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;">
<div style="font-size:0.65rem;color:#9ca3af;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:1rem;">Weather at Departure · {dep_hour:02d}:00</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1rem;">
<div style="text-align:center;"><div style="font-size:1.5rem;">🌡️</div>
<div style="font-size:0.7rem;color:#9ca3af;margin:0.25rem 0;">Temperature</div>
<div style="font-weight:600;color:#111111;">{weather_at_hour['temperature']} °C</div></div>
<div style="text-align:center;"><div style="font-size:1.5rem;">🌧️</div>
<div style="font-size:0.7rem;color:#9ca3af;margin:0.25rem 0;">Precipitation</div>
<div style="font-weight:600;color:#111111;">{weather_at_hour['precipitation']} mm</div></div>
<div style="text-align:center;"><div style="font-size:1.5rem;">💨</div>
<div style="font-size:0.7rem;color:#9ca3af;margin:0.25rem 0;">Wind Speed</div>
<div style="font-weight:600;color:#111111;">{weather_at_hour['windspeed']} km/h</div></div>
<div style="text-align:center;"><div style="font-size:1.5rem;">☁️</div>
<div style="font-size:0.7rem;color:#9ca3af;margin:0.25rem 0;">Condition</div>
<div style="background:{risk_color}20;color:{risk_color};font-weight:600;font-size:0.8rem;padding:0.2rem 0.5rem;border-radius:10px;display:inline-block;">{condition_label}</div></div>
</div></div>
""", unsafe_allow_html=True)

    st.markdown("---")

    # ── FULL DAY OVERVIEW ─────────────────────────────────────────────────────
    is_daily_avg = weather_df["temperature"].nunique() == 1
    if not is_daily_avg:
        st.subheader("Full Day Weather Overview")

        cond_emoji = {
            "Heavy Snow": "❄️", "Light Snow": "🌨️",
            "Heavy Rain": "🌧️", "Light Rain": "🌦️",
            "Strong Wind": "💨", "Overcast": "☁️", "Good": "☀️",
        }

        cards_html = ""
        for _, row in weather_df.iterrows():
            h      = int(row["hour"])
            is_dep = h == dep_hour
            cond   = classify_weather_condition(row)
            emoji  = cond_emoji.get(cond, "🌤️")
            prcp   = float(row["precipitation"] or 0)
            wind   = float(row["windspeed"] or 0)
            temp   = float(row["temperature"] or 0)

            if is_dep:
                card_style = f"background:linear-gradient(160deg,{risk_color} 0%,#6366f1 100%);border:none;box-shadow:0 4px 14px {risk_color}55;"
                text_main  = "color:#ffffff;"
                text_sub   = "color:rgba(255,255,255,0.75);"
                hour_style = "color:rgba(255,255,255,0.85);font-weight:700;"
                dot        = f'<div style="width:6px;height:6px;border-radius:50%;background:#fff;margin:0 auto 4px;opacity:0.9;"></div>'
            else:
                card_style = "background:#f8fafc;border:1px solid #e5e7eb;"
                text_main  = "color:#111111;"
                text_sub   = "color:#9ca3af;"
                hour_style = "color:#6b7280;font-weight:500;"
                dot        = ""

            cards_html += f"""<div style="flex:0 0 auto;width:80px;border-radius:16px;padding:0.9rem 0.5rem;text-align:center;{card_style}">
{dot}
<div style="font-size:0.7rem;letter-spacing:0.04em;{hour_style}margin-bottom:0.4rem;">{h:02d} h</div>
<div style="font-size:1.5rem;font-weight:700;{text_main}margin-bottom:0.2rem;">{temp:.0f}°</div>
<div style="font-size:1.6rem;margin-bottom:0.4rem;">{emoji}</div>
<div style="font-size:0.7rem;{text_sub}margin-bottom:0.15rem;">💧 {prcp:.0f}%</div>
<div style="font-size:0.7rem;{text_sub}">💨 {wind:.0f}</div>
</div>"""

        st.markdown(f"""
<div style="background:#f1f5f9;border-radius:20px;padding:1.25rem 1rem;">
<div style="display:flex;gap:0.5rem;overflow-x:auto;padding-bottom:0.25rem;scrollbar-width:thin;scrollbar-color:#cbd5e1 transparent;">
{cards_html}
</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.caption("📅 Weather based on historical daily average (same day, last 3 years) — hourly breakdown not available for dates beyond 16 days.")

    st.markdown("---")

    # ── CONTRIBUTING FACTORS ──────────────────────────────────────────────────
    st.subheader("Contributing Factors")
    if factors:
        _impact_colors = {"high": "#EF4444", "medium": "#F59E0B", "low": "#10B981"}
        _impact_labels = {"high": "high impact", "medium": "medium", "low": "low"}
        cells = ""
        for f in factors:
            color = _impact_colors.get(f["impact"], "#9ca3af")
            label = _impact_labels.get(f["impact"], f["impact"])
            cells += f"""<div style="background:#f8f9fa;border:1px solid #e5e7eb;border-radius:10px;padding:0.85rem 1.1rem;display:flex;align-items:center;gap:0.75rem;">
<div style="width:10px;height:10px;border-radius:50%;background:{color};flex-shrink:0;"></div>
<div><span style="font-size:0.9rem;color:#111111;font-weight:500;">{f['label']}</span>
<span style="font-size:0.78rem;color:#9ca3af;margin-left:0.4rem;">({label})</span></div></div>"""
        st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:1.5rem;">{cells}</div>', unsafe_allow_html=True)

    w = result["weather_used"]
    st.caption(f"Model inputs: TEMP={w['TEMP']}°C · PRCP={w['PRCP_H']}mm · SNOW={w['SNOW_H']}cm · WIND={round(w['WIND'],1)}m/s · CLOUD={w['CLOUD']}% · Trained on 2015 US flight data (XGBoost, 66.8% accuracy)")
