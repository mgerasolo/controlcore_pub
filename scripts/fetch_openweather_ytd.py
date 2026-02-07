#!/usr/bin/env python3
"""Fetch YTD weather data from OpenWeather API for Fincastle and Roanoke."""

import os
import time
import requests
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_KEY = os.getenv("OPENWEATHER_API_KEY")
PG_HOST = os.getenv("PG_HOST", "10.0.0.33")
PG_PORT = os.getenv("PG_PORT", "3353")
PG_USER = os.getenv("PG_USER", "forecaster")
PG_PASSWORD = os.getenv("PG_PASSWORD")

# Locations with coordinates
LOCATIONS = {
    "Fincastle": {"lat": 37.4993, "lon": -79.877, "id": 1},
    "Roanoke": {"lat": 37.271, "lon": -79.9414, "id": 3},
}

# Date range: YTD (Jan 1, 2026 to today)
START_DATE = datetime(2026, 1, 1)
END_DATE = datetime.now() - timedelta(days=1)  # Yesterday (API doesn't have today yet)

# API rate limiting
DELAY_BETWEEN_CALLS = 1.5  # seconds (to stay well under 60 calls/minute)


def connect_db():
    """Connect to PostgreSQL."""
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname="forecaster"
    )


def fetch_daily_summary(lat: float, lon: float, date: str) -> dict | None:
    """Fetch daily summary from OpenWeather API.

    Uses the One Call API 3.0 Day Summary endpoint.
    https://openweathermap.org/api/one-call-3#history_daily_aggregation
    """
    url = f"https://api.openweathermap.org/data/3.0/onecall/day_summary"
    params = {
        "lat": lat,
        "lon": lon,
        "date": date,
        "appid": API_KEY,
        "units": "imperial"  # Fahrenheit
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"  API error for {date}: {e}")
        return None


def parse_daily_data(data: dict, location_id: int, date: str) -> tuple | None:
    """Parse API response into database row."""
    if not data:
        return None

    try:
        temp = data.get("temperature", {})
        precip = data.get("precipitation", {})
        humidity = data.get("humidity", {})
        wind = data.get("wind", {})

        return (
            location_id,
            date,
            temp.get("min"),
            temp.get("max"),
            temp.get("afternoon"),
            precip.get("total", 0),
            humidity.get("afternoon"),
            wind.get("max", {}).get("speed"),
            wind.get("max", {}).get("direction"),
        )
    except (KeyError, TypeError) as e:
        print(f"  Parse error: {e}")
        return None


def insert_weather_data(conn, rows: list[tuple]):
    """Insert weather data into database."""
    insert_sql = """
        INSERT INTO daily_summary_data
        (location_id, date, temperature_min, temperature_max, temperature_afternoon,
         precipitation_total, humidity_afternoon, wind_max_speed, wind_max_direction)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (location_id, date) DO UPDATE SET
            temperature_min = EXCLUDED.temperature_min,
            temperature_max = EXCLUDED.temperature_max,
            temperature_afternoon = EXCLUDED.temperature_afternoon,
            precipitation_total = EXCLUDED.precipitation_total,
            humidity_afternoon = EXCLUDED.humidity_afternoon,
            wind_max_speed = EXCLUDED.wind_max_speed,
            wind_max_direction = EXCLUDED.wind_max_direction
    """

    with conn.cursor() as cur:
        for row in rows:
            cur.execute(insert_sql, row)
    conn.commit()


def main():
    print(f"OpenWeather YTD Data Fetcher")
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"Locations: {', '.join(LOCATIONS.keys())}")

    # Calculate total API calls
    days = (END_DATE - START_DATE).days + 1
    total_calls = days * len(LOCATIONS)
    print(f"Total API calls needed: {total_calls}")
    print()

    conn = connect_db()

    # First, add unique constraint if not exists
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DO $$ BEGIN
                    ALTER TABLE daily_summary_data
                    ADD CONSTRAINT daily_summary_unique UNIQUE (location_id, date);
                EXCEPTION
                    WHEN duplicate_table THEN NULL;
                    WHEN duplicate_object THEN NULL;
                END $$;
            """)
        conn.commit()
    except Exception as e:
        print(f"Note: {e}")
        conn.rollback()

    all_rows = []
    api_calls = 0

    for location_name, loc_info in LOCATIONS.items():
        print(f"\nFetching data for {location_name}...")
        lat, lon, loc_id = loc_info["lat"], loc_info["lon"], loc_info["id"]

        current_date = START_DATE
        while current_date <= END_DATE:
            date_str = current_date.strftime("%Y-%m-%d")
            print(f"  {date_str}...", end=" ")

            data = fetch_daily_summary(lat, lon, date_str)
            api_calls += 1

            if data:
                row = parse_daily_data(data, loc_id, date_str)
                if row:
                    all_rows.append(row)
                    print("OK")
                else:
                    print("parse error")
            else:
                print("no data")

            # Rate limiting
            time.sleep(DELAY_BETWEEN_CALLS)
            current_date += timedelta(days=1)

    print(f"\n\nInserting {len(all_rows)} rows into database...")
    insert_weather_data(conn, all_rows)
    conn.close()

    print(f"\nDone! Made {api_calls} API calls, inserted {len(all_rows)} rows.")


if __name__ == "__main__":
    main()
