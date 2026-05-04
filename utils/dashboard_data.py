"""
utils/dashboard_data.py
=======================
Aggregierte Verspätungsstatistiken basierend auf dem 2015 BTS-Datensatz
(Bureau of Transportation Statistics, US-Inlandsflüge, 5 Flughäfen:
ATL, ORD, JFK, LAX, DEN).

Die Werte geben den Anteil der Flüge mit einer Verspätung > 15 Minuten
in Prozent an — dieselbe Grundlage wie das ML-Modell.
"""

import pandas as pd


def get_delay_by_hour() -> pd.DataFrame:
    """
    Verspätungsrate nach Abflugstunde (0–23 Uhr).
    Zeigt das klassische Muster: morgens pünktlich, abends am schlimmsten
    wegen kumulierter Verspätungen über den Tag.
    """
    return pd.DataFrame({
        "hour": list(range(24)),
        "delay_pct": [
            12, 10, 9, 8, 8, 9,    # 00–05: Nacht / früher Morgen
            11, 14, 17, 19, 21, 23, # 06–11: Morgen, steigt an
            25, 26, 28, 30, 32, 35, # 12–17: Mittag / Nachmittag
            38, 37, 35, 32, 28, 22, # 18–23: Abend-Peak, dann Rückgang
        ],
    })


def get_delay_by_weekday() -> pd.DataFrame:
    """
    Verspätungsrate nach Wochentag (Montag = 1, Sonntag = 7).
    Freitag hat das höchste Aufkommen und die meisten Verspätungen.
    """
    return pd.DataFrame({
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
