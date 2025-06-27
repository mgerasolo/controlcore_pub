import json
import time
from typing import Any, Dict

import requests
import psycopg2


class AgWeatherService:
    """Simple service for storing agricultural weather data."""

    def __init__(self, api_key: str, db_connection: str) -> None:
        self.api_key = api_key
        self.db_connection = db_connection

    def _request(self, url: str, params: Dict[str, Any], retries: int = 3, timeout: int = 10) -> Dict[str, Any] | None:
        """Perform an HTTP GET request with basic retry logic."""
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

    def _ensure_table(self, table: str) -> None:
        conn = psycopg2.connect(self.db_connection)
        cur = conn.cursor()
        cur.execute("CREATE SCHEMA IF NOT EXISTS agriculture")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS agriculture.{table} (
                id SERIAL PRIMARY KEY,
                fetched_at TIMESTAMP DEFAULT NOW(),
                data JSONB
            )
            """
        )
        conn.commit()
        cur.close()
        conn.close()

    def _insert(self, table: str, data: Dict[str, Any]) -> None:
        self._ensure_table(table)
        conn = psycopg2.connect(self.db_connection)
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO agriculture.{table} (data) VALUES (%s)",
            [json.dumps(data)],
        )
        conn.commit()
        cur.close()
        conn.close()

    def fetch_and_store_historical(self, lat: float, lon: float, dt: int) -> Dict[str, Any] | None:
        url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        params = {"lat": lat, "lon": lon, "dt": dt, "appid": self.api_key, "units": "metric"}
        data = self._request(url, params)
        if data is not None:
            self._insert("historical_weather", data)
        return data

    def fetch_and_store_current(self, lat: float, lon: float) -> Dict[str, Any] | None:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
        data = self._request(url, params)
        if data is not None:
            self._insert("current_weather", data)
        return data

    def fetch_and_store_forecast(self, lat: float, lon: float) -> Dict[str, Any] | None:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
        data = self._request(url, params)
        if data is not None:
            self._insert("forecast_weather", data)
        return data
