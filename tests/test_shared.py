import os
import importlib

from shared.env_utils import build_dsn_from_env


def test_build_dsn_from_env(monkeypatch):
    monkeypatch.setenv('TEST_USER', 'user')
    monkeypatch.setenv('TEST_PW', 'pass')
    monkeypatch.setenv('PG_HOST', 'db.example')
    monkeypatch.setenv('PG_PORT', '5433')
    dsn = build_dsn_from_env('mydb', 'TEST_USER', 'TEST_PW')
    assert dsn == 'postgresql://user:pass@db.example:5433/mydb'

