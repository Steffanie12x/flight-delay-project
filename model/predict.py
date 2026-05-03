"""
model/predict.py
================
Vorhersage-Funktion für die Streamlit App.
Arbeitet zusammen mit utils/weather.py.

Verwendung in 03_Prediction.py:
    from utils.weather import get_weather
    from model.predict import predict_delay

    weather_df = get_weather("JFK", "2026-05-15")
    result = predict_delay(
        airline="AA",
        origin="JFK",
        destination="LAX",
        flight_date="2026-05-15",
        dep_hour=17,
        weather_df=weather_df,
    )
"""

import pandas as pd
import joblib
import os
from datetime import datetime, date

MODEL_DIR = "models"

# ── Airline-Codes zu lesbaren Namen ──────────────────────────────────────────
AIRLINE_NAMES = {
    "AA": "American Airlines",
    "AS": "Alaska Airlines",
    "B6": "JetBlue Airways",
    "DL": "Delta Air Lines",
    "EV": "Atlantic Southeast Airlines",
    "F9": "Frontier Airlines",
    "HA": "Hawaiian Airlines",
    "MQ": "American Eagle Airlines",
    "NK": "Spirit Air Lines",
    "OO": "Skywest Airlines",
    "UA": "United Air Lines",
    "US": "US Airways",
    "VX": "Virgin America",
    "WN": "Southwest Airlines",
}

# ── Distanzen zwischen den 5 Flughäfen in km ─────────────────────────────────
DISTANCES = {
    ("ATL", "ORD"): 1527, ("ATL", "JFK"): 1524, ("ATL", "LAX"): 3118, ("ATL", "DEN"): 2180,
    ("ORD", "ATL"): 1527, ("ORD", "JFK"): 1189, ("ORD", "LAX"): 2808, ("ORD", "DEN"): 1474,
    ("JFK", "ATL"): 1524, ("JFK", "ORD"): 1189, ("JFK", "LAX"): 4500, ("JFK", "DEN"): 2622,
    ("LAX", "ATL"): 3118, ("LAX", "ORD"): 2808, ("LAX", "JFK"): 4500, ("LAX", "DEN"): 1389,
    ("DEN", "ATL"): 2180, ("DEN", "ORD"): 1474, ("DEN", "JFK"): 2622, ("DEN", "LAX"): 1389,
}


# ─────────────────────────────────────────────
# 1. MODELLE LADEN (einmal beim Start)
# ─────────────────────────────────────────────

def load_models():
    """Lädt alle trainierten Modelle aus dem models/ Ordner."""
    required = ["binary_model.pkl", "multiclass_model.pkl", "encoders.pkl", "feature_list.pkl"]
    for f in required:
        if not os.path.exists(f"{MODEL_DIR}/{f}"):
            return None, None, None, None

    binary_model = joblib.load(f"{MODEL_DIR}/binary_model.pkl")
    multi_model  = joblib.load(f"{MODEL_DIR}/multiclass_model.pkl")
    encoders     = joblib.load(f"{MODEL_DIR}/encoders.pkl")
    feature_list = joblib.load(f"{MODEL_DIR}/feature_list.pkl")
    return binary_model, multi_model, encoders, feature_list


# Modelle einmal laden wenn die Datei importiert wird
_binary_model, _multi_model, _encoders, _feature_list = load_models()


# ─────────────────────────────────────────────
# 2. WETTER KONVERTIEREN
# ─────────────────────────────────────────────

def _convert_weather(weather_df: pd.DataFrame) -> dict:
    """
    Konvertiert stündliche Wetterdaten (aus utils/weather.py)
    in Tageswerte die das ML-Modell erwartet.

    Das Modell wurde mit NOAA Tageswerten trainiert:
    - PRCP: Tagesniederschlag (mm)
    - SNOW: Schnee (mm) — konvertiert von cm
    - TMAX: Höchsttemperatur des Tages (°C)
    - TMIN: Tiefsttemperatur des Tages (°C)
    - AWND: Max. Windgeschwindigkeit (m/s) — konvertiert von km/h
    """
    return {
        "PRCP": round(float(weather_df["precipitation"].sum()), 1),
        "SNOW": round(float(weather_df["snowfall"].sum() * 10), 1),  # cm → mm
        "TMAX": round(float(weather_df["temperature"].max()), 1),
        "TMIN": round(float(weather_df["temperature"].min()), 1),
        "AWND": round(float(weather_df["windspeed"].max() / 3.6), 1),  # km/h → m/s
    }


# ─────────────────────────────────────────────
# 3. HAUPTVORHERSAGE-FUNKTION
# ─────────────────────────────────────────────

def predict_delay(
    airline: str,
    origin: str,
    destination: str,
    flight_date,
    dep_hour: int,
    weather_df: pd.DataFrame,
) -> dict:
    """
    Macht eine Delay-Vorhersage für einen Flug.

    Parameter:
        airline:      Airline Code (z.B. "AA", "DL")
        origin:       Abflughafen (z.B. "JFK", "ATL")
        destination:  Zielflughafen (z.B. "LAX", "ORD")
        flight_date:  Datum als date-Objekt oder String "YYYY-MM-DD"
        dep_hour:     Abflugstunde (0-23)
        weather_df:   DataFrame aus utils/weather.py get_weather()

    Rückgabe:
        Dictionary mit allen Vorhersage-Ergebnissen
    """
    if _binary_model is None:
        return {"error": "Modell nicht geladen. Sind die .pkl Dateien im models/ Ordner?"}

    # ── Datum verarbeiten
    if isinstance(flight_date, str):
        dt = datetime.strptime(flight_date, "%Y-%m-%d")
    else:
        dt = datetime.combine(flight_date, datetime.min.time())

    month       = dt.month
    day_of_week = dt.isoweekday()   # 1=Montag, 7=Sonntag

    # ── Stündliche Wetterdaten zu Tageswerten konvertieren
    weather = _convert_weather(weather_df)

    # ── Distanz bestimmen
    distance_km = DISTANCES.get((origin, destination), 2500)

    # ── Feature-Vektor aufbauen
    input_data = {
        "MONTH":               month,
        "DAY_OF_WEEK":         day_of_week,
        "DEP_HOUR":            dep_hour,
        "AIRLINE":             airline,
        "ORIGIN_AIRPORT":      origin,
        "DESTINATION_AIRPORT": destination,
        "DISTANCE_KM":         distance_km,
        "PRCP":                weather["PRCP"],
        "SNOW":                weather["SNOW"],
        "TMAX":                weather["TMAX"],
        "TMIN":                weather["TMIN"],
        "AWND":                weather["AWND"],
    }

    df = pd.DataFrame([input_data])

    # ── Nur bekannte Features verwenden
    df = df[[f for f in _feature_list if f in df.columns]]

    # ── Text-Spalten encodieren (gleich wie beim Training)
    for col, encoder in _encoders.items():
        if col in df.columns:
            known = set(encoder.classes_)
            df[col] = df[col].apply(lambda x: x if x in known else encoder.classes_[0])
            df[col] = encoder.transform(df[col].astype(str))

    # ── Vorhersage 1: Wahrscheinlichkeit (Modell 1)
    delay_prob = _binary_model.predict_proba(df)[0][1]

    # ── Vorhersage 2: Delay-Kategorie (Modell 2)
    pred_encoded   = _multi_model.predict(df)[0]
    delay_category = _multi_model._label_encoder.inverse_transform([pred_encoded])[0]

    # ── Risiko-Level bestimmen
    if delay_prob < 0.30:
        risk_level, risk_color = "Low",    "#10B981"
    elif delay_prob < 0.55:
        risk_level, risk_color = "Medium", "#F59E0B"
    else:
        risk_level, risk_color = "High",   "#EF4444"

    return {
        "delay_probability":     round(float(delay_prob), 3),
        "delay_probability_pct": f"{delay_prob:.0%}",
        "delay_category":        delay_category,
        "is_likely_delayed":     delay_prob >= 0.5,
        "risk_level":            risk_level,
        "risk_color":            risk_color,
        "weather_used":          weather,
        "distance_km":           distance_km,
    }


# ─────────────────────────────────────────────
# 4. HILFSFUNKTIONEN FÜR DROPDOWNS
# ─────────────────────────────────────────────

def get_airline_options() -> dict:
    """
    Gibt Dictionary zurück: {voller Name: Code}
    Für Streamlit Selectbox.
    Beispiel: {"American Airlines": "AA", ...}
    """
    if _encoders and "AIRLINE" in _encoders:
        codes = sorted(_encoders["AIRLINE"].classes_.tolist())
    else:
        codes = list(AIRLINE_NAMES.keys())
    return {AIRLINE_NAMES.get(c, c): c for c in codes}


def get_destination_options(origin: str) -> dict:
    """
    Gibt mögliche Ziele für einen Abflughafen zurück.
    Schliesst den Abflughafen selbst aus.
    """
    all_airports = {
        "Atlanta (ATL)":        "ATL",
        "Chicago O'Hare (ORD)": "ORD",
        "New York JFK (JFK)":   "JFK",
        "Los Angeles (LAX)":    "LAX",
        "Denver (DEN)":         "DEN",
    }
    return {name: code for name, code in all_airports.items() if code != origin}
