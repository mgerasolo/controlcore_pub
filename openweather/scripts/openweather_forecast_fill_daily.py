import os

from openweather.src.services.openweather_forecast_daily_get import OpenWeatherDailyForecast

# Initialize the OpenWeather API wrapper
openweather = OpenWeatherDailyForecast()

# Call the run method to get weather overview data
overview_data = openweather.run()
