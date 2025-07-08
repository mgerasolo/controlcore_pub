import sys
import types
sys.path.append('.')

# Stub heavy optional deps before importing the script
st_mod = types.ModuleType("sentence_transformers")
st_mod.SentenceTransformer = object
sys.modules.setdefault("sentence_transformers", st_mod)

pg_mod = types.ModuleType("pgvector")
pg_psy = types.ModuleType("pgvector.psycopg2")
pg_psy.register_vector = lambda conn: None
pg_mod.psycopg2 = pg_psy
sys.modules.setdefault("pgvector", pg_mod)
sys.modules.setdefault("pgvector.psycopg2", pg_psy)

dotenv_mod = types.ModuleType("dotenv")
dotenv_mod.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", dotenv_mod)

psycopg2 = types.ModuleType("psycopg2")
extras = types.ModuleType("psycopg2.extras")
extras.execute_values = lambda cur, sql, rows: None
psycopg2.extras = extras
sys.modules.setdefault("psycopg2", psycopg2)
sys.modules.setdefault("psycopg2.extras", extras)

import json
from pathlib import Path

import scripts.load_schema_vectors as lsv


def test_main_inserts_rows(monkeypatch, tmp_path):
    data = {
        "tables": [
            {
                "table": "users",
                "description": "User table",
                "columns": {"id": "identifier"},
                "aliases": ["people"],
                "example_queries": ["count users"]
            }
        ]
    }
    json_file = tmp_path / "sample.json"
    json_file.write_text(json.dumps(data))

    class DummyModel:
        def __init__(self):
            self.calls = []
        def encode(self, text):
            self.calls.append(text)
            class Vec(list):
                def tolist(self):
                    return list(self)

            return Vec([len(self.calls)])

    model = DummyModel()
    monkeypatch.setattr(lsv, "SentenceTransformer", lambda name: model)
    monkeypatch.setattr(lsv.Path, "glob", lambda self, pattern: [json_file])
    monkeypatch.setattr(lsv, "load_environment", lambda: None)
    monkeypatch.setattr(lsv, "register_vector", lambda conn: None)

    class DummyCursor:
        def __init__(self):
            self.called = False
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

    conn = DummyConn()
    captured = {}

    def fake_connect(db, user_var, pw_var):
        captured['args'] = (db, user_var, pw_var)
        return conn

    def fake_execute_values(cur, sql, rows):
        captured['sql'] = sql
        captured['rows'] = rows

    monkeypatch.setattr(lsv, "connect_using_env", fake_connect)
    monkeypatch.setattr(lsv, "execute_values", fake_execute_values)

    lsv.main()

    assert captured['args'] == ("controlcore", "CONTROLCORE_USER", "CONTROLCORE_PW")
    assert captured['sql'].startswith("INSERT INTO schema_embeddings")
    assert captured['rows'] == [
        ("users", None, "User table", [1], "sample.json", "description"),
        ("users", "id", "identifier", [2], "sample.json", "column"),
        ("users", None, "people", [3], "sample.json", "alias"),
        ("users", None, "count users", [4], "sample.json", "example"),
    ]
    assert model.calls == ["User table", "identifier", "people", "count users"]
