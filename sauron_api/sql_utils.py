"""Utility helpers for database interactions."""

from __future__ import annotations

from typing import List, Dict


def get_table_schema(conn, tables: List[str]) -> Dict[str, List[dict]]:
    """Return a mapping of table names to column schemas.

    Parameters
    ----------
    conn : psycopg connection
        Open connection to query.
    tables : list[str]
        List of table names to inspect.

    Returns
    -------
    dict
        Mapping of table name to list of ``{'name': column_name, 'type': data_type}``.
    """
    schema: Dict[str, List[dict]] = {}
    if not tables:
        return schema

    sql = (
        "SELECT table_name, column_name, data_type "
        "FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = ANY(%s) "
        "ORDER BY table_name, ordinal_position"
    )

    with conn.cursor() as cur:
        cur.execute(sql, (tables,))
        rows = cur.fetchall()

    for table_name, column_name, data_type in rows:
        schema.setdefault(table_name, []).append({"name": column_name, "type": data_type})

    return schema


def run_sql(conn, query: str) -> List[dict]:
    """Execute a read-only SQL query and return rows as dictionaries.

    This performs very small safety checks to help avoid executing
    destructive statements.
    """
    stripped = query.strip().lower()
    if not (stripped.startswith("select") or stripped.startswith("with")):
        raise ValueError("only SELECT queries are allowed")
    if ";" in stripped[:-1]:
        raise ValueError("multiple statements detected")

    with conn.cursor() as cur:
        cur.execute(query)
        colnames = [desc[0] for desc in (cur.description or [])]
        rows = cur.fetchall()

    return [dict(zip(colnames, row)) for row in rows]

