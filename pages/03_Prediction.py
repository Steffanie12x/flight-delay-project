import streamlit as st          # Streamlit für die Web-Oberfläche
import pandas as pd             # Pandas für Datentabellen
from datetime import date       # date-Modul für Datumseingabe
from utils.weather import get_historical_weather, get_forecast_weather, classify_weather_condition
                                # Unsere eigenen Wetterfunktionen importieren

# Titel der Seite
st.title("Prediction Tool")

# Trennlinie
st.markdown("---")

# ── BENUTZER-EINGABEN ──────────────────────────────────────────
st.subheader("Your Flight Details")

# Datumseingabe: Benutzer wählt ein Datum
flight_date = st.date_input(
    "Flight Date",
    value=date.today()          # Standardmässig heutiges Datum vorausgewählt
)

# Stundeneingabe: Benutzer wählt die Abflugstunde (0-23 Uhr)
flight_hour = st.slider(
    "Departure Hour",
    min_value=0,                # Frühester Abflug: 0 Uhr
    max_value=23,               # Spätester Abflug: 23 Uhr
    value=12                    # Standardmässig 12 Uhr vorausgewählt
)

# Trennlinie
st.markdown("---")

# ── WETTERDATEN LADEN ──────────────────────────────────────────

# Datum in String umwandeln (API erwartet Format 'YYYY-MM-DD')
date_str = flight_date.strftime("%Y-%m-%d")

# Prüfen ob das gewählte Datum in der Vergangenheit oder Zukunft liegt
today = date.today()

# Wetterdaten laden mit Fehlerbehandlung
try:
    if flight_date <= today:
        # Datum liegt in der Vergangenheit → historische Daten verwenden
        weather_df = get_historical_weather(date_str)
        st.caption("Weather source: Historical data (Open-Meteo Archive)")
    else:
        # Datum liegt in der Zukunft → Wettervorhersage verwenden
        weather_df = get_forecast_weather(date_str)
        st.caption("Weather source: Forecast data (Open-Meteo Forecast)")

    # ── WETTERKLASSIFIKATION ───────────────────────────────────────
    # Wetterzeile für die gewählte Abflugstunde aus der Tabelle holen
    weather_at_hour = weather_df[weather_df["hour"] == flight_hour].iloc[0]

    # Wetterkategorie für diese Stunde berechnen (z.B. "Heavy Rain", "Good")
    condition = classify_weather_condition(weather_at_hour)

    # Wettericon je nach Kategorie bestimmen (für visuelle Darstellung)
    condition_icons = {
        "Heavy Snow":    "❄️ Heavy Snow",
        "Light Snow":    "🌨️ Light Snow",
        "Heavy Rain":    "🌧️ Heavy Rain",
        "Light Rain":    "🌦️ Light Rain",
        "Strong Wind":   "💨 Strong Wind",
        "Low Visibility":"🌫️ Low Visibility",
        "Good":          "☀️ Good",
    }
    # Icon aus dem Dictionary holen, Fallback auf den rohen Text
    condition_label = condition_icons.get(condition, condition)

    # ── WETTER-ANZEIGE: GEWÄHLTE STUNDE ────────────────────────────
    st.subheader(f"Weather at ZRH – {flight_date} {flight_hour:02d}:00")

    # Wetterkategorie als farbiger Badge anzeigen
    st.markdown(f"**Condition:** {condition_label}")

    # Vier Kennzahlen nebeneinander als Metric-Karten anzeigen
    col1, col2, col3, col4 = st.columns(4)

    # Temperatur in der ersten Spalte
    col1.metric(
        label="🌡️ Temperature",
        value=f"{weather_at_hour['temperature']} °C"
    )

    # Niederschlag in der zweiten Spalte
    col2.metric(
        label="🌧️ Precipitation",
        value=f"{weather_at_hour['precipitation']} mm"
    )

    # Schneefall in der dritten Spalte
    col3.metric(
        label="❄️ Snowfall",
        value=f"{weather_at_hour['snowfall']} cm"
    )

    # Windgeschwindigkeit in der vierten Spalte
    col4.metric(
        label="💨 Wind Speed",
        value=f"{weather_at_hour['windspeed']} km/h"
    )

    # Zweite Zeile: Bewölkung
    col5, col6, col7, col8 = st.columns(4)

    # Bewölkung in der ersten Spalte der zweiten Zeile
    col5.metric(
        label="☁️ Cloud Cover",
        value=f"{weather_at_hour['cloudcover']} %"
    )

    # ── TAGESÜBERSICHT ──────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Full Day Overview")

    # Kopie des DataFrames erstellen, damit wir das Original nicht verändern
    display_df = weather_df.copy()

    # Tageszeit-Icon zur Stunde hinzufügen (Nacht / Morgen / Tag / Abend)
    def hour_label(h):
        if 0 <= h < 6:
            return f"🌙 {h:02d}:00"   # Nacht: 0–5 Uhr
        elif 6 <= h < 12:
            return f"🌅 {h:02d}:00"   # Morgen: 6–11 Uhr
        elif 12 <= h < 19:
            return f"☀️ {h:02d}:00"   # Tag: 12–18 Uhr
        else:
            return f"🌆 {h:02d}:00"   # Abend: 19–23 Uhr

    # Stundenspalte durch lesbare Labels ersetzen
    display_df["hour"] = display_df["hour"].apply(hour_label)

    # Wetterkategorie mit Icon für jede Zeile berechnen und als neue Spalte hinzufügen
    display_df["condition"] = weather_df.apply(classify_weather_condition, axis=1).map({
        "Heavy Snow":    "❄️ Heavy Snow",
        "Light Snow":    "🌨️ Light Snow",
        "Heavy Rain":    "🌧️ Heavy Rain",
        "Light Rain":    "🌦️ Light Rain",
        "Strong Wind":   "💨 Strong Wind",
        "Low Visibility":"🌫️ Low Visibility",
        "Good":          "☀️ Good",
    })

    # Spaltenreihenfolge festlegen: Stunde und Condition zuerst, dann Messwerte
    display_df = display_df[["hour", "condition", "temperature", "precipitation", "snowfall", "windspeed", "cloudcover"]]

    # Tabelle mit Streamlit column_config anzeigen:
    # - Fortschrittsbalken für Bewölkung
    # - Einheiten in den Spaltenköpfen
    # - gewählte Abflugstunde ist durch den Balken direkt erkennbar
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            # Stundenspalte umbenennen
            "hour":          st.column_config.TextColumn("🕐 Hour"),
            # Wetterkategorie-Spalte umbenennen
            "condition":     st.column_config.TextColumn("Condition"),
            # Temperatur mit Einheit
            "temperature":   st.column_config.NumberColumn("🌡️ Temp", format="%.1f °C"),
            # Niederschlag mit Einheit
            "precipitation": st.column_config.NumberColumn("🌧️ Rain", format="%.1f mm"),
            # Schneefall mit Einheit
            "snowfall":      st.column_config.NumberColumn("❄️ Snow", format="%.1f cm"),
            # Wind mit Einheit
            "windspeed":     st.column_config.NumberColumn("💨 Wind", format="%.1f km/h"),
            # Bewölkung als Fortschrittsbalken von 0–100%
            "cloudcover":    st.column_config.ProgressColumn(
                "☁️ Clouds",
                format="%d%%",   # Anzeige als Prozentzahl
                min_value=0,     # Minimum: 0% Bewölkung
                max_value=100    # Maximum: 100% Bewölkung
            ),
        }
    )

except Exception as e:
    # Falls die API nicht erreichbar ist oder Fehler zurückgibt
    st.error(f"Fehler beim Laden der Wetterdaten: {e}")
    st.stop()                   # Seite hier stoppen, nichts weiteres ausführen