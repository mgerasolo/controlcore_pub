import sys
sys.path.append('.')

from fastapi.testclient import TestClient

import sauron_api.main as main

class DummyResp:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data

class DummyClient:
    def __init__(self, sql):
        self.sql = sql
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, url, json):
        if url.endswith('/generate-sql'):
            return DummyResp({'sql': self.sql})
        if url.endswith('/analyze'):
            return DummyResp({'answer': 'hello', 'display': {'type': 'text'}})
        raise AssertionError('unexpected url')

class DummyConn:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

def run_chat(monkeypatch, sql, question="what?"):
    captured = {}
    monkeypatch.setattr(main, 'collect_table_schema', lambda q: 'schema')
    monkeypatch.setattr(main.httpx, 'AsyncClient', lambda: DummyClient(sql))
    def fake_connect(db, user_var, pw_var):
        captured['args'] = (db, user_var, pw_var)
        return DummyConn()
    monkeypatch.setattr(main, 'connect_using_env', fake_connect)
    monkeypatch.setattr(main, 'run_sql', lambda conn, q: captured.setdefault('query', q) or [])

    client = TestClient(main.app)
    resp = client.post('/chat', json={'question': question})
    assert resp.status_code == 200
    assert resp.json()['answer'] == 'hello'
    assert captured['query'] == main.strip_fake_schemas(sql)
    return captured['args']

def test_chat_controlcore(monkeypatch):
    args = run_chat(monkeypatch, 'SELECT * FROM controllers')
    assert args == ('controlcore', 'CONTROLCORE_USER', 'CONTROLCORE_PW')

def test_chat_openweather_historical(monkeypatch):
    sql = 'SELECT * FROM openweather_historical.fincastle_daily'
    args = run_chat(monkeypatch, sql, question='historical rainfall data')
    assert args == ('openweather_historical', 'OPENHIST_USER', 'OPENHIST_PW')

def test_chat_openweather_forecast(monkeypatch):
    sql = 'SELECT * FROM openweather_forecast.forecast_data'
    args = run_chat(monkeypatch, sql, question='weather forecast for tomorrow')
    assert args == ('openweather_forecast', 'OPENFORE_USER', 'OPENFORE_PW')
