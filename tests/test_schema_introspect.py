import sys
sys.path.append('.')

import shared.schema_introspect as si
from shared.table_schema import collect_table_schema


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
    calls = []

    def fake_fetch(db, tables):
        calls.append((db, tuple(tables)))
        if db == 'openweather_historical':
            return {'fincastle_daily': [{'name': 'date', 'type': 'int'}]}
        if db == 'openweather_forecast':
            return {'forecast_data': [{'name': 'date', 'type': 'int'}]}
        return {
            'controllers': [{'name': 'controller_id', 'type': 'text'}],
            'controller_health': [{'name': 'controller_id', 'type': 'text'}],
        }

    monkeypatch.setattr('shared.table_schema.fetch_schema', fake_fetch)

    md = collect_table_schema('ignored')

    assert ('controlcore', ('controllers', 'controller_health')) in calls
    assert ('openweather_historical', ('fincastle_daily',)) in calls
    assert ('openweather_forecast', ('forecast_data',)) in calls
    assert '# Available Databases and Tables' in md
    assert '## controlcore' in md
    assert '- controllers(' in md
