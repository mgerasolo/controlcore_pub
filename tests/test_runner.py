import sys
sys.path.append('.')

from datetime import datetime, timezone
import psycopg2
import paho.mqtt.client as mqtt

import controlcore_ai.core.runner as runner

class DummyCursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed = []
    def execute(self, query, params=None):
        self.executed.append((query, params))
    def fetchall(self):
        return self.rows
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

class DummyConn:
    def __init__(self, rows):
        self.cursor_obj = DummyCursor(rows)
    def cursor(self):
        return self.cursor_obj
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

class DummyMQTT:
    def __init__(self):
        self.published = []
    def connect(self, host, port, keepalive):
        pass
    def publish(self, topic, payload):
        self.published.append((topic, payload))
    def disconnect(self):
        pass


def test_runner_publishes(monkeypatch):
    rows = [(
        1,
        'zone1',
        'sensor1',
        'src1',
        'station',
        'ctrl',
        datetime.now(timezone.utc),
        30,
    )]
    conn = DummyConn(rows)
    monkeypatch.setattr(psycopg2, 'connect', lambda *a, **k: conn)
    mqtt_obj = DummyMQTT()
    monkeypatch.setattr(mqtt, 'Client', lambda: mqtt_obj)

    runner.run_due_tasks()

    assert mqtt_obj.published
    topic, payload = mqtt_obj.published[0]
    assert 'controlcore/command' in topic
