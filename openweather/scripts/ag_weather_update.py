import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.agriculture.ag_weather_service import AgWeatherService


def main(lat: float, lon: float) -> None:
    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY")
    db_conn = os.getenv("AG_WEATHER_DB")
    if not api_key or not db_conn:
        print("OPENWEATHER_API_KEY and AG_WEATHER_DB environment variables are required")
        sys.exit(1)

    service = AgWeatherService(api_key, db_conn)

    now = datetime.utcnow()
    hour_ago = int((now - timedelta(hours=1)).timestamp())

    service.fetch_and_store_historical(lat, lon, hour_ago)
    service.fetch_and_store_current(lat, lon)
    service.fetch_and_store_forecast(lat, lon)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    else:
        try:
            latitude = float(os.getenv("AG_LATITUDE", "0"))
            longitude = float(os.getenv("AG_LONGITUDE", "0"))
        except ValueError:
            print("Latitude and longitude must be numeric")
            sys.exit(1)

    main(latitude, longitude)
