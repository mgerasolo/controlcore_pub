import os

from openweather.src.services.openweather_overview import OpenWeatherDailyOverview

# Initialize the OpenWeather API wrapper
openweather = OpenWeatherDailyOverview()

# Call the run method to get weather overview data
overview_data = openweather.run()
