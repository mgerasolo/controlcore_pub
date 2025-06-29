import sys
sys.path.append('.')
import controlcore_ai.core.advisor as advisor
import psycopg2
from controlcore_ai.core.status_logger import update_status
from controlcore_ai.core.master import should_run
advise_watering = advisor.advise_watering


def test_advise_skip_due_to_recent_rain():
    decision, reasons = advise_watering({}, {"recent_rain_mm_last_3_days": 12})
    assert decision == "skip"
    assert "last 3 days" in reasons[0]


def test_advise_skip_due_to_forecast():
    weather = {"hourly_pop_windows": {"a": 0.9, "b": 0.95, "c": 0.94, "d": 0.93}}
    decision, reasons = advise_watering({}, weather)
    assert decision == "skip"
    assert "High-confidence forecast" in reasons[0]


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


def test_update_status_inserts(monkeypatch):
    conn = DummyConn()
    monkeypatch.setattr(psycopg2, "connect", lambda *a, **k: conn)
    update_status("advisor", "ok", {"foo": "bar"})
    assert "module_status" in conn.cursor_obj.query


def test_should_run_logic():
    from datetime import datetime, timezone, timedelta

    assert should_run(None, 5)

    last = datetime.now(timezone.utc) - timedelta(minutes=10)
    assert should_run(last, 5)

    recent = datetime.now(timezone.utc) - timedelta(minutes=2)
    assert not should_run(recent, 5)

