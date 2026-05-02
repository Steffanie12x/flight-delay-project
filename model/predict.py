"""
model/predict.py
================
Vorhersage-Funktion für die Streamlit App.
Verwendet stündliche Wetterdaten und neue Delay-Kategorien.

ÄNDERUNGEN gegenüber Version 1:
- Neue Kategorien: No Delay / 15-30 / 30-45 / 45-60 / 60-90 / 90+
- Stündliche Wetterdaten (Temperatur, Wind etc. zur Abflugzeit)
- 33% Benchmark-Logik für die Anzeige
"""

import pandas as pd
import joblib
import os
from datetime import datetime

MODEL_DIR = "models"

AIRLINE_NAMES = {
    "AA": "American Airlines",    "AS": "Alaska Airlines",
    "B6": "JetBlue Airways",      "DL": "Delta Air Lines",
    "EV": "Atlantic Southeast Airlines", "F9": "Frontier Airlines",
    "HA": "Hawaiian Airlines",    "MQ": "American Eagle Airlines",
    "NK": "Spirit Air Lines",     "OO": "Skywest Airlines",
    "UA": "United Air Lines",     "US": "US Airways",
    "VX": "Virgin America",       "WN": "Southwest Airlines",
}

DISTANCES = {
    ("ATL", "ORD"): 1527, ("ATL", "JFK"): 1524, ("ATL", "LAX"): 3118, ("ATL", "DEN"): 2180,
    ("ORD", "ATL"): 1527, ("ORD", "JFK"): 1189, ("ORD", "LAX"): 2808, ("ORD", "DEN"): 1474,
    ("JFK", "ATL"): 1524, ("JFK", "ORD"): 1189, ("JFK", "LAX"): 4500, ("JFK", "DEN"): 2622,
    ("LAX", "ATL"): 3118, ("LAX", "ORD"): 2808, ("LAX", "JFK"): 4500, ("LAX", "DEN"): 1389,
    ("DEN", "ATL"): 2180, ("DEN", "ORD"): 1474, ("DEN", "JFK"): 2622, ("DEN", "LAX"): 1389,
}

# Benchmark: unter 33% → "Low Risk / No Delay erwartet"
DELAY_BENCHMARK = 0.33


# ─────────────────────────────────────────────
# 1. MODELLE LADEN
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# 2. WETTER VORBEREITEN
# ─────────────────────────────────────────────

def _get_weather_at_hour(weather_df: pd.DataFrame, dep_hour: int) -> dict:
    """
    Holt die Wetterdaten zur exakten Abflugstunde aus dem DataFrame.
    Das ist neu — statt Tagesdurchschnitt verwenden wir die exakte Stunde!
    """
    row = weather_df[weather_df["hour"] == dep_hour]

    if row.empty:
        # Fallback: nächste verfügbare Stunde
        row = weather_df.iloc[0]
    else:
        row = row.iloc[0]

    return {
        "TEMP":   float(row["temperature"] or 20.0),
        "PRCP_H": float(row["precipitation"] or 0.0),
        "SNOW_H": float(row["snowfall"] or 0.0),
        "WIND":   float(row["windspeed"] / 3.6 if row["windspeed"] else 5.0),  # km/h → m/s
        "CLOUD":  float(row["cloudcover"] or 50.0),
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
        Dictionary mit Vorhersage + Anzeigelogik (33% Benchmark)
    """
    if _binary_model is None:
        return {"error": "Modell nicht geladen. Sind die .pkl Dateien im models/ Ordner?"}

    # Datum verarbeiten
    if isinstance(flight_date, str):
        dt = datetime.strptime(flight_date, "%Y-%m-%d")
    else:
        dt = datetime.combine(flight_date, datetime.min.time())

    month       = dt.month
    day_of_week = dt.isoweekday()

    # Wetter zur exakten Abflugstunde holen
    weather = _get_weather_at_hour(weather_df, dep_hour)

    # Distanz bestimmen
    distance_km = DISTANCES.get((origin, destination), 2500)

    # Feature-Vektor aufbauen
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
    df = df[[f for f in _feature_list if f in df.columns]]

    # Text-Spalten encodieren
    for col, encoder in _encoders.items():
        if col in df.columns:
            known  = set(encoder.classes_)
            df[col] = df[col].apply(lambda x: x if x in known else encoder.classes_[0])
            df[col] = encoder.transform(df[col].astype(str))

    # Vorhersage 1: Wahrscheinlichkeit
    delay_prob = _binary_model.predict_proba(df)[0][1]

    # Vorhersage 2: Wahrscheinlichkeiten aller Kategorien
    all_probs  = _multi_model.predict_proba(df)[0]
    categories = _multi_model._label_encoder.classes_

    # Wahrscheinlichste Kategorie
    best_idx      = all_probs.argmax()
    best_category = categories[best_idx]
    best_prob     = all_probs[best_idx]

    # ── 33% BENCHMARK LOGIK ──────────────────────────────────────────────────
    # Unter 33% → "Low Risk, No Delay erwartet"
    # Über 33%  → wahrscheinlichste Kategorie anzeigen
    if delay_prob < DELAY_BENCHMARK:
        display_mode     = "low_risk"
        display_category = "No Delay"
        display_prob     = 1 - delay_prob   # Wahrscheinlichkeit KEIN Delay
        risk_level       = "Low"
        risk_color       = "#10B981"        # Grün
    else:
        display_mode     = "show_category"
        display_category = best_category
        display_prob     = best_prob
        if delay_prob < 0.55:
            risk_level, risk_color = "Medium", "#F59E0B"   # Orange
        else:
            risk_level, risk_color = "High",   "#EF4444"   # Rot

    return {
        # Rohwerte
        "delay_probability":     round(float(delay_prob), 3),
        "delay_probability_pct": f"{delay_prob:.0%}",

        # Anzeigelogik (33% Benchmark)
        "display_mode":          display_mode,
        "display_category":      display_category,
        "display_prob":          round(float(display_prob), 3),
        "display_prob_pct":      f"{display_prob:.0%}",

        # Risiko
        "risk_level":            risk_level,
        "risk_color":            risk_color,

        # Alle Kategorien mit Wahrscheinlichkeiten (für Details)
        "all_categories": {
            cat: round(float(prob), 3)
            for cat, prob in zip(categories, all_probs)
        },

        # Kontext
        "weather_used":          weather,
        "distance_km":           distance_km,
        "is_likely_delayed":     delay_prob >= 0.5,
    }


# ─────────────────────────────────────────────
# 4. HILFSFUNKTIONEN FÜR DROPDOWNS
# ─────────────────────────────────────────────

def get_airline_options() -> dict:
    """Gibt {voller Name: Code} zurück für Streamlit Selectbox."""
    if _encoders and "AIRLINE" in _encoders:
        codes = sorted(_encoders["AIRLINE"].classes_.tolist())
    else:
        codes = list(AIRLINE_NAMES.keys())
    return {AIRLINE_NAMES.get(c, c): c for c in codes}


def get_destination_options(origin: str) -> dict:
    """Gibt mögliche Ziele zurück (ohne Abflughafen selbst)."""
    all_airports = {
        "Atlanta (ATL)":        "ATL",
        "Chicago O'Hare (ORD)": "ORD",
        "New York JFK (JFK)":   "JFK",
        "Los Angeles (LAX)":    "LAX",
        "Denver (DEN)":         "DEN",
    }
    return {name: code for name, code in all_airports.items() if code != origin}
