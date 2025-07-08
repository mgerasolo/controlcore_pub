def collect_table_schema(_: str) -> str:
    return """
# Available Databases and Tables

## openweather_historical
- fincastle_daily(
    date INT,
    precipitation_total REAL,
    temperature_max REAL,
    temperature_min REAL
)

## openweather_forecast
- forecast_data(
    date INT,
    lat REAL,
    lon REAL,
    temperature REAL,
    precipitation_mm REAL,
    humidity INT
)

## controlcore
- controllers(
    controller_id TEXT,
    station_id TEXT,
    last_seen TIMESTAMP
)
- controller_health(
    controller_id TEXT,
    last_reported TIMESTAMP,
    issue TEXT,
    severity TEXT
)
"""
