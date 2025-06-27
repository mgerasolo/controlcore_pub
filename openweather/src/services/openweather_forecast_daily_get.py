import requests
import sys
from datetime import datetime, timezone, timedelta
import psycopg2
import time
import json
import os
from src.services.api_logger import APILogging
from src.config.config import LATITUDE, LONGITUDE, WEATHER_FORECAST_DB_CONNECTION, API_KEY, DAILY_FORECAST_LIMIT
from src.services.api_control import APIControl

class OpenWeatherDailyForecast:
    def __init__(self):
        self.latitude = LATITUDE
        self.longitude = LONGITUDE
        self.api_key = API_KEY
        self.logger = APILogging()
        self.failed_requests = 0
        self.failed_sql_inserts = 0
        self.daily_limit = DAILY_FORECAST_LIMIT  # Total API call limit per day
        self.start_time = time.time()  # Track when rate-limiting minute starts
        self.db_connection = WEATHER_FORECAST_DB_CONNECTION
        self.platform = "OpenWeather"
        self.api_call_type_id = 1
        self.script_name = "openweather_forecast_daily_get"
        self.api_call_alt_name = "onecall"
        self.api_call_type = 'Current and Forecasts'
        self.control = APIControl(self.api_call_type_id, self.script_name, self.platform, self.api_call_alt_name, self.daily_limit)

    def call_openweather_api(self):
        try:
            # Retrieve the API prototype URL
            api_prototype = self.logger.get_api_prototype(self.platform, self.api_call_type)
            base_url = api_prototype.format(lat=self.latitude, lon=self.longitude, API_key=self.api_key)

            self.logger.log_event("Request", f"Calling API: OpenWeather Current and Forecasts")

            params = {
                'lat': self.latitude,
                'lon': self.longitude,
                'appid': self.api_key,
                'units': 'imperial'
            }

            max_retries = 3  # Maximum number of retries
            retry_count = 0
            call_timestamp = int(datetime.now().timestamp())
            request_payload = base_url

            for attempt in range(max_retries):
                try:
                    response = requests.get(base_url, params=params, timeout=5)  # Set a timeout of 5 seconds
                    response_code = response.status_code
                    response_message = f"Successfully retrieved Current and Forecasts" if response_code == 200 else f"API call failed with status {response_code} - {response.text}"

                    # Log the API call in the database
                    api_call_id = self.logger.log_api_call(
                        call_timestamp, self.api_call_type_id, 'API Call', request_payload,
                        response_code, response_message, retry_count,
                        "OpenWeather API Current and Forecasts"
                    )

                    # Handle successful response
                    if response_code == 200:
                        self.logger.log_event("Success", f"Data received for Current and Forecasts")
                        self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, "stopped-succ", None, False)
                        self.control.update_requests_made_today()
                        return response.json(), api_call_id

                    # If 400 Bad Request (invalid date range), handle it as a known failure
                    elif response_code == 400 and "out the available range" in response.text:
                        error_message = f"API Error: call failed with status {response_code}: Invalid date"
                        self.logger.log_event("Warning", error_message)
                        self.failed_requests += 1  # Count invalid responses
                        self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'Processing', error_message, False)
                        self.control.update_requests_made_today()
                        return None, api_call_id

                    # Handle critical errors like 404 (Not Found) or 403 (Forbidden)
                    elif response_code == 404:
                        error_message = f"API call failed with status {response_code}: Not Found"
                        self.logger.log_event("Critical Error", error_message)
                        self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'stopped-err', error_message, True)
                        self.control.update_requests_made_today()
                        sys.exit(1)  # Stop execution

                    elif response_code == 403:
                        error_message = f"API call failed with status {response_code}: Forbidden (Invalid API Key)"
                        self.logger.log_event("Critical Error", error_message)
                        self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'stopped-err', error_message, True)
                        self.control.update_requests_made_today()
                        sys.exit(1)  # Stop execution

                    # Handle server-side or unhandled errors
                    elif response_code >= 500:
                        error_message = f"Server Error (Status: {response_code}) during API call"
                        self.logger.log_event("Critical Error", error_message)
                        self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'stopped-err', error_message, True)
                        self.control.update_requests_made_today()
                        sys.exit(1)  # Stop execution

                except requests.exceptions.RequestException as e:
                    self.logger.log_api_call(
                        call_timestamp, self.api_call_type_id, 'API Call', request_payload,
                        500, str(e), retry_count,
                        "OpenWeather API Overview"
                    )
                    retry_count += 1
                    if attempt < max_retries - 1:
                        self.logger.log_event("Warning", f"Error fetching data: {e}. Retrying ({retry_count}/{max_retries})...")
                        self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'Retrying', error_message, True)
                        self.control.update_requests_made_today()
                        continue
                    else:
                        error_message = f"Error fetching data after {max_retries} attempts. Skipping this timestamp"
                        self.logger.log_event("Error", error_message)
                        self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'Skipped - Retries Exceeded', error_message, True)
                        self.control.update_requests_made_today()
                        return None, None

        except Exception as e:
            # Log exceptions and treat as a critical failure
            error_message = f"API Error: {str(e)}"
            self.logger.log_event("API Error", error_message)
            self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'stopped-err', error_message, True)
            self.control.update_requests_made_today()
            sys.exit(1)  # Stop execution

    def extract_and_validate_weather_data(self, data):
        """
        Extracts and validates weather data from the OpenWeather API response.
        """
        try:
            # Ensure the necessary top-level fields exist in the API response
            if 'lat' not in data or 'lon' not in data or 'timezone' not in data:
                raise ValueError("Missing required fields in the weather data.")

            # Prepare the result dictionary to store validated weather data
            result = {
                'timestamp': datetime.now(timezone.utc),  # Use proper timestamptz format
                'lat': data['lat'],
                'lon': data['lon'],
                'timezone': data.get('timezone', ''),
                'timezone_offset': data.get('timezone_offset', 0),
                'sunrise': datetime.utcfromtimestamp(data['current'].get('sunrise')),
                'sunset': datetime.utcfromtimestamp(data['current'].get('sunset')),
                'current_temp': data['current'].get('temp', 0.0),
                'current_feels_like': data['current'].get('feels_like', 0.0),
                'current_pressure': data['current'].get('pressure', 0),
                'current_humidity': data['current'].get('humidity', 0),
                'current_dew_point': data['current'].get('dew_point', 0.0),
                'current_uvi': data['current'].get('uvi', 0.0),
                'current_clouds': data['current'].get('clouds', 0),
                'current_visibility': data['current'].get('visibility', 0),
                'current_wind_speed': data['current'].get('wind_speed', 0.0),
                'current_wind_deg': data['current'].get('wind_deg', 0),
                'current_wind_gust': data['current'].get('wind_gust', 0.0),
                'current_weather_main': data['current']['weather'][0].get('main', ''),
                'current_weather_description': data['current']['weather'][0].get('description', '')
            }

            # Handle hourly forecast data (for the next 24 hours)
            for hour in range(24):
                hour_data = data['hourly'][hour]
                result.update({
                    f'hour_{hour}_timestamptz': datetime.utcfromtimestamp(hour_data.get('dt')),
                    f'hour_{hour}_temp': hour_data.get('temp', 0.0),
                    f'hour_{hour}_feels_like': hour_data.get('feels_like', 0.0),
                    f'hour_{hour}_pressure': hour_data.get('pressure', 0),
                    f'hour_{hour}_humidity': hour_data.get('humidity', 0),
                    f'hour_{hour}_dew_point': hour_data.get('dew_point', 0.0),
                    f'hour_{hour}_clouds': hour_data.get('clouds', 0),
                    f'hour_{hour}_visibility': hour_data.get('visibility', 0),
                    f'hour_{hour}_wind_speed': hour_data.get('wind_speed', 0.0),
                    f'hour_{hour}_wind_deg': hour_data.get('wind_deg', 0),
                    f'hour_{hour}_wind_gust': hour_data.get('wind_gust', 0.0),
                    f'hour_{hour}_weather_main': hour_data['weather'][0].get('main', ''),
                    f'hour_{hour}_weather_description': hour_data['weather'][0].get('description', ''),
                    f'hour_{hour}_pop': hour_data.get('pop', 0.0)  # Probability of precipitation
                })

            # Handle daily forecast data (for the next 8 days)
            for day in range(8):
                day_data = data['daily'][day]
                result.update({
                    f'day_{day}_timestamptz': datetime.utcfromtimestamp(day_data.get('dt')),
                    f'day_{day}_summary': day_data['weather'][0].get('description', ''),
                    f'day_{day}_temp_day': day_data['temp'].get('day', 0.0),
                    f'day_{day}_temp_min': day_data['temp'].get('min', 0.0),
                    f'day_{day}_temp_max': day_data['temp'].get('max', 0.0),
                    f'day_{day}_temp_night': day_data['temp'].get('night', 0.0),
                    f'day_{day}_temp_eve': day_data['temp'].get('eve', 0.0),
                    f'day_{day}_temp_morn': day_data['temp'].get('morn', 0.0),
                    f'day_{day}_feels_like_day': day_data['feels_like'].get('day', 0.0),
                    f'day_{day}_feels_like_night': day_data['feels_like'].get('night', 0.0),
                    f'day_{day}_feels_like_eve': day_data['feels_like'].get('eve', 0.0),
                    f'day_{day}_feels_like_morn': day_data['feels_like'].get('morn', 0.0),
                    f'day_{day}_pressure': day_data.get('pressure', 0),
                    f'day_{day}_humidity': day_data.get('humidity', 0),
                    f'day_{day}_dew_point': day_data.get('dew_point', 0.0),
                    f'day_{day}_wind_speed': day_data.get('wind_speed', 0.0),
                    f'day_{day}_wind_deg': day_data.get('wind_deg', 0),
                    f'day_{day}_wind_gust': day_data.get('wind_gust', 0.0),
                    f'day_{day}_weather_main': day_data['weather'][0].get('main', ''),
                    f'day_{day}_weather_description': day_data['weather'][0].get('description', ''),
                    f'day_{day}_clouds': day_data.get('clouds', 0),
                    f'day_{day}_pop': day_data.get('pop', 0.0),
                    f'day_{day}_uvi': day_data.get('uvi', 0.0)
                })

            return result

        except (KeyError, ValueError) as e:
            # Log the error for further analysis
            self.logger.log_data_error(self.script_name, str(e))
            raise ValueError(f"Error processing weather data: {e}")

    def prepare_insert_statement(self):
        columns = [
            'timestamp', 'lat', 'lon', 'timezone', 'timezone_offset', 'sunrise', 'sunset',
            'current_temp', 'current_feels_like', 'current_pressure', 'current_humidity',
            'current_dew_point', 'current_uvi', 'current_clouds', 'current_visibility',
            'current_wind_speed', 'current_wind_deg', 'current_wind_gust', 'current_weather_main',
            'current_weather_description'
        ]

        # Append hourly forecast columns
        for hour in range(24):
            columns += [
                f'hour_{hour}_timestamptz', f'hour_{hour}_temp', f'hour_{hour}_feels_like',
                f'hour_{hour}_pressure', f'hour_{hour}_humidity', f'hour_{hour}_dew_point',
                f'hour_{hour}_clouds', f'hour_{hour}_visibility', f'hour_{hour}_wind_speed',
                f'hour_{hour}_wind_deg', f'hour_{hour}_wind_gust', f'hour_{hour}_weather_main',
                f'hour_{hour}_weather_description', f'hour_{hour}_pop'
            ]

        # Append daily forecast columns
        for day in range(8):
            columns += [
                f'day_{day}_timestamptz', f'day_{day}_summary', f'day_{day}_temp_day', f'day_{day}_temp_min',
                f'day_{day}_temp_max', f'day_{day}_temp_night', f'day_{day}_temp_eve', f'day_{day}_temp_morn',
                f'day_{day}_feels_like_day', f'day_{day}_feels_like_night', f'day_{day}_feels_like_eve',
                f'day_{day}_feels_like_morn', f'day_{day}_pressure', f'day_{day}_humidity', f'day_{day}_dew_point',
                f'day_{day}_wind_speed', f'day_{day}_wind_deg', f'day_{day}_wind_gust', f'day_{day}_weather_main',
                f'day_{day}_weather_description', f'day_{day}_clouds', f'day_{day}_pop', f'day_{day}_uvi'
            ]

        # Prepare placeholders for values
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join(columns)

        sql = f"INSERT INTO openweather_forecast_detail ({column_names}) VALUES ({placeholders})"
        return sql

    def insert_forecast_data(self, forecast_data, api_call_id):
        try:
            # Establish the database connection
            conn = psycopg2.connect(self.db_connection)
            cursor = conn.cursor()

            # Prepare SQL insert statement
            insert_query = self.prepare_insert_statement()

            # Prepare values for the insert
            values = [
                forecast_data['timestamp'],
                forecast_data['lat'],
                forecast_data['lon'],
                forecast_data['timezone'],
                forecast_data['timezone_offset'],
                forecast_data['sunrise'],
                forecast_data['sunset'],
                forecast_data['current_temp'],
                forecast_data['current_feels_like'],
                forecast_data['current_pressure'],
                forecast_data['current_humidity'],
                forecast_data['current_dew_point'],
                forecast_data['current_uvi'],
                forecast_data['current_clouds'],
                forecast_data['current_visibility'],
                forecast_data['current_wind_speed'],
                forecast_data['current_wind_deg'],
                forecast_data['current_wind_gust'],
                forecast_data['current_weather_main'],
                forecast_data['current_weather_description'],
            ]

            # Append hourly forecast data (24 hours)
            for hour in range(24):
                values += [
                    forecast_data[f'hour_{hour}_timestamptz'],
                    forecast_data[f'hour_{hour}_temp'],
                    forecast_data[f'hour_{hour}_feels_like'],
                    forecast_data[f'hour_{hour}_pressure'],
                    forecast_data[f'hour_{hour}_humidity'],
                    forecast_data[f'hour_{hour}_dew_point'],
                    forecast_data[f'hour_{hour}_clouds'],
                    forecast_data[f'hour_{hour}_visibility'],
                    forecast_data[f'hour_{hour}_wind_speed'],
                    forecast_data[f'hour_{hour}_wind_deg'],
                    forecast_data[f'hour_{hour}_wind_gust'],
                    forecast_data[f'hour_{hour}_weather_main'],
                    forecast_data[f'hour_{hour}_weather_description'],
                    forecast_data[f'hour_{hour}_pop']
                ]

            # Append daily forecast data (8 days)
            for day in range(8):
                values += [
                    forecast_data[f'day_{day}_timestamptz'],
                    forecast_data[f'day_{day}_summary'],
                    forecast_data[f'day_{day}_temp_day'],
                    forecast_data[f'day_{day}_temp_min'],
                    forecast_data[f'day_{day}_temp_max'],
                    forecast_data[f'day_{day}_temp_night'],
                    forecast_data[f'day_{day}_temp_eve'],
                    forecast_data[f'day_{day}_temp_morn'],
                    forecast_data[f'day_{day}_feels_like_day'],
                    forecast_data[f'day_{day}_feels_like_night'],
                    forecast_data[f'day_{day}_feels_like_eve'],
                    forecast_data[f'day_{day}_feels_like_morn'],
                    forecast_data[f'day_{day}_pressure'],
                    forecast_data[f'day_{day}_humidity'],
                    forecast_data[f'day_{day}_dew_point'],
                    forecast_data[f'day_{day}_wind_speed'],
                    forecast_data[f'day_{day}_wind_deg'],
                    forecast_data[f'day_{day}_wind_gust'],
                    forecast_data[f'day_{day}_weather_main'],
                    forecast_data[f'day_{day}_weather_description'],
                    forecast_data[f'day_{day}_clouds'],
                    forecast_data[f'day_{day}_pop'],
                    forecast_data[f'day_{day}_uvi']
                ]

            # Execute the SQL insert command
            cursor.execute(insert_query, values)

            # Commit the changes
            conn.commit()

            # Log the successful insert
            self.logger.log_sql_insert(api_call_id, int(datetime.now().timestamp()), f"Successfully inserted forecast data for {forecast_data['timestamp']}", None)
            self.logger.log_event("sql_insert_success", f"Record inserted for timestamp {forecast_data['timestamp']}")
            return 1

        except psycopg2.IntegrityError:
            # Handle SQL IntegrityError (e.g., duplicate records)
            conn.rollback()
            self.logger.log_event("sql_insert_failure", f"Integrity error for forecast {forecast_data['timestamp']}")
            self.logger.log_sql_insert(api_call_id, int(datetime.now().timestamp()), 'failure', "Duplicate record")
            self.failed_sql_inserts += 1  # Track failed inserts
            return 0

        except psycopg2.DatabaseError as e:
            # Handle other database-related errors
            conn.rollback()
            self.logger.log_event("sql_insert_failure", f"Database error: {e}")
            print(f"Database error: {e}")
            return 0

        except Exception as e:
            # Handle and log other SQL exceptions
            conn.rollback()
            self.logger.log_event("sql_insert_failure", f"Failed to insert data: {e}")
            self.logger.log_sql_insert(api_call_id, int(datetime.now().timestamp()), 'failure', str(e))
            self.failed_sql_inserts += 1  # Track failed inserts
            return 0

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_old_records(self):
        try:
            # Establish the database connection
            conn = psycopg2.connect(self.db_connection)
            cursor = conn.cursor()

            # Calculate the date 4 days ago from now
            four_days_ago = datetime.now() - timedelta(days=4)

            # Prepare the SQL delete statement
            delete_query = "DELETE FROM openweather_forecast_detail WHERE timestamp < %s"

            # Execute the SQL delete command
            cursor.execute(delete_query, (four_days_ago,))

            # Commit the changes
            conn.commit()

            # Log the successful deletion
            self.logger.log_event("sql_delete_success", f"Deleted records older than {four_days_ago}")

        except psycopg2.DatabaseError as e:
            # Handle other database-related errors
            conn.rollback()
            self.logger.log_event("sql_delete_failure", f"Database error: {e}")
            print(f"Database error: {e}")

        except Exception as e:
            # Handle and log other SQL exceptions
            conn.rollback()
            self.logger.log_event("sql_delete_failure", f"Failed to delete old records: {e}")
            print(f"Error: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def run(self):
        if self.control.check_daily_limit_reached():
            sys.exit(1)  # Exit the script to stop further processing

        # Get the current day
        current_day = datetime.now().strftime("%Y-%m-%d")

        # Call the OpenWeather API
        daily_forecast_data, api_call_id = self.call_openweather_api()

        if daily_forecast_data and api_call_id:
            # Extract and validate
            try:
                daily_forecast_result = self.extract_and_validate_weather_data(daily_forecast_data)
                # Display the result (for webpage or email content)
                #for key, value in daily_forecast_result.items():
                    #print(f"{key}: {value}")
                #self.insert_weather_data(daily_forecast_result)
            except ValueError as e:
                print(f"Validation Error: {e}")

        if daily_forecast_result:
            self.insert_forecast_data(daily_forecast_result, api_call_id)
            self.delete_old_records()  # Clean up old records after insertion

        # Log script success if processing completes
        if self.failed_requests or self.failed_sql_inserts > 0:
            self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'stopped-warn')
        else:
            self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'stopped-succ')
        self.logger.log_event("Success", f"Script completed, {self.failed_requests} request failures, and {self.failed_sql_inserts} failed inserts.")

