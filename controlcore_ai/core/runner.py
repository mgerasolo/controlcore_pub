import os
import psycopg2
from datetime import datetime, timezone

from shared import load_environment, build_dsn_from_env

load_environment()

DB_DSN = build_dsn_from_env("controlcore", "CONTROLCORE_USER", "CONTROLCORE_PW")


def run_due_tasks():
    now = datetime.now(timezone.utc)

    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, zone_id, sensor_id, source_id, station, controller_id, start_time, duration_seconds
                FROM watering_schedule
                WHERE status = 'scheduled'
                  AND start_time <= %s
                  AND confirmed_execution = FALSE
                ORDER BY start_time
            """, (now,))

            rows = cur.fetchall()
            for row in rows:
                (id, zone_id, sensor_id, source_id, station, controller_id, start_time, duration_seconds) = row

                # Insert command into control_log
                cur.execute("""
                    INSERT INTO control_log (station, controller_id, sensor_id, command, duration, source, requestor_id, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, EXTRACT(EPOCH FROM now())::bigint)
                """, (
                    station,
                    controller_id,
                    sensor_id,
                    "open",
                    duration_seconds,
                    "advisor_schedule",
                    "watering_runner"
                ))

                # Mark schedule as executed
                cur.execute("""
                    UPDATE watering_schedule
                    SET status = 'completed',
                        confirmed_execution = TRUE,
                        last_updated = now()
                    WHERE id = %s
                """, (id,))

                print(f"[runner] ✅ Triggered zone '{zone_id}' for {duration_seconds // 60} minutes")


if __name__ == "__main__":
    run_due_tasks()
