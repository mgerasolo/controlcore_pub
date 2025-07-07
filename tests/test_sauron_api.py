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


async def dummy_post(url, json):
    if url.endswith('/generate-sql'):
        return DummyResp({'sql': 'SELECT 1'})
    elif url.endswith('/analyze'):
        return DummyResp({'answer': 'hello', 'display': {'type': 'text'}})
    raise AssertionError('unexpected url')


class DummyClient:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, url, json):
        return await dummy_post(url, json)


class DummyCursor:
    def execute(self, sql):
        self.sql = sql
    def fetchall(self):
        return [(1,)]
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass


class DummyConn:
    def cursor(self):
        return DummyCursor()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass


def test_chat_endpoint(monkeypatch):
    monkeypatch.setattr(main, 'collect_table_schema', lambda q: 'schema')
    monkeypatch.setattr(main.httpx, 'AsyncClient', lambda: DummyClient())
    monkeypatch.setattr(main, 'connect_using_env', lambda *a, **k: DummyConn())

    client = TestClient(main.app)
    resp = client.post('/chat', json={'question': 'What is up?'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['answer'] == 'hello'
