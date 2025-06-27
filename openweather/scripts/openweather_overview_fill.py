import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.services.openweather_overview import OpenWeatherDailyOverview

# Initialize the OpenWeather API wrapper
openweather = OpenWeatherDailyOverview()

# Call the run method to get weather overview data
overview_data = openweather.run()
