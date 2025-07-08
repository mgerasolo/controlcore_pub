from .schema_introspect import fetch_schema


def collect_table_schema(_: str) -> str:
    db_tables = {
        "openweather_historical": ["fincastle_daily"],
        "openweather_forecast": ["forecast_data"],
        "controlcore": ["controllers", "controller_health"],
    }

    lines = ["# Available Databases and Tables", ""]
    for dbname, tables in db_tables.items():
        schema = fetch_schema(dbname, tables)
        lines.append(f"## {dbname}")
        for table in tables:
            cols = schema.get(table, [])
            if not cols:
                continue
            lines.append(f"- {table}(")
            for i, col in enumerate(cols):
                comma = "," if i < len(cols) - 1 else ""
                lines.append(f"    {col['name']} {col['type'].upper()}{comma}")
            lines.append(")")
        lines.append("")

    return "\n".join(lines).rstrip()
