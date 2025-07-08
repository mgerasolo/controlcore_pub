import sys
sys.path.append('.')

from sauron_api.sql_utils import get_table_schema, run_sql
from fastapi import HTTPException
import psycopg2


class DummyCursor:
    def __init__(self, rows=None, description=None):
        self.rows = rows or []
        self.description = description
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
    def __init__(self, cursor):
        self.cursor_obj = cursor

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_get_table_schema_builds_map():
    rows = [
        ('table1', 'id', 'integer'),
        ('table1', 'name', 'text'),
        ('table2', 'flag', 'boolean'),
    ]
    cursor = DummyCursor(rows)
    conn = DummyConn(cursor)

    schema = get_table_schema(conn, ['table1', 'table2'])

    assert 'information_schema.columns' in cursor.executed[0]
    assert cursor.params == (['table1', 'table2'],)
    assert schema == {
        'table1': [
            {'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'text'},
        ],
        'table2': [
            {'name': 'flag', 'type': 'boolean'},
        ],
    }


def test_run_sql_returns_dicts():
    description = [('id',), ('name',)]
    rows = [
        (1, 'Alice'),
        (2, 'Bob'),
    ]
    cursor = DummyCursor(rows, description=description)
    conn = DummyConn(cursor)

    result = run_sql(conn, 'SELECT id, name FROM users')

    assert cursor.executed
    assert result == [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
    ]


def test_run_sql_rejects_non_select():
    cursor = DummyCursor()
    conn = DummyConn(cursor)

    try:
        run_sql(conn, 'DELETE FROM users')
    except ValueError:
        pass
    else:
        assert False, 'ValueError not raised'
    assert not cursor.executed


class ErrorCursor(DummyCursor):
    def execute(self, query, params=None):
        class Dummy(psycopg2.Error):
            def __init__(self, code, msg):
                super().__init__(msg)
                self._code = code
                self._err = msg

            @property
            def pgcode(self):
                return self._code

            @property
            def pgerror(self):
                return self._err

        raise Dummy("42P01", "relation 'missing' does not exist")


def test_run_sql_missing_table_returns_400():
    cursor = ErrorCursor()
    conn = DummyConn(cursor)
    try:
        run_sql(conn, "SELECT * FROM missing")
    except HTTPException as e:
        assert e.status_code == 400
        assert "does not exist" in e.detail
    else:
        assert False, "HTTPException not raised"

