import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
import psycopg2
import paho.mqtt.client as mqtt

from shared import load_environment, build_dsn_from_env
from .status_logger import update_status
from openweather.scripts.archive_recent_to_longterm import archive_recent_data

load_environment()

DB_DSN = build_dsn_from_env("controlcore", "CONTROLCORE_USER", "CONTROLCORE_PW")
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_COMMAND_PREFIX = os.getenv("MQTT_COMMAND_PREFIX", "controlcore/command")

# Setup logging
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "runner.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def log(msg: str, level: str = "info") -> None:
    print(msg)
    getattr(logging, level)(msg)


def run_due_tasks():
    start = datetime.now(timezone.utc)
    log("[runner] Starting watering runner")
    now = start
    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT, 60)

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

                payload = {
                    "station": station,
                    "controller": controller_id,
                    "sensor_id": sensor_id,
                    "sensor_type": "valve-state",
                    "unit": "seconds",
                    "value": duration_seconds,
                    "command": "open",
                    "source": "advisor_schedule",
                    "requestor_id": "watering_runner",
                    "timestamp": int(now.timestamp()),
                    "source_id": source_id,
                }
                topic = f"{MQTT_COMMAND_PREFIX}/{sensor_id}"
                client.publish(topic, json.dumps(payload))

                # Mark schedule as executed
                cur.execute("""
                    UPDATE watering_schedule
                    SET status = 'completed',
                        confirmed_execution = TRUE,
                        last_updated = now()
                    WHERE id = %s
                """, (id,))

                log(f"[runner] ✅ Triggered zone '{zone_id}' for {duration_seconds // 60} minutes")

    try:
        archive_recent_data()
    except Exception as exc:
        log(f"[runner] ⚠️ weather archive failed: {exc}", level="warning")

    duration = (datetime.now(timezone.utc) - start).total_seconds()
    log(f"[runner] Completed in {duration:.1f}s with {len(rows)} tasks")
    update_status("runner", "completed", {"tasks": len(rows)})
    client.disconnect()


if __name__ == "__main__":
    run_due_tasks()
