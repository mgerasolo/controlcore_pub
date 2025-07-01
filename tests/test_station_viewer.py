import sys
sys.path.append('.')

from datetime import datetime, timezone
from station_viewer.python.src.services.cc_data_manager import (
    resolve_timestamp,
    insert_sensor_data,
    SENSOR_LOCATION_MAP,
)
import psycopg2


def test_resolve_timestamp_valid():
    ts = 1700000000
    expected = datetime.fromtimestamp(ts, tz=timezone.utc)
    assert resolve_timestamp(ts) == expected


def test_resolve_timestamp_invalid():
    result = resolve_timestamp("notatime")
    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc


class DummyCursor:
    def __init__(self):
        self.query = None
        self.params = None

    def execute(self, query, params):
        self.query = query
        self.params = params

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


class DummyConn:
    def __init__(self):
        self.cursor_obj = DummyCursor()

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_insert_sensor_data_uses_source_prefix(monkeypatch):
    conn = DummyConn()
    monkeypatch.setattr(psycopg2, "connect", lambda *a, **k: conn)

    payload = {
        "sensor_id": "BeetsTomatoes-Light",
        "station": 1,
        "controller": "c1",
        "sensor_type": "temperature",
        "value": 42,
        "unit": "C",
        "source_id": "excessus-home_extra",
        "timestamp": 1700000000,
    }
    insert_sensor_data(payload)

    assert conn.cursor_obj.params[1] == "excessus-home"


def test_insert_sensor_data_uses_json_map(monkeypatch):
    conn = DummyConn()
    monkeypatch.setattr(psycopg2, "connect", lambda *a, **k: conn)

    payload = {
        "sensor_id": "CucumberWatermelon-USSolid",
        "station": 1,
        "controller": "c1",
        "sensor_type": "temperature",
        "value": 42,
        "unit": "C",
        "source_id": "unknownprefix_sensor",
        "timestamp": 1700000000,
    }
    insert_sensor_data(payload)

    assert conn.cursor_obj.params[1] == SENSOR_LOCATION_MAP["CucumberWatermelon-USSolid"]


