import json
import psycopg2
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
import logging
import os
from shared import load_environment, build_dsn_from_env

load_environment()

DB_DSN = build_dsn_from_env("controlcore", "PG_USER", "PG_PASSWORD")

# Load mapping of sensor_id to location_id
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../../../configs')
SENSOR_LOCATION_FILE = os.path.join(CONFIG_DIR, 'sensor_locations.json')
try:
    with open(SENSOR_LOCATION_FILE) as f:
        SENSOR_LOCATION_MAP = json.load(f)
except FileNotFoundError:
    SENSOR_LOCATION_MAP = {}



VALID_SENSOR_TYPES = {
    "temperature",
    "humidity",
    "barometric-pressure",
    "water-pressure",
    "valve-state",
    "soil-moisture",
    "light-intensity",
    "water-flow",
}

# Additional hard-coded sensor mappings for backward compatibility
DEFAULT_SENSOR_LOCATIONS = {
    "BeetsTomatoes-Valve": "excessus-home",
    "BeetsTomatoes-USSolid": "excessus-home",
    "BeetsTomatoes-Grieda": "excessus-home",
    "StationExt-SHT-1": "excessus-home",
    "StationExt-BMP-1": "excessus-home",
    "BeetsTomatoes-Soil": "excessus-home",
    "BeetsTomatoes-Light": "excessus-home",
    "CucumberWatermelon-USSolid": "excessus-home",
}

SENSOR_LOCATION_MAP.update(DEFAULT_SENSOR_LOCATIONS)


# Setup logging
LOG_DIR = os.path.join(os.path.dirname(__file__), '../../../logs/python/services')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'cc_data_manager.log'),
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def log(msg, level="info"):
    print(msg)
    getattr(logging, level)(msg)


def resolve_timestamp(ts):
    try:
        ts_float = float(ts)
        if ts_float > 1e12:
            ts_float /= 1000.0
        if ts_float < 1600000000:  # Before ~2020 — likely bogus
            raise ValueError("Invalid epoch timestamp")
        return datetime.fromtimestamp(ts_float, tz=timezone.utc)
    except Exception:
        log(
            f"⚠️ Substituting current UTC timestamp for bad input: {ts}",
            level="warning",
        )
        return datetime.now(timezone.utc)


def insert_sensor_data(payload):
    source_id = payload.get("source_id")
    if not source_id:
        log(f"⚠️ Missing source_id for {payload.get('sensor_id')}", level="warning")

    # Derive the location based on the source_id prefix when available
    location_id = None
    if source_id:
        prefix = source_id.split("_", 1)[0]
        if prefix in SENSOR_LOCATION_MAP.values():
            location_id = prefix

    # Fallback to the older sensor_id mapping if prefix lookup failed
    if not location_id:
        location_id = SENSOR_LOCATION_MAP.get(payload.get("sensor_id"))

    received_at = resolve_timestamp(payload.get("timestamp"))
    if location_id is None:
        log(
            f"⚠️ Unknown location for sensor {payload.get('sensor_id')}",
            level="warning",
        )

    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sensor_data (
                    station_id, location_id, controller_id, sensor_id, pin,
                    value, unit, source_id, sensor_type, received_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload.get("station"),
                    location_id,
                    payload.get("controller"),
                    payload.get("sensor_id"),
                    payload.get("pin", -1),
                    payload.get("value"),
                    payload.get("unit"),
                    source_id,
                    payload.get("sensor_type"),
                    received_at,
                ),
            )

def insert_control_log(payload):
    received_at = resolve_timestamp(payload.get("timestamp"))

    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO control_log (
                    station, controller_id, sensor_id, sensor_type,
                    command, value, unit, source, requestor_id, source_id,
                    received_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                payload.get("station"),
                payload.get("controller"),
                payload.get("sensor_id"),
                payload.get("sensor_type"),
                payload.get("command"),
                payload.get("value"),
                payload.get("unit"),
                payload.get("source"),
                payload.get("requestor_id"),
                payload.get("source_id"),
                received_at,
                ),
            )

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        topic = msg.topic

        required = ["sensor_id", "station", "controller", "sensor_type", "value", "unit"]
        missing = [key for key in required if payload.get(key) is None]

        if missing:
            log(f"⚠️ Skipping sensor payload missing fields: {missing}", level="warning")
            return

        if topic.startswith("controlcore/data/"):
            sensor_type = payload.get("sensor_type")
            if sensor_type not in VALID_SENSOR_TYPES:
                log(f"❌ Unknown sensor_type: {sensor_type}", level="error")
                return

            insert_sensor_data(payload)
            log(
                f"📥 Logged sensor data: {payload.get('sensor_id')} -> {payload.get('source_id', '')}"
            )
        elif topic.startswith("controlcore/command/"):
            insert_control_log(payload)
            log(f"🛠️ Logged control command: {payload.get('command')} → {payload.get('sensor_id')}")
        else:
            log(f"⚠️ Unknown topic: {topic}")

    except Exception as e:
        log(f"❌ Error processing message: {e}", level="error")

def main():
    client = mqtt.Client()
    client.on_message = on_message

    mqtt_host = os.getenv("MQTT_HOST", "localhost")
    mqtt_port = int(os.getenv("MQTT_PORT", 1883))
    mqtt_topic = os.getenv("MQTT_TOPIC", "controlcore/#")

    client.connect(mqtt_host, mqtt_port, 60)
    client.subscribe(mqtt_topic)

    log("✅ cc_data_manager is live and listening...")
    client.loop_forever()

if __name__ == "__main__":
    main()

