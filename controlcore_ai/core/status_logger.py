import json
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import Json
from shared import load_environment, build_dsn_from_env

load_environment()
DB_DSN_CONTROLCORE = build_dsn_from_env("controlcore", "CONTROLCORE_USER", "CONTROLCORE_PW")


def update_status(module_name: str, status: str, details: dict | None = None) -> None:
    """Insert or update status info for the given module."""
    with psycopg2.connect(DB_DSN_CONTROLCORE) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO module_status (module_name, last_run_time, status, details)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (module_name) DO UPDATE
                  SET last_run_time = EXCLUDED.last_run_time,
                      status = EXCLUDED.status,
                      details = EXCLUDED.details
                """,
                (
                    module_name,
                    datetime.now(timezone.utc),
                    status,
                    Json(details or {}),
                ),
            )
