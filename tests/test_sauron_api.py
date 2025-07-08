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
    def __init__(self, sql, question, rephrased):
        self.sql = sql
        self.question = question
        self.rephrased = rephrased
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, url, json):
        if url.endswith('/rephrase'):
            assert json['text'] == self.question
            return DummyResp({'text': self.rephrased})
        if url.endswith('/generate-sql'):
            assert json['question'] == self.rephrased
            assert json['schema'] == 'schema'
            return DummyResp({'sql': self.sql})
        if url.endswith('/analyze'):
            return DummyResp({'answer': 'hello', 'display': {'type': 'text'}})
        raise AssertionError('unexpected url')

class DummyConn:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

def run_chat(monkeypatch, sql, question="what?", rephrased="clean"):
    captured = {}
    monkeypatch.setattr(main, 'collect_table_schema', lambda q: 'schema')
    monkeypatch.setattr(main.httpx, 'AsyncClient', lambda: DummyClient(sql, question, rephrased))
    def fake_connect(db, user_var, pw_var):
        captured['args'] = (db, user_var, pw_var)
        return DummyConn()
    monkeypatch.setattr(main, 'connect_using_env', fake_connect)
    def fake_run_sql(conn, q):
        captured.setdefault('query', q)
        return []
    monkeypatch.setattr(main, 'run_sql', fake_run_sql)

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

def test_sql_decides_db(monkeypatch):
    sql = 'SELECT * FROM openweather_historical.fincastle_daily'
    args = run_chat(monkeypatch, sql)
    assert args == ('openweather_historical', 'OPENHIST_USER', 'OPENHIST_PW')

def test_sql_overrides_question(monkeypatch):
    sql = 'SELECT * FROM openweather_forecast.forecast_data'
    # question mentions historical but SQL uses forecast schema
    args = run_chat(monkeypatch, sql, question='show me historical data')
    assert args == ('openweather_forecast', 'OPENFORE_USER', 'OPENFORE_PW')


def test_chat_rephrase(monkeypatch):
    run_chat(monkeypatch, 'SELECT 1', question='orig', rephrased='cleaned')


def test_strip_keeps_valid_table(monkeypatch):
    monkeypatch.setattr(main, 'build_db_tables', lambda: {
        'openweather_historical': ['fincastle_daily'],
        'openweather_forecast': ['forecast_data'],
        'controlcore': ['controllers', 'controller_health'],
    })
    main.DB_TABLES = main.build_db_tables()
    sql = 'SELECT * FROM openweather_historical.fincastle_daily'
    assert main.strip_fake_schemas(sql) == sql


def test_strip_removes_invalid_schema(monkeypatch):
    monkeypatch.setattr(main, 'build_db_tables', lambda: {
        'openweather_historical': ['fincastle_daily'],
        'openweather_forecast': ['forecast_data'],
        'controlcore': ['controllers', 'controller_health'],
    })
    main.DB_TABLES = main.build_db_tables()
    sql = 'SELECT * FROM openweather_forecast.controllers'
    assert main.strip_fake_schemas(sql) == 'SELECT * FROM controllers'


def test_chat_rejects_invalid_sql(monkeypatch):
    monkeypatch.setattr(main, 'collect_table_schema', lambda q: 'schema')
    monkeypatch.setattr(main.httpx, 'AsyncClient', lambda: DummyClient('SELECT (', 'bad', 'clean'))
    client = TestClient(main.app)
    resp = client.post('/chat', json={'question': 'bad'})
    assert resp.status_code == 400
    assert 'unbalanced' in resp.json()['detail'] or 'invalid' in resp.json()['detail']
