# OpenWeather Application - Public Version

This is the public version of the OpenWeather application. It includes:
- API integrations
- Data logging and storage
- Basic configuration management

## Requirements
- Python 3.11
- Dependencies listed in `requirements.txt`

## Setting Up
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies using:
   ```bash
   pip install -r requirements.txt
    ```

## Agricultural Weather Service

The `ag_weather_update.py` script stores historical, current and forecast data
for a location in a dedicated `agriculture` schema. Configure the following
environment variables before running:

- `OPENWEATHER_API_KEY` – your OpenWeather API token
- `AG_WEATHER_DB` – PostgreSQL connection string
- `AG_LATITUDE` and `AG_LONGITUDE` (optional defaults)

Example usage:

```bash
export OPENWEATHER_API_KEY=YOUR_KEY
export AG_WEATHER_DB="dbname=weather user=postgres password=secret host=localhost"
python scripts/ag_weather_update.py 44.5 -110.5
```
