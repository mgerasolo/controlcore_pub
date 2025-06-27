import os
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import psycopg2

from shared import load_environment, build_dsn_from_env

load_environment()

BASE_DIR = Path(__file__).resolve().parent.parent

DB_DSN_CONTROLCORE = build_dsn_from_env("controlcore", "CONTROLCORE_USER", "CONTROLCORE_PW")
DB_DSN_HISTORICAL = build_dsn_from_env("openweather_historical", "OPENHIST_USER", "OPENHIST_PW")
DB_DSN_FORECAST = build_dsn_from_env("openweather_forecast", "OPENFORE_USER", "OPENFORE_PW")

def load_zone_configs():
    config_path = BASE_DIR / "configs" / "zones.json"
    with open(config_path) as f:
        return json.load(f)["zones"]

def resolve_location_from_zone(zone):
    location_id = zone.get("location")
    if location_id:
        return location_id
    else:
        print(f"[resolve_location] No location defined for zone {zone['zone_id']}")
        return None

def get_lat_lon_from_location_id(location_id):
    try:
        with psycopg2.connect(DB_DSN_CONTROLCORE) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT lat, lon
                    FROM locations
                    WHERE location_id = %s
                """, (location_id,))
                return cur.fetchone()
    except Exception as e:
        print(f"[get_lat_lon_from_location_id] DB error: {e}")
        return None

def get_weather_context(location_id: str, now: datetime):
    context = {}
    coords = get_lat_lon_from_location_id(location_id)
    if not coords:
        print(f"[get_weather_context] No lat/lon for location_id: {location_id}")
        return context

    lat, lon = coords
    lat_rounded = round(lat, 4)
    lon_rounded = round(lon, 4)

    # === Historical: Yesterday's Summary ===
    try:
        with psycopg2.connect(DB_DSN_HISTORICAL) as conn:
            with conn.cursor() as cur:
                target_unix_day = int((now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
                cur.execute("""
                    SELECT precipitation_total, temperature_afternoon
                    FROM daily_summary_data
                    WHERE date = %s
                      AND ROUND(lat::numeric, 4) = %s
                      AND ROUND(lon::numeric, 4) = %s
                    ORDER BY date DESC
                    LIMIT 1
                """, (target_unix_day, lat_rounded, lon_rounded))
                row = cur.fetchone()
                if row:
                    context["yesterday_rain_mm"] = row[0]
                    context["yesterday_temp_max"] = row[1]
    except Exception as e:
        print(f"[get_weather_context] Historical DB error: {e}")

    # === Forecast: Today and Tomorrow + Hourly Windows ===
    try:
        with psycopg2.connect(DB_DSN_FORECAST) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT timestamp,
                           day_0_temp_max, day_0_pop,
                           day_1_pop, day_1_temp_morn,
                           """ + ", ".join([f"hour_{i}_pop" for i in range(24)]) + """
                    FROM openweather_forecast_detail
                    WHERE ROUND(lat::numeric, 4) = %s
                      AND ROUND(lon::numeric, 4) = %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (lat_rounded, lon_rounded))
                row = cur.fetchone()
                if row:
                    (forecast_time, day_0_temp_max, day_0_pop, day_1_pop, day_1_temp_morn, *hourly_pops) = row
                    context.update({
                        "today_temp_max_forecast": day_0_temp_max,
                        "today_pop": day_0_pop,
                        "tomorrow_pop": day_1_pop,
                        "tomorrow_temp_morn": day_1_temp_morn,
                        "forecast_time": forecast_time,
                    })

                    # Calculate true hour of day for each pop value
                    local_windows = {
                        "early_morning": [],
                        "late_morning": [],
                        "afternoon": [],
                        "evening": []
                    }
                    for i, pop in enumerate(hourly_pops):
                        local_hour = (forecast_time + timedelta(hours=i)).astimezone().hour
                        if 5 <= local_hour < 9:
                            local_windows["early_morning"].append(pop)
                        elif 9 <= local_hour < 12:
                            local_windows["late_morning"].append(pop)
                        elif 12 <= local_hour < 17:
                            local_windows["afternoon"].append(pop)
                        elif 17 <= local_hour < 22:
                            local_windows["evening"].append(pop)

                    context["hourly_pop_windows"] = {
                        k: max(v) if v else 0.0 for k, v in local_windows.items()
                    }
    except Exception as e:
        print(f"[get_weather_context] Forecast DB error: {e}")

    # === Historical: Recent 3-Day Rain Total ===
    try:
        with psycopg2.connect(DB_DSN_HISTORICAL) as conn:
            with conn.cursor() as cur:
                three_days_ago = int((now - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
                cur.execute("""
                    SELECT SUM(precipitation_total)
                    FROM daily_summary_data
                    WHERE date >= %s
                      AND date < %s
                      AND ROUND(lat::numeric, 4) = %s
                      AND ROUND(lon::numeric, 4) = %s
                """, (three_days_ago, int(now.timestamp()), lat_rounded, lon_rounded))
                result = cur.fetchone()
                if result and result[0] is not None:
                    context["recent_rain_mm_last_3_days"] = result[0]
    except Exception as e:
        print(f"[get_weather_context] Historical 3-day rain DB error: {e}")


    return context

if __name__ == "__main__":
    zones = load_zone_configs()
    now = datetime.now(timezone.utc)
    for zone in zones:
        location_id = resolve_location_from_zone(zone)
        if location_id:
            print(f"✅ Zone '{zone['zone_id']}' maps to location: {location_id}")
            summary = get_weather_context(location_id, now)
            print(f"📦 Weather context for '{zone['zone_id']}': {summary}")
