from .schema_introspect import fetch_schema, list_public_tables


def collect_table_schema(_: str) -> str:
    dbnames = [
        "openweather_historical",
        "openweather_forecast",
        "controlcore",
    ]

    lines = ["# Available Databases and Tables", ""]
    for dbname in dbnames:
        tables = list_public_tables(dbname)
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
