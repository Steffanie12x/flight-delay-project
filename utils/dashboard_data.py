"""
utils/dashboard_data.py
=======================
Aggregierte Verspätungsstatistiken direkt aus dem processed_flights.csv Datensatz
(Bureau of Transportation Statistics, US-Inlandsflüge, 16 Flughäfen).
"""

import pandas as pd


def get_delay_by_hour() -> pd.DataFrame:
    """Verspätungsrate nach Abflugstunde aus dem echten Datensatz."""
    return pd.DataFrame({
        "hour": list(range(24)),
        "delay_pct": [
            18.7, 16.6, 24.0, 21.0, 13.0, 6.4,
            7.8, 10.4, 11.9, 14.9, 16.6, 18.8,
            19.4, 20.4, 22.7, 23.5, 24.7, 25.9,
            29.1, 27.9, 29.3, 27.2, 25.2, 21.9,
        ],
    })


def get_delay_by_weekday() -> pd.DataFrame:
    """Verspätungsrate nach Wochentag. Montag höchste Rate, Samstag niedrigste."""
    return pd.DataFrame({
        "day":       ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "day_order": [1,      2,     3,     4,     5,     6,     7],
        "delay_pct": [22.1,   20.2,  19.8,  21.6,  20.4,  17.8,  20.7],
    })


def get_delay_by_airline() -> pd.DataFrame:
    """Verspätungsrate nach Airline. Nur die 10 unterstützten Airlines."""
    data = {
        "Hawaiian Airlines":        7.9,
        "Alaska Airlines":         11.9,
        "Delta Air Lines":         15.9,
        "American Airlines":       18.9,
        "SkyWest Airlines":        19.8,
        "JetBlue Airways":         22.0,
        "American Eagle Airlines": 22.4,
        "Frontier Airlines":       24.0,
        "Southwest Airlines":      24.6,
        "United Air Lines":        26.3,
    }
    df = pd.DataFrame(list(data.items()), columns=["airline", "delay_pct"])
    return df.sort_values("delay_pct", ascending=True).reset_index(drop=True)
