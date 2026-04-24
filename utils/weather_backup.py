import requests       # Bibliothek um HTTP-Anfragen an APIs zu senden
import pandas as pd   # Bibliothek für Datentabellen (DataFrames)

# Koordinaten des Zürich Flughafens für die API-Abfrage
ZRH_LAT = 47.4647    # Breitengrad (Latitude) von ZRH
ZRH_LON = 8.5492     # Längengrad (Longitude) von ZRH


def get_historical_weather(date: str) -> pd.DataFrame:
    """
    Holt historische Wetterdaten für Zürich Flughafen.
    Parameter: date im Format 'YYYY-MM-DD'
    Gibt eine Tabelle mit 24 Zeilen zurück (eine pro Stunde)
    """

    # URL der Open-Meteo API für historische Wetterdaten (kein API-Key nötig)
    url = "https://archive-api.open-meteo.com/v1/archive"

    # Parameter die an die API geschickt werden (was wir anfragen)
    params = {
        "latitude": ZRH_LAT,           # Standort: Breitengrad ZRH
        "longitude": ZRH_LON,          # Standort: Längengrad ZRH
        "start_date": date,            # Startdatum der Abfrage
        "end_date": date,              # Enddatum (gleich wie Start = 1 Tag)
        "hourly": "temperature_2m,precipitation,snowfall,windspeed_10m,cloudcover",
                                       # Welche Wetterwerte wir wollen (stündlich)
        "timezone": "Europe/Zurich"    # Zeitzone für korrekte Uhrzeiten
    }

    # API-Anfrage senden und Antwort empfangen
    response = requests.get(url, params=params)

    # Antwort von JSON-Format in ein Python-Dictionary umwandeln
    data = response.json()

    # Aus den API-Daten eine übersichtliche Tabelle (DataFrame) erstellen
    df = pd.DataFrame({
        "hour": range(24),                              # Stunden 0-23 Uhr
        "temperature": data["hourly"]["temperature_2m"],# Temperatur in °C
        "precipitation": data["hourly"]["precipitation"],# Niederschlag in mm
        "snowfall": data["hourly"]["snowfall"],          # Schneefall in cm
        "windspeed": data["hourly"]["windspeed_10m"],   # Windgeschwindigkeit in km/h
        "cloudcover": data["hourly"]["cloudcover"]      # Bewölkung in Prozent
    })

    return df  # Fertige Tabelle zurückgeben


def get_forecast_weather(date: str) -> pd.DataFrame:
    """
    Holt Wettervorhersage für Zürich Flughafen (für zukünftige Daten).
    Parameter: date im Format 'YYYY-MM-DD'
    Gibt eine Tabelle mit 24 Zeilen zurück (eine pro Stunde)
    """

    # URL der Open-Meteo API für Wettervorhersagen
    url = "https://api.open-meteo.com/v1/forecast"

    # Gleiche Parameter wie bei historischen Daten
    params = {
        "latitude": ZRH_LAT,           # Standort: Breitengrad ZRH
        "longitude": ZRH_LON,          # Standort: Längengrad ZRH
        "start_date": date,            # Startdatum der Vorhersage
        "end_date": date,              # Enddatum (gleich wie Start = 1 Tag)
        "hourly": "temperature_2m,precipitation,snowfall,windspeed_10m,cloudcover",
                                       # Welche Wetterwerte wir wollen (stündlich)
        "timezone": "Europe/Zurich"    # Zeitzone für korrekte Uhrzeiten
    }

    # API-Anfrage senden und Antwort empfangen
    response = requests.get(url, params=params)

    # Antwort von JSON-Format in ein Python-Dictionary umwandeln
    data = response.json()

    # Aus den API-Daten eine übersichtliche Tabelle (DataFrame) erstellen
    df = pd.DataFrame({
        "hour": range(24),                              # Stunden 0-23 Uhr
        "temperature": data["hourly"]["temperature_2m"],# Temperatur in °C
        "precipitation": data["hourly"]["precipitation"],# Niederschlag in mm
        "snowfall": data["hourly"]["snowfall"],          # Schneefall in cm
        "windspeed": data["hourly"]["windspeed_10m"],   # Windgeschwindigkeit in km/h
        "cloudcover": data["hourly"]["cloudcover"]      # Bewölkung in Prozent
    })

    return df  # Fertige Tabelle zurückgeben


def classify_weather_condition(row) -> str:
    """
    Klassifiziert das Wetter einer Stunde in eine Kategorie.
    Wird später vom ML-Modell als zusätzliches Feature verwendet.
    Parameter: row = eine Zeile aus dem Weather-DataFrame
    """

    # Prüft ob Schneefall vorliegt (über 0 cm)
    if row["snowfall"] is not None and row["snowfall"] > 0.5:
        return "Heavy Snow"
    elif row["snowfall"] is not None and row["snowfall"] > 0:
        return "Light Snow"

    # Prüft ob starker Regen vorliegt (über 2mm Niederschlag)
    elif row["precipitation"] is not None and row["precipitation"] > 2.0:
        return "Heavy Rain"

    # Prüft ob leichter Regen vorliegt (zwischen 0.5mm und 2mm)
    elif row["precipitation"] is not None and row["precipitation"] > 0.5:
        return "Light Rain"

    # Prüft ob starker Wind vorliegt (über 50 km/h)
    elif row["windspeed"] is not None and row["windspeed"] > 50:
        return "Strong Wind"

    # Prüft ob starke Bewölkung vorliegt (über 80%)
    elif row["cloudcover"] is not None and row["cloudcover"] > 80:
        return "Low Visibility"

    # Wenn keine der obigen Bedingungen zutrifft: gutes Wetter
    else:
        return "Good"
