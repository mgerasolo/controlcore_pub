import os
from datetime import datetime, timedelta
import psycopg2

from openweather.src.config.config import WEATHER_DB_CONNECTION
from shared import load_environment

load_environment()

CUTOFF_DAYS = int(os.getenv("OPENWEATHER_ARCHIVE_CUTOFF_DAYS", "30"))
LOCATIONS = [name.strip() for name in os.getenv("OPENWEATHER_ARCHIVE_LOCATIONS", "").split(',') if name.strip()]


def get_location_map(cur):
    cur.execute("SELECT friendly_name, lat_detail, lon_detail FROM locations")
    rows = cur.fetchall()
    mapping = {}
    for friendly, lat, lon in rows:
        key = (round(lat, 4), round(lon, 4))
        mapping[friendly.lower()] = key
    return mapping


def archive_table(cur, src_table, dest_suffix, time_col, cutoff_ts, mapping):
    for friendly, (lat_r, lon_r) in mapping.items():
        if LOCATIONS and friendly not in LOCATIONS:
            continue
        dest_table = f"{friendly}_{dest_suffix}"
        insert_sql = f"INSERT INTO {dest_table} SELECT * FROM {src_table} " \
                    f"WHERE ROUND(lat::numeric,4)=%s AND ROUND(lon::numeric,4)=%s " \
                    f"AND {time_col} < %s ON CONFLICT DO NOTHING"
        cur.execute(insert_sql, (lat_r, lon_r, cutoff_ts))
        delete_sql = f"DELETE FROM {src_table} WHERE ROUND(lat::numeric,4)=%s " \
                    f"AND ROUND(lon::numeric,4)=%s AND {time_col} < %s"
        cur.execute(delete_sql, (lat_r, lon_r, cutoff_ts))


def archive_recent_data():
    cutoff_ts = int((datetime.utcnow() - timedelta(days=CUTOFF_DAYS)).timestamp())
    with psycopg2.connect(WEATHER_DB_CONNECTION) as conn:
        with conn.cursor() as cur:
            mapping = get_location_map(cur)
            archive_table(cur, "hourly_data", "hourly", "dt", cutoff_ts, mapping)
            archive_table(cur, "daily_summary_data", "daily", "date", cutoff_ts, mapping)
        conn.commit()


if __name__ == "__main__":
    archive_recent_data()
