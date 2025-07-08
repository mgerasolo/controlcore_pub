import json
import logging
from .schema_introspect import fetch_schema, list_public_tables


def collect_table_schema(_: str) -> str:
    dbnames = [
        "openweather_historical",
        "openweather_forecast",
        "controlcore",
    ]

    schema_dict = {}
    for dbname in dbnames:
        tables = list_public_tables(dbname)
        logging.debug("Introspecting tables for %s: %s", dbname, tables)
        table_map = {}
        schema = fetch_schema(dbname, tables)
        if not schema:
            logging.warning("No schema returned for %s", dbname)
        for table in tables:
            cols = schema.get(table, [])
            if not cols:
                continue
            table_map[table] = [f"{c['name']} {c['type'].upper()}" for c in cols]
        schema_dict[dbname] = table_map

    return json.dumps(schema_dict, indent=2)
