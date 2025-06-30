import math
from datetime import datetime, timezone, timedelta
from typing import Optional

import pandas as pd
import psycopg2

from shared import load_environment, build_dsn_from_env
from .status_logger import update_status

load_environment()

DB_DSN_CONTROLCORE = build_dsn_from_env("controlcore", "CONTROLCORE_USER", "CONTROLCORE_PW")
DB_DSN_HISTORICAL = build_dsn_from_env("openweather_historical", "OPENHIST_USER", "OPENHIST_PW")
DB_DSN_FORECAST = build_dsn_from_env("openweather_forecast", "OPENFORE_USER", "OPENFORE_PW")


def calculate_error_metrics(df: pd.DataFrame, observed_col: str = "actual_temp") -> dict:
    """Return MAE and RMSE for forecast vs observed temperatures."""
    if observed_col not in df:
        raise KeyError(f"missing column: {observed_col}")

    diffs = df["forecast_temp"] - df[observed_col]
    diffs = diffs.dropna()
    if diffs.empty:
        return {"mae": float("nan"), "rmse": float("nan")}

    mae = float(diffs.abs().mean())
    rmse = float(math.sqrt((diffs ** 2).mean()))
    return {"mae": mae, "rmse": rmse}


def calculate_error_by_lead(df: pd.DataFrame, bins: list[int] | None = None) -> pd.DataFrame:
    """Return MAE/RMSE grouped by lead time in hours."""
    if "lead_hours" not in df:
        raise KeyError("lead_hours column missing")

    work = df.dropna(subset=["lead_hours"])
    if bins is not None:
        work = work.copy()
        work["lead_group"] = pd.cut(work["lead_hours"], bins=bins, right=False)
        groups = work.groupby("lead_group")
        key_name = "lead_group"
    else:
        groups = work.groupby("lead_hours")
        key_name = "lead_hours"

    records = []
    for key, grp in groups:
        metrics = calculate_error_metrics(grp)
        records.append({key_name: key, **metrics})
    return pd.DataFrame(records)


def _fetch_data(days: int) -> pd.DataFrame:
    """Fetch forecast, historical and sensor data for the last `days` days."""
    start_time = datetime.now(timezone.utc) - timedelta(days=days)

    forecast_rows: list[tuple] = []
    with psycopg2.connect(DB_DSN_FORECAST) as conn:
        with conn.cursor() as cur:
            hourly_ts_cols = ", ".join([f"hour_{i}_timestamptz" for i in range(24)])
            hourly_temp_cols = ", ".join([f"hour_{i}_temp" for i in range(24)])
            cur.execute(
                f"""
                SELECT timestamp, lat, lon, {hourly_ts_cols}, {hourly_temp_cols}
                FROM openweather_forecast_detail
                WHERE timestamp >= %s
                """,
                (start_time, ),
            )
            for row in cur.fetchall():
                base_ts, lat, lon, *rest = row
                ts_values = rest[:24]
                temp_values = rest[24:]
                for ts, temp in zip(ts_values, temp_values):
                    forecast_rows.append((ts, base_ts, lat, lon, temp))

    df = pd.DataFrame(
        forecast_rows,
        columns=["forecast_time", "snapshot_time", "lat", "lon", "forecast_temp"],
    )
    if df.empty:
        return df

    df["lead_hours"] = (
        df["forecast_time"] - df["snapshot_time"]
    ).dt.total_seconds() / 3600

    # Fetch historical temperatures
    min_time = df["forecast_time"].min() - timedelta(hours=1)
    max_time = df["forecast_time"].max() + timedelta(hours=1)
    with psycopg2.connect(DB_DSN_HISTORICAL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT to_timestamp(dt) AT TIME ZONE 'UTC' AS ts, ROUND(lat::numeric,4) AS lat,
                       ROUND(lon::numeric,4) AS lon, temp
                FROM hourly_data
                WHERE dt BETWEEN %s AND %s
                """,
                (int(min_time.timestamp()), int(max_time.timestamp())),
            )
            hist = cur.fetchall()
    hist_df = pd.DataFrame(hist, columns=["ts", "lat", "lon", "actual_temp"])
    hist_df["ts"] = pd.to_datetime(hist_df["ts"], utc=True)

    df["lat_r"] = df["lat"].round(4)
    df["lon_r"] = df["lon"].round(4)
    merged = pd.merge(
        df,
        hist_df,
        left_on=["lat_r", "lon_r", "forecast_time"],
        right_on=["lat", "lon", "ts"],
        how="left",
    )
    merged.drop(["lat_r", "lon_r", "lat_y", "lon_y", "ts"], axis=1, inplace=True)

    # Attach sensor data when available
    with psycopg2.connect(DB_DSN_CONTROLCORE) as conn:
        with conn.cursor() as cur:
            sensor_vals: list[Optional[float]] = []
            merged.rename(columns={"lat_x": "lat", "lon_x": "lon"}, inplace=True)
            for ts, lat, lon in merged[["forecast_time", "lat", "lon"]].itertuples(index=False):
                cur.execute(
                    """
                    SELECT AVG(sd.value)
                    FROM sensor_data sd
                    JOIN stations st ON st.station_id = sd.station_id
                    JOIN locations l ON l.location_id = st.location_id
                    WHERE sd.sensor_type = 'temperature'
                      AND sd.received_at BETWEEN %s AND %s
                      AND ROUND(l.lat::numeric,4) = %s AND ROUND(l.lon::numeric,4) = %s
                    """,
                    (
                        ts - timedelta(minutes=30),
                        ts + timedelta(minutes=30),
                        round(lat, 4),
                        round(lon, 4),
                    ),
                )
                val = cur.fetchone()[0]
                sensor_vals.append(val)
    merged["sensor_temp"] = sensor_vals
    return merged


def run_forecast_regression(days: int = 1, store: bool = False) -> pd.DataFrame:
    """Run forecast regression for the last `days` days."""
    df = _fetch_data(days)
    if not df.empty:
        # ignore future forecasts or rows without an observed temperature
        now = datetime.now(timezone.utc)
        df = df[df["forecast_time"] <= now]
        df = df.dropna(subset=["actual_temp"])

    metrics = calculate_error_metrics(df)
    lead_metrics = calculate_error_by_lead(df) if not df.empty else pd.DataFrame()

    if store:
        run_time = datetime.now(timezone.utc)
        with psycopg2.connect(DB_DSN_FORECAST) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS forecast_accuracy (
                        run_time timestamptz PRIMARY KEY,
                        mae double precision,
                        rmse double precision
                    )
                    """
                )
                cur.execute(
                    "INSERT INTO forecast_accuracy (run_time, mae, rmse) VALUES (%s, %s, %s) ON CONFLICT (run_time) DO NOTHING",
                    (datetime.now(timezone.utc), metrics["mae"], metrics["rmse"]),
                    (run_time, metrics["mae"], metrics["rmse"]),
                )

                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS forecast_accuracy_lead (
                        run_time timestamptz,
                        lead_hours double precision,
                        mae double precision,
                        rmse double precision
                    )
                    """
                )
                for _, row in lead_metrics.iterrows():
                    cur.execute(
                        "INSERT INTO forecast_accuracy_lead (run_time, lead_hours, mae, rmse) VALUES (%s, %s, %s, %s)",
                        (run_time, float(row.get('lead_hours', row[0])), row['mae'], row['rmse']),
                    )
    return df


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run forecast regression analysis")
    parser.add_argument("--days", type=int, default=1, help="Number of past days to process")
    parser.add_argument("--store", action="store_true", help="Persist metrics to DB")
    args = parser.parse_args()

    df = run_forecast_regression(args.days, args.store)
    metrics = calculate_error_metrics(df)
    if math.isnan(metrics["mae"]):
        print("MAE: NaN\nRMSE: NaN")
        details = {}
    else:
        print(f"MAE: {metrics['mae']:.2f}\nRMSE: {metrics['rmse']:.2f}")
        details = metrics
    update_status("forecast_regression", "completed", details)


if __name__ == "__main__":
    main()
