import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.services.openweather_forecast_daily_get import OpenWeatherDailyForecast

# Initialize the OpenWeather API wrapper
openweather = OpenWeatherDailyForecast()

# Call the run method to get weather overview data
overview_data = openweather.run()
