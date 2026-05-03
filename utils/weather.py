"""
utils/weather.py
================
Stündliche Wetterdaten für 16 US-Flughäfen via Open-Meteo API.
"""

import requests
import pandas as pd
from datetime import date, datetime

AIRPORT_COORDS = {
    "ATL": {"lat": 33.6407,  "lon": -84.4277,  "name": "Atlanta (ATL)"},
    "ORD": {"lat": 41.9742,  "lon": -87.9073,  "name": "Chicago O'Hare (ORD)"},
    "DFW": {"lat": 32.8998,  "lon": -97.0403,  "name": "Dallas Fort Worth (DFW)"},
    "DEN": {"lat": 39.8561,  "lon": -104.6737, "name": "Denver (DEN)"},
    "LAX": {"lat": 33.9425,  "lon": -118.4081, "name": "Los Angeles (LAX)"},
    "SFO": {"lat": 37.6213,  "lon": -122.3790, "name": "San Francisco (SFO)"},
    "PHX": {"lat": 33.4373,  "lon": -112.0078, "name": "Phoenix (PHX)"},
    "IAH": {"lat": 29.9902,  "lon": -95.3368,  "name": "Houston (IAH)"},
    "LAS": {"lat": 36.0840,  "lon": -115.1537, "name": "Las Vegas (LAS)"},
    "MSP": {"lat": 44.8848,  "lon": -93.2223,  "name": "Minneapolis (MSP)"},
    "MCO": {"lat": 28.4294,  "lon": -81.3089,  "name": "Orlando (MCO)"},
    "SEA": {"lat": 47.4502,  "lon": -122.3088, "name": "Seattle (SEA)"},
    "DTW": {"lat": 42.2162,  "lon": -83.3554,  "name": "Detroit (DTW)"},
    "BOS": {"lat": 42.3656,  "lon": -71.0096,  "name": "Boston (BOS)"},
    "EWR": {"lat": 40.6895,  "lon": -74.1745,  "name": "Newark (EWR)"},
    "JFK": {"lat": 40.6413,  "lon": -73.7781,  "name": "New York JFK (JFK)"},
}

MAX_FORECAST_DAYS = 16
HISTORICAL_YEARS  = [2024, 2023, 2022]


def get_weather(airport_code: str, flight_date: str) -> pd.DataFrame:
    if airport_code not in AIRPORT_COORDS:
        raise ValueError(f"Unbekannter Flughafen: {airport_code}")
    coords     = AIRPORT_COORDS[airport_code]
    target     = datetime.strptime(flight_date, "%Y-%m-%d").date()
    today      = date.today()
    days_ahead = (target - today).days
    if target <= today:
        return _fetch_archive(coords, flight_date)
    elif days_ahead <= MAX_FORECAST_DAYS:
        return _fetch_forecast(coords, flight_date)
    else:
        return _get_historical_day_average(coords, target)


def _fetch_archive(coords, flight_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": coords["lat"], "longitude": coords["lon"],
        "start_date": flight_date, "end_date": flight_date,
        "hourly": "temperature_2m,precipitation,snowfall,windspeed_10m,cloudcover",
        "timezone": "America/New_York",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return _parse_hourly(response.json())


def _fetch_forecast(coords, flight_date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"], "longitude": coords["lon"],
        "start_date": flight_date, "end_date": flight_date,
        "hourly": "temperature_2m,precipitation,snowfall,windspeed_10m,cloudcover",
        "timezone": "America/New_York",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return _parse_hourly(response.json())


def _parse_hourly(data):
    return pd.DataFrame({
        "hour":          range(24),
        "temperature":   data["hourly"]["temperature_2m"],
        "precipitation": data["hourly"]["precipitation"],
        "snowfall":      data["hourly"]["snowfall"],
        "windspeed":     data["hourly"]["windspeed_10m"],
        "cloudcover":    data["hourly"]["cloudcover"],
    })


def _get_historical_day_average(coords, target):
    all_days = []
    for year in HISTORICAL_YEARS:
        try:
            historical_date = target.replace(year=year)
        except ValueError:
            historical_date = target.replace(year=year, day=28)
        try:
            df = _fetch_archive(coords, historical_date.strftime("%Y-%m-%d"))
            all_days.append(df)
        except Exception:
            continue
    if not all_days:
        return _simple_fallback(target.month)
    combined  = pd.concat(all_days)
    daily_avg = combined[["temperature", "precipitation", "snowfall", "windspeed", "cloudcover"]].mean().round(1)
    rows = []
    for h in range(24):
        rows.append({
            "hour": h,
            "temperature":   daily_avg["temperature"],
            "precipitation": daily_avg["precipitation"],
            "snowfall":      daily_avg["snowfall"],
            "windspeed":     daily_avg["windspeed"],
            "cloudcover":    daily_avg["cloudcover"],
        })
    return pd.DataFrame(rows)


def _simple_fallback(month):
    monthly = {
        1: (4,-4,0.12,25), 2: (6,-2,0.10,23), 3: (12,3,0.13,22),
        4: (17,7,0.12,20), 5: (22,12,0.13,18), 6: (27,17,0.11,16),
        7: (30,20,0.13,15), 8: (29,19,0.12,15), 9: (25,15,0.11,17),
        10: (18,8,0.10,19), 11: (11,2,0.11,22), 12: (5,-3,0.12,24),
    }
    tmax, tmin, prcp_h, wind = monthly.get(month, (20,10,0.10,20))
    rows = []
    for h in range(24):
        if 6 <= h <= 14:   temp = tmin + (tmax-tmin)*(h-6)/8
        elif 14 < h <= 20: temp = tmax - (tmax-tmin)*(h-14)/6
        else:              temp = tmin
        rows.append({"hour": h, "temperature": round(temp,1),
                     "precipitation": prcp_h, "snowfall": 0.1 if month in [12,1,2] else 0.0,
                     "windspeed": float(wind), "cloudcover": 50})
    return pd.DataFrame(rows)


def classify_weather_condition(row):
    if row["snowfall"] is not None and row["snowfall"] > 0.5:   return "Heavy Snow"
    elif row["snowfall"] is not None and row["snowfall"] > 0:   return "Light Snow"
    elif row["precipitation"] is not None and row["precipitation"] > 2.0: return "Heavy Rain"
    elif row["precipitation"] is not None and row["precipitation"] > 0.5: return "Light Rain"
    elif row["windspeed"] is not None and row["windspeed"] > 50:          return "Strong Wind"
    elif row["cloudcover"] is not None and row["cloudcover"] > 80:        return "Overcast"
    else: return "Good"


def get_airport_name(airport_code):
    return AIRPORT_COORDS.get(airport_code, {}).get("name", airport_code)


def get_airport_list():
    return {v["name"]: k for k, v in AIRPORT_COORDS.items()}
