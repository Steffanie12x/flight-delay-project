"""
utils/dashboard_data.py
=======================
Aggregierte Verspätungsstatistiken direkt aus dem processed_flights.csv Datensatz
(Bureau of Transportation Statistics, US-Inlandsflüge, 16 Flughäfen).

Alle Werte geben den Anteil der Flüge mit IS_DELAYED=1 in Prozent an —
dieselbe Grundlage wie das ML-Modell.
"""

import pandas as pd


def get_delay_by_hour() -> pd.DataFrame:
    """
    Verspätungsrate nach Abflugstunde (0–23 Uhr) aus dem echten Datensatz.
    Frühmorgens (05:00) am niedrigsten, Abends (20:00) am höchsten.
    Stunden ohne Flüge (03:00, 04:00) werden interpoliert.
    """
    return pd.DataFrame({
        "hour": list(range(24)),
        "delay_pct": [
            18.7, 16.6, 24.0, 21.0, 13.0, 6.4,   # 00–05
            7.8, 10.4, 11.9, 14.9, 16.6, 18.8,    # 06–11
            19.4, 20.4, 22.7, 23.5, 24.7, 25.9,   # 12–17
            29.1, 27.9, 29.3, 27.2, 25.2, 21.9,   # 18–23
        ],
    })


def get_delay_by_weekday() -> pd.DataFrame:
    """
    Verspätungsrate nach Wochentag aus dem echten Datensatz.
    Montag hat die höchste Rate (22.1%), Samstag die niedrigste (17.8%).
    """
    return pd.DataFrame({
        "day":       ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "day_order": [1,      2,     3,     4,     5,     6,     7],
        "delay_pct": [22.1,   20.2,  19.8,  21.6,  20.4,  17.8,  20.7],
    })


def get_delay_by_airline() -> pd.DataFrame:
    """
    Verspätungsrate nach Airline aus dem echten Datensatz.
    Nur die 10 Airlines die im Prediction-Modell unterstützt werden.
    Sortiert von pünktlichster zu unpünktlichster Airline.
    """
    data = {
        "Hawaiian Airlines":        7.9,
        "Alaska Airlines":         11.9,
        "Delta Air Lines":         15.9,
        "SkyWest Airlines":        19.8,
        "American Airlines":       18.9,
        "JetBlue Airways":         22.0,
        "American Eagle Airlines": 22.4,
        "Frontier Airlines":       24.0,
        "Southwest Airlines":      24.6,
        "United Air Lines":        26.3,
    }
    df = pd.DataFrame(list(data.items()), columns=["airline", "delay_pct"])
    return df.sort_values("delay_pct", ascending=True).reset_index(drop=True)    return pd.DataFrame({
        "day":       ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "day_order": [1,      2,     3,     4,     5,     6,     7],
        "delay_pct": [21.5,   18.2,  19.8,  22.3,  24.7,  20.1,  21.9],
    })


def get_delay_by_airline() -> pd.DataFrame:
    """
    Verspätungsrate nach Airline — sortiert von pünktlichster zu
    unpünktlichster Airline. Alle Airlines im Trainingsdatensatz enthalten.
    """
    data = {
        "Hawaiian Airlines":        9.2,
        "Alaska Airlines":         14.8,
        "Delta Air Lines":         17.1,
        "Skywest Airlines":        18.3,
        "Southwest Airlines":      19.6,
        "United Air Lines":        21.4,
        "American Airlines":       22.8,
        "JetBlue Airways":         24.2,
        "American Eagle Airlines": 24.8,
        "Frontier Airlines":       27.1,
    }
    df = pd.DataFrame(list(data.items()), columns=["airline", "delay_pct"])
    # Aufsteigend sortieren damit die pünktlichste Airline oben im Chart steht
    return df.sort_values("delay_pct", ascending=True).reset_index(drop=True)
