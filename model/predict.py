"""
model/predict.py
================
Vorhersage-Funktion für die Streamlit App — 16 Flughäfen.
"""

import pandas as pd
import joblib
import os
from datetime import datetime

MODEL_DIR = "models"

AIRLINE_NAMES = {
    "AA": "American Airlines",
    "AS": "Alaska Airlines",
    "B6": "JetBlue Airways",
    "DL": "Delta Air Lines",
    "F9": "Frontier Airlines",
    "HA": "Hawaiian Airlines",
    "MQ": "Envoy Air (American Eagle)",
    "OO": "SkyWest Airlines",
    "UA": "United Air Lines",
    "WN": "Southwest Airlines",
}

AIRPORT_NAMES = {
    "ATL": "Atlanta (ATL)",           "ORD": "Chicago O'Hare (ORD)",
    "DFW": "Dallas Fort Worth (DFW)", "DEN": "Denver (DEN)",
    "LAX": "Los Angeles (LAX)",       "SFO": "San Francisco (SFO)",
    "PHX": "Phoenix (PHX)",           "IAH": "Houston (IAH)",
    "LAS": "Las Vegas (LAS)",         "MSP": "Minneapolis (MSP)",
    "MCO": "Orlando (MCO)",           "SEA": "Seattle (SEA)",
    "DTW": "Detroit (DTW)",           "BOS": "Boston (BOS)",
    "EWR": "Newark (EWR)",            "JFK": "New York JFK (JFK)",
}

DELAY_BENCHMARK = 0.33


def load_models():
    required = ["binary_model.pkl", "multiclass_model.pkl", "encoders.pkl", "feature_list.pkl"]
    for f in required:
        if not os.path.exists(f"{MODEL_DIR}/{f}"):
            return None, None, None, None
    binary_model = joblib.load(f"{MODEL_DIR}/binary_model.pkl")
    multi_model  = joblib.load(f"{MODEL_DIR}/multiclass_model.pkl")
    encoders     = joblib.load(f"{MODEL_DIR}/encoders.pkl")
    feature_list = joblib.load(f"{MODEL_DIR}/feature_list.pkl")
    return binary_model, multi_model, encoders, feature_list


_binary_model, _multi_model, _encoders, _feature_list = load_models()


def _get_weather_at_hour(weather_df: pd.DataFrame, dep_hour: int) -> dict:
    row = weather_df[weather_df["hour"] == dep_hour]
    row = row.iloc[0] if not row.empty else weather_df.iloc[0]
    return {
        "TEMP":   float(row["temperature"] or 20.0),
        "PRCP_H": float(row["precipitation"] or 0.0),
        "SNOW_H": float(row["snowfall"] or 0.0),
        "WIND":   float(row["windspeed"] / 3.6 if row["windspeed"] else 5.0),
        "CLOUD":  float(row["cloudcover"] or 50.0),
    }


def _get_distance(origin: str, destination: str) -> float:
    """Berechnet Distanz zwischen zwei Flughäfen via Haversine-Formel."""
    import math
    coords = {
        "ATL": (33.6407, -84.4277),  "ORD": (41.9742, -87.9073),
        "DFW": (32.8998, -97.0403),  "DEN": (39.8561, -104.6737),
        "LAX": (33.9425, -118.4081), "SFO": (37.6213, -122.3790),
        "PHX": (33.4373, -112.0078), "IAH": (29.9902, -95.3368),
        "LAS": (36.0840, -115.1537), "MSP": (44.8848, -93.2223),
        "MCO": (28.4294, -81.3089),  "SEA": (47.4502, -122.3088),
        "DTW": (42.2162, -83.3554),  "BOS": (42.3656, -71.0096),
        "EWR": (40.6895, -74.1745),  "JFK": (40.6413, -73.7781),
    }
    if origin not in coords or destination not in coords:
        return 2500.0
    lat1, lon1 = math.radians(coords[origin][0]), math.radians(coords[origin][1])
    lat2, lon2 = math.radians(coords[destination][0]), math.radians(coords[destination][1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return round(6371 * 2 * math.asin(math.sqrt(a)), 0)


def predict_delay(airline, origin, destination, flight_date, dep_hour, weather_df):
    if _binary_model is None:
        return {"error": "Modell nicht geladen."}

    if isinstance(flight_date, str):
        dt = datetime.strptime(flight_date, "%Y-%m-%d")
    else:
        dt = datetime.combine(flight_date, datetime.min.time())

    month       = dt.month
    day_of_week = dt.isoweekday()
    weather     = _get_weather_at_hour(weather_df, dep_hour)
    distance_km = _get_distance(origin, destination)

    input_data = {
        "MONTH": month, "DAY_OF_WEEK": day_of_week, "DEP_HOUR": dep_hour,
        "AIRLINE": airline, "ORIGIN_AIRPORT": origin, "DESTINATION_AIRPORT": destination,
        "DISTANCE_KM": distance_km,
        "TEMP": weather["TEMP"], "PRCP_H": weather["PRCP_H"],
        "SNOW_H": weather["SNOW_H"], "WIND": weather["WIND"], "CLOUD": weather["CLOUD"],
    }

    df = pd.DataFrame([input_data])
    df = df[[f for f in _feature_list if f in df.columns]]

    for col, encoder in _encoders.items():
        if col in df.columns:
            known = set(encoder.classes_)
            df[col] = df[col].apply(lambda x: x if x in known else encoder.classes_[0])
            df[col] = encoder.transform(df[col].astype(str))

    delay_prob = _binary_model.predict_proba(df)[0][1]
    all_probs  = _multi_model.predict_proba(df)[0]
    categories = _multi_model._label_encoder.classes_

    delay_only_cats = {cat: prob for cat, prob in zip(categories, all_probs) if cat != "No Delay"}
    best_delay_cat  = max(delay_only_cats, key=delay_only_cats.get)

    if delay_prob < DELAY_BENCHMARK:
        display_mode, display_category = "low_risk", "No Delay"
        risk_level, risk_color = "Low", "#10B981"
    elif delay_prob < 0.66:
        display_mode, display_category = "show_category", best_delay_cat
        risk_level, risk_color = "Medium", "#F59E0B"
    else:
        display_mode, display_category = "show_category", best_delay_cat
        risk_level, risk_color = "High", "#EF4444"

    # ── TOP FACTORS generieren ────────────────────────────────────────────────
    top_factors = []

    # Abflugzeit
    if dep_hour >= 18:
        top_factors.append({"label": f"Evening departure ({dep_hour:02d}:00)", "impact": "high"})
    elif dep_hour >= 12:
        top_factors.append({"label": f"Afternoon departure ({dep_hour:02d}:00)", "impact": "medium"})
    else:
        top_factors.append({"label": f"Morning departure ({dep_hour:02d}:00)", "impact": "low"})

    # Airline
    airline_name = AIRLINE_NAMES.get(airline, airline)
    if delay_prob >= 0.5:
        top_factors.append({"label": airline_name, "impact": "high"})
    else:
        top_factors.append({"label": airline_name, "impact": "medium"})

    # Monat / Saison
    month = dt.month
    if month in [12, 1, 2]:
        top_factors.append({"label": "Winter season", "impact": "high"})
    elif month in [6, 7, 8]:
        top_factors.append({"label": "Summer season", "impact": "medium"})
    else:
        top_factors.append({"label": "Off-peak season", "impact": "low"})

    # Wetter
    if weather["SNOW_H"] > 0.5:
        top_factors.append({"label": "Snow at departure", "impact": "high"})
    elif weather["PRCP_H"] > 2.0:
        top_factors.append({"label": "Heavy rain at departure", "impact": "high"})
    elif weather["PRCP_H"] > 0.5:
        top_factors.append({"label": "Light rain at departure", "impact": "medium"})
    else:
        top_factors.append({"label": "Favorable weather", "impact": "low"})

    # Wochentag
    weekdays = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
                5: "Friday", 6: "Saturday", 7: "Sunday"}
    weekday_name = weekdays.get(day_of_week, "")
    if day_of_week in [1, 5]:
        top_factors.append({"label": f"{weekday_name} flight", "impact": "medium"})
    else:
        top_factors.append({"label": f"{weekday_name} flight", "impact": "low"})

    return {
        "delay_probability":     round(float(delay_prob), 3),
        "delay_probability_pct": f"{delay_prob:.0%}",
        "display_mode":          display_mode,
        "display_category":      display_category,
        "risk_level":            risk_level,
        "risk_color":            risk_color,
        "all_categories":        {cat: round(float(prob), 3) for cat, prob in zip(categories, all_probs)},
        "weather_used":          weather,
        "distance_km":           distance_km,
        "is_likely_delayed":     delay_prob >= 0.33,
        "top_factors":           top_factors,
    }


def get_airline_options():
    if _encoders and "AIRLINE" in _encoders:
        codes = sorted(_encoders["AIRLINE"].classes_.tolist())
    else:
        codes = list(AIRLINE_NAMES.keys())
    return {AIRLINE_NAMES.get(c, c): c for c in codes}


def get_destination_options(origin: str) -> dict:
    return {name: code for code, name in AIRPORT_NAMES.items() if code != origin}


def get_airport_list() -> dict:
    return {name: code for code, name in AIRPORT_NAMES.items()}
