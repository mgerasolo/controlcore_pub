import json
import time
from typing import Any, Dict, List

import requests
import psycopg2


class AgWeatherService:
    """Retrieve OpenWeather data and store it in an agriculture schema."""

    def __init__(self, api_key: str, db_connection: str) -> None:
        self.api_key = api_key
        self.db_connection = db_connection

    # ------------------------------------------------------------------
    # HTTP helpers
    def _request(self, url: str, params: Dict[str, Any], retries: int = 3, timeout: int = 10) -> Dict[str, Any] | None:
        """Make an HTTP GET request with simple retry logic."""
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, params=params, timeout=timeout)
                if response.status_code == 200:
                    return response.json()
            except requests.RequestException:
                pass
            if attempt < retries:
                time.sleep(attempt)
        return None

    # ------------------------------------------------------------------
    # Database helpers
    def _ensure_hourly_table(self) -> None:
        conn = psycopg2.connect(self.db_connection)
        cur = conn.cursor()
        cur.execute("CREATE SCHEMA IF NOT EXISTS agriculture")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS agriculture.hourly_data (
                id SERIAL PRIMARY KEY,
                dt INTEGER UNIQUE,
                lat NUMERIC(10,6) NOT NULL,
                lon NUMERIC(10,6) NOT NULL,
                tz TEXT NOT NULL,
                tzoff INTEGER NOT NULL,
                sunrise INTEGER NOT NULL,
                sunset INTEGER NOT NULL,
                temp REAL NOT NULL,
                feels_like REAL NOT NULL,
                pressure INTEGER NOT NULL,
                humidity INTEGER NOT NULL,
                dew_point REAL,
                vis REAL,
                description TEXT NOT NULL,
                clouds INTEGER,
                wind_speed REAL,
                wind_deg INTEGER
            )
            """
        )
        conn.commit()
        cur.close()
        conn.close()

    def _ensure_current_table(self) -> None:
        conn = psycopg2.connect(self.db_connection)
        cur = conn.cursor()
        cur.execute("CREATE SCHEMA IF NOT EXISTS agriculture")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS agriculture.current_weather (
                id SERIAL PRIMARY KEY,
                dt INTEGER UNIQUE,
                lat NUMERIC(10,6) NOT NULL,
                lon NUMERIC(10,6) NOT NULL,
                temp REAL,
                feels_like REAL,
                pressure INTEGER,
                humidity INTEGER,
                visibility REAL,
                description TEXT,
                clouds INTEGER,
                wind_speed REAL,
                wind_deg INTEGER,
                fetched_at TIMESTAMP DEFAULT NOW()
            )
            """
        )
        conn.commit()
        cur.close()
        conn.close()

    def _ensure_forecast_table(self) -> None:
        conn = psycopg2.connect(self.db_connection)
        cur = conn.cursor()
        cur.execute("CREATE SCHEMA IF NOT EXISTS agriculture")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS agriculture.forecast_weather (
                id SERIAL PRIMARY KEY,
                dt INTEGER,
                lat NUMERIC(10,6) NOT NULL,
                lon NUMERIC(10,6) NOT NULL,
                temp REAL,
                feels_like REAL,
                pressure INTEGER,
                humidity INTEGER,
                visibility REAL,
                description TEXT,
                clouds INTEGER,
                wind_speed REAL,
                wind_deg INTEGER,
                fetched_at TIMESTAMP DEFAULT NOW()
            )
            """
        )
        conn.commit()
        cur.close()
        conn.close()

    # Insert helpers ----------------------------------------------------
    def _insert_hourly(self, data: Dict[str, Any]) -> None:
        self._ensure_hourly_table()
        conn = psycopg2.connect(self.db_connection)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO agriculture.hourly_data (
                dt, lat, lon, tz, tzoff, sunrise, sunset, temp,
                feels_like, pressure, humidity, dew_point, vis,
                description, clouds, wind_speed, wind_deg
            )
            VALUES (
                %(dt)s, %(lat)s, %(lon)s, %(tz)s, %(tzoff)s, %(sunrise)s, %(sunset)s,
                %(temp)s, %(feels_like)s, %(pressure)s, %(humidity)s, %(dew_point)s,
                %(vis)s, %(description)s, %(clouds)s, %(wind_speed)s, %(wind_deg)s
            )
            ON CONFLICT (dt) DO NOTHING
            """,
            data,
        )
        conn.commit()
        cur.close()
        conn.close()

    def _insert_current(self, data: Dict[str, Any]) -> None:
        self._ensure_current_table()
        conn = psycopg2.connect(self.db_connection)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO agriculture.current_weather (
                dt, lat, lon, temp, feels_like, pressure, humidity,
                visibility, description, clouds, wind_speed, wind_deg
            )
            VALUES (
                %(dt)s, %(lat)s, %(lon)s, %(temp)s, %(feels_like)s, %(pressure)s,
                %(humidity)s, %(visibility)s, %(description)s, %(clouds)s,
                %(wind_speed)s, %(wind_deg)s
            )
            ON CONFLICT (dt) DO NOTHING
            """,
            data,
        )
        conn.commit()
        cur.close()
        conn.close()

    def _insert_forecast(self, data: List[Dict[str, Any]]) -> None:
        self._ensure_forecast_table()
        conn = psycopg2.connect(self.db_connection)
        cur = conn.cursor()
        for entry in data:
            cur.execute(
                """
                INSERT INTO agriculture.forecast_weather (
                    dt, lat, lon, temp, feels_like, pressure, humidity,
                    visibility, description, clouds, wind_speed, wind_deg
                )
                VALUES (
                    %(dt)s, %(lat)s, %(lon)s, %(temp)s, %(feels_like)s,
                    %(pressure)s, %(humidity)s, %(visibility)s, %(description)s,
                    %(clouds)s, %(wind_speed)s, %(wind_deg)s
                )
                """,
                entry,
            )
        conn.commit()
        cur.close()
        conn.close()

    # ------------------------------------------------------------------
    # Public API --------------------------------------------------------
    def fetch_and_store_historical(self, lat: float, lon: float, dt: int) -> Dict[str, Any] | None:
        url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        params = {"lat": lat, "lon": lon, "dt": dt, "appid": self.api_key, "units": "metric"}
        data = self._request(url, params)
        if not data or "data" not in data:
            return None
        weather = data["data"][0]
        record = {
            "dt": weather.get("dt"),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "tz": data.get("timezone", ""),
            "tzoff": data.get("timezone_offset", 0),
            "sunrise": weather.get("sunrise"),
            "sunset": weather.get("sunset"),
            "temp": weather.get("temp"),
            "feels_like": weather.get("feels_like"),
            "pressure": weather.get("pressure"),
            "humidity": weather.get("humidity"),
            "dew_point": weather.get("dew_point"),
            "vis": weather.get("visibility", 0),
            "description": weather.get("weather", [{}])[0].get("description", ""),
            "clouds": weather.get("clouds"),
            "wind_speed": weather.get("wind_speed"),
            "wind_deg": weather.get("wind_deg"),
        }
        self._insert_hourly(record)
        return data

    def fetch_and_store_current(self, lat: float, lon: float) -> Dict[str, Any] | None:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
        data = self._request(url, params)
        if not data:
            return None
        record = {
            "dt": data.get("dt"),
            "lat": data.get("coord", {}).get("lat"),
            "lon": data.get("coord", {}).get("lon"),
            "temp": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "pressure": data.get("main", {}).get("pressure"),
            "humidity": data.get("main", {}).get("humidity"),
            "visibility": data.get("visibility"),
            "description": (data.get("weather") or [{}])[0].get("description"),
            "clouds": data.get("clouds", {}).get("all"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "wind_deg": data.get("wind", {}).get("deg"),
        }
        self._insert_current(record)
        return data

    def fetch_and_store_forecast(self, lat: float, lon: float) -> Dict[str, Any] | None:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
        data = self._request(url, params)
        if not data or "list" not in data:
            return None
        records = []
        for entry in data["list"]:
            records.append(
                {
                    "dt": entry.get("dt"),
                    "lat": lat,
                    "lon": lon,
                    "temp": entry.get("main", {}).get("temp"),
                    "feels_like": entry.get("main", {}).get("feels_like"),
                    "pressure": entry.get("main", {}).get("pressure"),
                    "humidity": entry.get("main", {}).get("humidity"),
                    "visibility": entry.get("visibility"),
                    "description": (entry.get("weather") or [{}])[0].get("description"),
                    "clouds": entry.get("clouds", {}).get("all"),
                    "wind_speed": entry.get("wind", {}).get("speed"),
                    "wind_deg": entry.get("wind", {}).get("deg"),
                }
            )
        self._insert_forecast(records)
        return data
