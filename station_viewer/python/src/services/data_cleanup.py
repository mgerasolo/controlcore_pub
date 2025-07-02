from datetime import datetime, timedelta, timezone
import argparse
import os
import psycopg2

from shared import load_environment, build_dsn_from_env

load_environment()
DB_DSN = build_dsn_from_env("controlcore", "PG_USER", "PG_PASSWORD")


def remove_old_sensor_data(days: int) -> int:
    """Delete sensor_data rows older than the provided number of days.

    Args:
        days: Number of days of history to retain.

    Returns:
        Number of rows removed.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM sensor_data WHERE received_at < %s",
                (cutoff,)
            )
            deleted = cur.rowcount
    return deleted


def main() -> None:
    parser = argparse.ArgumentParser(description="Purge old sensor_data records")
    parser.add_argument(
        "--days",
        type=int,
        default=int(os.getenv("DATA_RETENTION_DAYS", 30)),
        help="Number of days of data to keep",
    )
    args = parser.parse_args()
    removed = remove_old_sensor_data(args.days)
    print(f"Deleted {removed} sensor_data rows older than {args.days} days")


if __name__ == "__main__":
    main()
