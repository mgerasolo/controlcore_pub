import sys
sys.path.append('.')

import shared.schema_introspect as si
from shared.table_schema import collect_table_schema
import json


class DummyCursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed = []
        self.params = None

    def execute(self, query, params=None):
        self.executed.append(query)
        self.params = params

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


def test_fetch_schema_builds_mapping(monkeypatch):
    rows = [
        ('controllers', 'controller_id', 'text'),
        ('controllers', 'station_id', 'text'),
        ('controller_health', 'controller_id', 'text'),
    ]
    conn = DummyConn(rows)

    called = {}

    def fake_connect(db, user_var, pw_var):
        called['args'] = (db, user_var, pw_var)
        return conn

    monkeypatch.setattr(si, 'connect_using_env', fake_connect)

    schema = si.fetch_schema('controlcore', ['controllers', 'controller_health'])

    assert called['args'] == ('controlcore', 'CONTROLCORE_USER', 'CONTROLCORE_PW')
    assert conn.cursor_obj.params == (['controllers', 'controller_health'],)
    assert schema['controllers'][0]['name'] == 'controller_id'


def test_collect_table_schema_aggregates(monkeypatch):
    fetch_calls = []

    def fake_fetch(db, tables):
        fetch_calls.append((db, tuple(tables)))
        return {t: [{'name': 'id', 'type': 'int'}] for t in tables}

    def fake_list(db):
        return {
            'controlcore': ['controllers', 'controller_health'],
            'openweather_historical': ['fincastle_daily'],
            'openweather_forecast': ['forecast_data'],
        }[db]

    monkeypatch.setattr('shared.table_schema.fetch_schema', fake_fetch)
    monkeypatch.setattr('shared.table_schema.list_public_tables', fake_list)

    md = collect_table_schema('ignored')
    schema = json.loads(md)

    assert ('controlcore', ('controllers', 'controller_health')) in fetch_calls
    assert ('openweather_historical', ('fincastle_daily',)) in fetch_calls
    assert ('openweather_forecast', ('forecast_data',)) in fetch_calls
    assert 'controlcore' in schema
    assert 'controllers' in schema['controlcore']
    assert schema['controlcore']['controllers'][0] == 'id INT'
