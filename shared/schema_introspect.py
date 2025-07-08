import psycopg2
from typing import List, Dict

from .env_utils import connect_using_env

# Map database names to environment variable names for credentials
USER_VARS = {
    "controlcore": ("CONTROLCORE_USER", "CONTROLCORE_PW"),
    "openweather_historical": ("OPENHIST_USER", "OPENHIST_PW"),
    "openweather_forecast": ("OPENFORE_USER", "OPENFORE_PW"),
}


def fetch_schema(dbname: str, tables: List[str]) -> Dict[str, List[dict]]:
    """Return table column info for a database.

    Parameters
    ----------
    dbname : str
        Database to connect to.
    tables : list[str]
        Specific tables to inspect.
    """
    schema: Dict[str, List[dict]] = {}
    if not tables:
        return schema

    user_var, pw_var = USER_VARS.get(dbname, ("PG_USER", "PG_PASSWORD"))
    try:
        with connect_using_env(dbname, user_var, pw_var) as conn:
            sql = (
                "SELECT table_name, column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = ANY(%s) "
                "ORDER BY table_name, ordinal_position"
            )
            with conn.cursor() as cur:
                cur.execute(sql, (tables,))
                rows = cur.fetchall()
    except Exception:
        return schema

    for table_name, column_name, data_type in rows:
        schema.setdefault(table_name, []).append({"name": column_name, "type": data_type})

    return schema


def list_public_tables(dbname: str) -> List[str]:
    """Return all table names in the public schema of a database."""
    user_var, pw_var = USER_VARS.get(dbname, ("PG_USER", "PG_PASSWORD"))
    try:
        with connect_using_env(dbname, user_var, pw_var) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
                    "ORDER BY table_name"
                )
                rows = cur.fetchall()
    except Exception:
        return []

    return [r[0] for r in rows]
