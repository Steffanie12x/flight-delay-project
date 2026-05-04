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

def _get_weather_at_hour(weather_df: pd.DataFrame, dep_hour: int) -> dict:
    """Extrahiert Wetterwerte zur Abflugstunde — passend zu den Trainings-Features."""
    row = weather_df[weather_df["hour"] == dep_hour]
    row = row.iloc[0] if not row.empty else weather_df.iloc[0]
    return {
        "TEMP":   round(float(row["temperature"] or 20.0), 1),
        "PRCP_H": round(float(row["precipitation"] or 0.0), 1),
        "SNOW_H": round(float(row["snowfall"] or 0.0), 1),
        "WIND":   round(float(row["windspeed"] / 3.6 if row["windspeed"] else 5.0), 1),
        "CLOUD":  round(float(row["cloudcover"] or 50.0), 1),
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

    # ── Wetterdaten zur Abflugstunde extrahieren (passend zu Trainings-Features)
    weather = _get_weather_at_hour(weather_df, dep_hour)

    # ── Distanz bestimmen
    distance_km = DISTANCES.get((origin, destination), 2500)

    # ── Feature-Vektor aufbauen (exakt wie beim Training)
    input_data = {
        "MONTH":               month,
        "DAY_OF_WEEK":         day_of_week,
        "DEP_HOUR":            dep_hour,
        "AIRLINE":             airline,
        "ORIGIN_AIRPORT":      origin,
        "DESTINATION_AIRPORT": destination,
        "DISTANCE_KM":         distance_km,
        "TEMP":                weather["TEMP"],
        "PRCP_H":              weather["PRCP_H"],
        "SNOW_H":              weather["SNOW_H"],
        "WIND":                weather["WIND"],
        "CLOUD":               weather["CLOUD"],
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

    # ── TOP FACTORS generieren ────────────────────────────────────────────────
    top_factors = []

    # Abflugzeit — Rush hours vs. Off-peak
    if 16 <= dep_hour <= 19:
        top_factors.append({"label": f"Afternoon rush hour ({dep_hour:02d}:00)", "impact": "high"})
    elif 7 <= dep_hour <= 9:
        top_factors.append({"label": f"Morning rush hour ({dep_hour:02d}:00)", "impact": "medium"})
    else:
        top_factors.append({"label": f"Off-peak departure ({dep_hour:02d}:00)", "impact": "low"})

    # Airline — basierend auf historischer Verspätungsrate
    airline_name = AIRLINE_NAMES.get(airline, airline)
    _HIGH_DELAY_AIRLINES = {"F9", "EV", "MQ", "NK"}   # >24% historische Verspätungsrate
    _LOW_DELAY_AIRLINES  = {"DL", "AS", "HA"}          # <18% historische Verspätungsrate
    if airline in _HIGH_DELAY_AIRLINES:
        top_factors.append({"label": airline_name, "impact": "high"})
    elif airline in _LOW_DELAY_AIRLINES:
        top_factors.append({"label": airline_name, "impact": "low"})
    else:
        top_factors.append({"label": airline_name, "impact": "medium"})

    # Monat / Saison — Sommer und Feiertage erhöhen Risiko
    if month in [7, 12]:
        top_factors.append({"label": "Peak travel season", "impact": "high"})
    elif month in [6, 8, 11, 3]:
        top_factors.append({"label": "Busy travel period", "impact": "medium"})
    else:
        top_factors.append({"label": "Off-peak season", "impact": "low"})

    # Wetter (stündliche Werte zur Abflugzeit)
    if weather["SNOW_H"] > 0.5 or weather["TEMP"] <= 0:
        top_factors.append({"label": "Snow / Freezing conditions", "impact": "high"})
    elif weather["PRCP_H"] > 2.0 or weather["WIND"] > 13.9:
        top_factors.append({"label": "Heavy rain / Strong winds", "impact": "high"})
    elif weather["PRCP_H"] > 0.3 or weather["CLOUD"] > 85:
        top_factors.append({"label": "Rain / Low visibility", "impact": "medium"})
    else:
        top_factors.append({"label": "Clear / Sunny conditions", "impact": "low"})

    # Wochentag
    weekdays = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
                5: "Friday", 6: "Saturday", 7: "Sunday"}
    weekday_name = weekdays.get(day_of_week, "")
    if day_of_week in [1, 5]:   # Monday & Friday = busy travel days
        top_factors.append({"label": f"{weekday_name} flight", "impact": "medium"})
    else:
        top_factors.append({"label": f"{weekday_name} flight", "impact": "low"})

    return {
        "delay_probability":     round(float(delay_prob), 3),
        "delay_probability_pct": f"{delay_prob:.0%}",
        "delay_category":        delay_category,
        "display_category":      delay_category,
        "is_likely_delayed":     delay_prob >= 0.5,
        "risk_level":            risk_level,
        "risk_color":            risk_color,
        "weather_used":          weather,
        "distance_km":           distance_km,
        "top_factors":           top_factors,
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
