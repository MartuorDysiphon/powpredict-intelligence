"""
Live weather for Johannesburg, pulled from Open-Meteo (no API key needed).

Weather does NOT influence lottery draws. This is display-only context.
"""
import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode


JOBURG_LAT = -26.2041
JOBURG_LON = 28.0473
CACHE_SECONDS = 600  # refetch at most every 10 minutes

_cache = {"ts": 0, "data": None}


def get_weather():
    """
    Return dict with current Johannesburg weather, or None on failure.
    Shape:
      {
        "temp_c": 24.3,
        "humidity": 45,
        "wind_kmh": 12.4,
        "pressure_hpa": 1013.2,
        "condition": "Partly cloudy",
        "updated": "HH:MM"
      }
    """
    import time
    now = time.time()
    if _cache["data"] and (now - _cache["ts"]) < CACHE_SECONDS:
        return _cache["data"]

    params = {
        "latitude": JOBURG_LAT,
        "longitude": JOBURG_LON,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure,weather_code",
        "timezone": "Africa/Johannesburg",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)

    try:
        req = Request(url, headers={"User-Agent": "Powpredict/1.0"})
        with urlopen(req, timeout=8) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

    cur = raw.get("current", {})
    data = {
        "temp_c": cur.get("temperature_2m"),
        "humidity": cur.get("relative_humidity_2m"),
        "wind_kmh": cur.get("wind_speed_10m"),
        "pressure_hpa": cur.get("surface_pressure"),
        "condition": _describe(cur.get("weather_code")),
        "updated": (cur.get("time") or "")[-5:] or "--:--",
    }

    _cache["ts"] = now
    _cache["data"] = data
    return data


def _describe(code):
    """Turn WMO weather code into a short label."""
    if code is None:
        return "—"
    table = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime fog",
        51: "Light drizzle",
        53: "Drizzle",
        55: "Heavy drizzle",
        61: "Light rain",
        63: "Rain",
        65: "Heavy rain",
        71: "Light snow",
        73: "Snow",
        75: "Heavy snow",
        80: "Rain showers",
        81: "Heavy showers",
        82: "Violent showers",
        95: "Thunderstorm",
    }
    return table.get(int(code), "—")