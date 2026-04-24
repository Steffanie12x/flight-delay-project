"""
utils/weather.py
================
Holt stündliche Wetterdaten für die 5 US-Flughäfen via Open-Meteo API.
Kein API-Key nötig — Open-Meteo ist kostenlos.

Verwendung:
    from utils.weather import get_weather, classify_weather_condition
    df = get_weather("JFK", "2026-05-15")
"""

import requests
import pandas as pd
from datetime import date, datetime

# ── Koordinaten der 5 Flughäfen ───────────────────────────────────────────────
AIRPORT_COORDS = {
    "ATL": {"lat": 33.6407, "lon": -84.4277, "name": "Atlanta (ATL)"},
    "ORD": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago O'Hare (ORD)"},
    "JFK": {"lat": 40.6413, "lon": -73.7781, "name": "New York JFK (JFK)"},
    "LAX": {"lat": 33.9425, "lon": -118.4081, "name": "Los Angeles (LAX)"},
    "DEN": {"lat": 39.8561, "lon": -104.6737, "name": "Denver (DEN)"},
}


def get_weather(airport_code: str, flight_date: str) -> pd.DataFrame:
    """
    Holt stündliche Wetterdaten für einen Flughafen an einem Datum.
    Wählt automatisch historische Daten oder Vorhersage je nach Datum.

    Parameter:
        airport_code: z.B. "JFK", "ATL", "LAX"
        flight_date:  Datum als String "YYYY-MM-DD"

    Rückgabe:
        DataFrame mit 24 Zeilen (eine pro Stunde) und Spalten:
        hour, temperature, precipitation, snowfall, windspeed, cloudcover
    """
    if airport_code not in AIRPORT_COORDS:
        raise ValueError(f"Unbekannter Flughafen: {airport_code}. Erlaubt: {list(AIRPORT_COORDS.keys())}")

    coords = AIRPORT_COORDS[airport_code]
    target = datetime.strptime(flight_date, "%Y-%m-%d").date()
    today  = date.today()

    # Historische Daten oder Vorhersage je nach Datum
    if target <= today:
        url = "https://archive-api.open-meteo.com/v1/archive"
    else:
        url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude":   coords["lat"],
        "longitude":  coords["lon"],
        "start_date": flight_date,
        "end_date":   flight_date,
        "hourly":     "temperature_2m,precipitation,snowfall,windspeed_10m,cloudcover",
        "timezone":   "America/New_York",   # US-Zeitzone
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame({
        "hour":          range(24),
        "temperature":   data["hourly"]["temperature_2m"],
        "precipitation": data["hourly"]["precipitation"],
        "snowfall":      data["hourly"]["snowfall"],
        "windspeed":     data["hourly"]["windspeed_10m"],
        "cloudcover":    data["hourly"]["cloudcover"],
    })

    return df


def classify_weather_condition(row) -> str:
    """
    Klassifiziert das Wetter einer Stunde in eine lesbare Kategorie.

    Parameter:
        row: eine Zeile aus dem Weather-DataFrame

    Rückgabe:
        String wie "Heavy Rain", "Good", "Heavy Snow", etc.
    """
    if row["snowfall"] is not None and row["snowfall"] > 0.5:
        return "Heavy Snow"
    elif row["snowfall"] is not None and row["snowfall"] > 0:
        return "Light Snow"
    elif row["precipitation"] is not None and row["precipitation"] > 2.0:
        return "Heavy Rain"
    elif row["precipitation"] is not None and row["precipitation"] > 0.5:
        return "Light Rain"
    elif row["windspeed"] is not None and row["windspeed"] > 50:
        return "Strong Wind"
    elif row["cloudcover"] is not None and row["cloudcover"] > 80:
        return "Overcast"
    else:
        return "Good"


def get_airport_name(airport_code: str) -> str:
    """Gibt den vollen Namen eines Flughafens zurück."""
    return AIRPORT_COORDS.get(airport_code, {}).get("name", airport_code)


def get_airport_list() -> dict:
    """Gibt alle Flughäfen als Dictionary zurück: {Name: Code}"""
    return {v["name"]: k for k, v in AIRPORT_COORDS.items()}
