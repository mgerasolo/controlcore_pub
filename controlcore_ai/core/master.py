import os
import sys
import subprocess
from datetime import datetime, timezone, timedelta
import psycopg2
from shared import load_environment, build_dsn_from_env

load_environment()
DB_DSN_CONTROLCORE = build_dsn_from_env("controlcore", "CONTROLCORE_USER", "CONTROLCORE_PW")

ADVISOR_INTERVAL_MINUTES = int(os.getenv("ADVISOR_INTERVAL_MINUTES", "60"))
FORECAST_INTERVAL_MINUTES = int(os.getenv("FORECAST_REGRESSION_INTERVAL_MINUTES", "1440"))


def get_last_run(module: str) -> datetime | None:
    with psycopg2.connect(DB_DSN_CONTROLCORE) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT last_run_time FROM module_status WHERE module_name = %s",
                (module,),
            )
            row = cur.fetchone()
            return row[0] if row else None


def should_run(last_run: datetime | None, interval_min: int) -> bool:
    if last_run is None:
        return True
    return datetime.now(timezone.utc) - last_run >= timedelta(minutes=interval_min)


def run_module(name: str, args: list[str] | None = None) -> None:
    cmd = [sys.executable, "-m", f"controlcore_ai.core.{name}"]
    if args:
        cmd += args
    subprocess.run(cmd, check=True)


def main(advisor_interval: int = ADVISOR_INTERVAL_MINUTES, forecast_interval: int = FORECAST_INTERVAL_MINUTES) -> None:
    # Always run runner to process any due schedules
    run_module("runner")

    # Advisor
    last = get_last_run("advisor")
    if should_run(last, advisor_interval):
        run_module("advisor")

    # Forecast regression
    last = get_last_run("forecast_regression")
    if should_run(last, forecast_interval):
        run_module("forecast_regression")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Control AI modules as needed")
    parser.add_argument("--advisor-interval", type=int, default=ADVISOR_INTERVAL_MINUTES)
    parser.add_argument("--forecast-interval", type=int, default=FORECAST_INTERVAL_MINUTES)
    args = parser.parse_args()
    main(args.advisor_interval, args.forecast_interval)
