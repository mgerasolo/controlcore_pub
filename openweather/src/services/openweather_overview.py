import requests
import sys
from datetime import datetime, timezone, timedelta
import psycopg2
import sys
import time
import json
import os
from src.services.api_logger import APILogging
from src.config.config import LATITUDE, LONGITUDE, WEATHER_FORECAST_DB_CONNECTION, API_KEY, DAILY_OVERVIEW_LIMIT
from src.services.api_control import APIControl

class OpenWeatherDailyOverview:
    def __init__(self):
        self.latitude = LATITUDE
        self.longitude = LONGITUDE
        self.api_key = API_KEY
        self.logger = APILogging()
        self.failed_requests = 0
        self.failed_sql_inserts = 0
        self.daily_limit = DAILY_OVERVIEW_LIMIT  # Total API call limit per day for this script
        self.start_time = time.time()  # Track when rate-limiting minute starts
        self.db_connection = WEATHER_FORECAST_DB_CONNECTION
        self.platform = "OpenWeather"
        self.api_call_type_id = 3
        self.script_name = "openweather_overview_get"
        self.api_call_alt_name = "overview"
        self.api_call_type = 'Weather Overview'
        self.control = APIControl(self.api_call_type_id, self.script_name, self.platform, self.api_call_alt_name, self.daily_limit)

    def call_openweather_api(self, date):
        try:
            # Retrieve the API prototype URL
            api_prototype = self.logger.get_api_prototype(self.platform, self.api_call_type)
            base_url = api_prototype.format(lat=self.latitude, lon=self.longitude, API_key=self.api_key)

            self.logger.log_event("Request", f"Calling API: OpenWeather daily overview")

            params = {
                'lat': self.latitude,
                'lon': self.longitude,
                'appid': self.api_key,
                'date': date,
                'units': 'imperial'
            }


            max_retries = 3  # Maximum number of retries
            retry_count = 0
            call_timestamp = int(datetime.now().timestamp())
            request_payload = base_url

            for attempt in range(max_retries):
                try:
                    response = requests.get(base_url, params=params, timeout=5)  # Set a timeout of 15 seconds
                    response_code = response.status_code
                    response_message = f"Successfully retrieved overview" if response_code == 200 else f"API call failed with status {response_code} - {response.text}"

                    # Log the API call in the database
                    api_call_id = self.logger.log_api_call(
                        call_timestamp, self.api_call_type_id, 'API Call', request_payload,
                        response_code, response_message, retry_count,
                        "OpenWeather API Overview"
                    )

                    # Handle successful response
                    if response_code == 200:
                        self.logger.log_event("Success", f"Data received for overview")
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
        Extracts and validates the weather overview data and returns a dictionary
        that is easily consumable for displaying on a webpage or sending via email.
        """
        # Required fields for validation
        required_fields = ['lat', 'lon', 'tz', 'date', 'units', 'weather_overview']

        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing fields in weather data: {missing_fields}")

        # Validate the data types (Example: lat/lon should be float, date should be str)
        try:
            lat = float(data['lat'])
            lon = float(data['lon'])
            tz = str(data['tz'])
            date = str(data['date'])  # Assuming date is in "YYYY-MM-DD" format
            units = str(data['units'])  # Should be 'imperial' or 'metric'
            weather_overview = str(data['weather_overview'])
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid data format: {e}")

        # Extract validated data into a structured format for display
        validated_data = {
            'lat': lat, 
            'lon': lon,
            'timezone': tz,
            'date': date,
            'units': units,
            'overview': weather_overview
        }

        return validated_data

    def insert_weather_data(self, weather_data, api_call_id, day):
        try:
            conn = psycopg2.connect(self.db_connection)
            cursor = conn.cursor()

            insert_query = """
            INSERT INTO overview_data (date, lat, lon, timezone, weather_overview, api_call_id, day)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                weather_data['date'], 
                weather_data['lat'], 
                weather_data['lon'], 
                weather_data['timezone'], 
                weather_data['overview'], 
                api_call_id,
                day
            ))

            # Maintain only the last 4 calls (8 rows)
            cursor.execute("""
                DELETE FROM overview_data
                WHERE id NOT IN (
                    SELECT id FROM overview_data
                    ORDER BY last_updated DESC
                    LIMIT 8
                )
            """)

            conn.commit()
            cursor.close()

            # Log successful insert
            self.logger.log_sql_insert(api_call_id, int(datetime.now().timestamp()), f"Successfully inserted overview {weather_data['date']}", None)
            self.logger.log_event("sql_insert_success", f"Record inserted for timestamp {weather_data['date']}")
            return 1

        except psycopg2.IntegrityError:
            # Handle and log SQL IntegrityError (e.g., duplicate records)
            conn.rollback()
            self.logger.log_event("sql_insert_failure", f"Integrity error for overview {weather_data['date']}")
            self.logger.log_sql_insert(api_call_id, datetime.now().timestamp(), 'failure', "Duplicate record")
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
            self.logger.log_sql_insert(api_call_id, datetime.now().timestamp(), 'failure', str(e))
            self.failed_sql_inserts += 1  # Track failed inserts
            return 0

        finally:
            if conn:
                cursor.close()
                conn.close()



    def run(self):

        if(self.control.check_daily_limit_reached()):
            sys.exit(1)  # Exit the script to stop further processing

        # Get the current day
        current_day = datetime.now().strftime("%Y-%m-%d")

        # Get the next day by adding one day to the current date
        next_day = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        # Call the OpenWeather API
        current_day_data, api_call_id = self.call_openweather_api(current_day)

        if current_day_data and api_call_id:
            # Extract and validate
            try:
                current_day_result = self.extract_and_validate_weather_data(current_day_data)
                # Display the result (for webpage or email content)
                #for key, value in current_day_result.items():
                #    print(f"{key}: {value}")
                #self.insert_weather_data(current_day_result)
            except ValueError as e:
                print(f"Validation Error: {e}")

        if(current_day_result):
            self.insert_weather_data(current_day_result, api_call_id, 0)

        time.sleep(2)

        # Call the OpenWeather API
        next_day_data, api_call_id = self.call_openweather_api(next_day)

        if next_day_data and api_call_id:
            # Extract and validate
            try:
                next_day_result = self.extract_and_validate_weather_data(next_day_data)
                # Display the result (for webpage or email content)
                #for key, value in next_day_result.items():
                #    print(f"{key}: {value}")
                
            except ValueError as e:
                print(f"Validation Error: {e}")
        
        if(next_day_result):
            self.insert_weather_data(next_day_result, api_call_id, 1)


        # Log script success if processing completes
        if self.failed_requests or self.failed_sql_inserts > 0:
            self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'stopped-warn')
        else:
            self.logger.insert_tracking_log(self.script_name, self.platform, self.api_call_alt_name, 'stopped-succ')
        self.logger.log_event("Success", f"Script completed, {self.failed_requests} request failures, and {self.failed_sql_inserts} failed inserts.")


