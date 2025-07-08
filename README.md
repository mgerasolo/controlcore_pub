# Codex ControlCore Suite

This repo unifies three primary applications under the ControlCore irrigation and environmental monitoring system:

- `controlcore_main_site`: The page users use daily to view and manage their organization's systems - Currently same as Location
- `openweather`: Gathers and logs weather data from OpenWeather API
- `station_viewer`: Displays sensor and station data in a modern UI - Troubleshooting Focus
- `controlcore_ai`: Provides contextual watering advice and decision logic

## Configuration

Copy `.env.example` to `.env` and provide real values for the database and MQTT
settings used by all modules. Set `NEXT_PUBLIC_MQTT_WS_URL` to the WebSocket URL
for your broker (e.g. `ws://localhost:9001`). Install the Python dependencies
with `pip install -r requirements.txt` and the test packages with
`pip install -r requirements-dev.txt` after creating your virtual environment.
Specify `BASELINE_SENSOR_ID` with the `source_id` of your on-site temperature
sensor so the weather page can display the most recent reading.
Set `OPENWEATHER_ARCHIVE_CUTOFF_DAYS` to control how old weather data must be before
being moved to long‑term tables. `OPENWEATHER_ARCHIVE_LOCATIONS` lists the
friendly names that have `<name>_daily` and `<name>_hourly` tables used for archival.
Set `SAURON_API_URL` to the `/chat` route exposed by the FastAPI server.
Provide `GANDALF_SQL_URL`, `GANDALF_ANALYZE_URL` and `GANDALF_REPHRASE_URL` so
the API can call Gandalf for SQL generation, analysis and question cleanup.
Gandalf in turn contacts Ollama using `OLLAMA_URL` with the models specified by
`OLLAMA_SQL_MODEL` and `OLLAMA_SUMMARY_MODEL`.

## Planned Structure

- Each module remains in its own subdirectory
- Shared configs and common code go in `shared/`
- A lightweight controller script coordinates execution

### Control AI Master

The master runner at `controlcore_ai.core.master` can be invoked periodically
via cron or a systemd timer. It always runs the watering `runner` and triggers
`advisor` after its configured interval elapses. Two execution modes are
available:

- **heavy** (default) &ndash; runs `forecast_regression` whenever its own
  interval has elapsed
- **light** &ndash; skips the regression step entirely

Choose the mode with `--mode light|heavy` or the `MASTER_MODE` environment
variable. The variables `ADVISOR_INTERVAL_MINUTES` and
`FORECAST_REGRESSION_INTERVAL_MINUTES` or the arguments `--advisor-interval` and
`--forecast-interval` control the internal schedules.

Recommended cron frequencies are roughly every five minutes for `runner`
(handled by the master invocation), regularly for `advisor`, and no more than
every four hours for `forecast_regression`.

Example usage:

```bash
# default heavy mode
python -m controlcore_ai.core.master

# explicitly run heavy mode
python -m controlcore_ai.core.master --mode heavy

# run in light mode
python -m controlcore_ai.core.master --mode light
```

Each core script writes execution details to its own log file under
`controlcore_ai/logs/`:

- `runner.log`
- `advisor.log`
- `forecast_regression.log`
- `master.log`

See [docs/forecast_accuracy.md](docs/forecast_accuracy.md) for details on the forecast regression workflow.
See [docs/schema_introspection.md](docs/schema_introspection.md) for how table schema information is gathered.

### FastAPI Server

Start the API with:

```bash
./run_sauron_api.sh
```

The server listens on port 8000 and sends requests to Gandalf using
`GANDALF_REPHRASE_URL`, `GANDALF_SQL_URL` and `GANDALF_ANALYZE_URL`. Gandalf
then talks to Ollama via `OLLAMA_URL` using the models defined by
`OLLAMA_SQL_MODEL` and `OLLAMA_SUMMARY_MODEL`. Configure your front end to send
chat requests to `SAURON_API_URL`.

## Short Term Goals

- Finish setting up basic AI SQL helper / research assistant / AI Chat Assistant
  -  It seems logical the first AI support would be to retrieve data from our storage systems
  -  We have started with a concept of llama3 and deepseek coding working in tandem to:
    -  Interpret the user's request 
    -  Create a proper SQL query
    -  Send the query
    -  Interpret the data result in context to the request
    -  Send a response that is rich and web friendly
    -  Display the response to the user

Naming convention for clarity:
Sauron - The machine running ControlCore main services - data gathering, sensors, controllers, MQTT, Postgres
Gandalf - A separate machine on the same LAN (currently) with hardware more appropriate to running AI models

This may actually be similar to a real deployment. 

Our current largest problem is the AI agents on Gandalf arent aware of, not just the database schema, but that there are three databases.
We have a concept of database structure:
controlcore - the database used by the application for sensors, control, tracking, etc - essentially immutable in definitions
openweather_historical - external, potentially large, historical records the user can provide or, in this bundle, the OpenWeather sub app can build
openweather_forecast - external, volitile database of records that frequently change - in our cast forecasts also provided by OpenWeather

We are hoping this separation helps containerization and customization in the future.

What we have tried to send it so far with the references in /shared resulted in a lack of handling the three databases. 

ie. 
sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$ curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How much rain did Fincastle get in June 2020?"}'
{"detail":"SQL execution failed: only SELECT queries are allowed"}

(cc_data_manager) sauron@sauron:~/projects/codex_controlcore_agg$ ./run_sauron_api.sh
```sql
SELECT SUM(precipitation_total) as total_rainfall
FROM openweather_historical.fincaste_daily
WHERE date BETWEEN '2020-06-01' AND '2020-06-30';
```

So, our best case has stalled at bad reference to schema and a mistake in the table name. 

-----
UPDATE: Problems still with setting up a SQL request that mirrors reality.  Recommend add a first pass to LLM to reformat the request and present a simpler problem to the SQL generator.
Example relating to a sensor:

sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$ curl -X POST http://localhost:8000/chat -H "Content-Type: application/json"   -d '{"question": "What is the status of BeetsTomatoes-USSolid valve?"}'
{"summary":"**Summary**\n\nThe BeetsTomatoes-USSolid valve has no running configuration applied. The query results are empty, indicating that there is no current configuration associated with this valve.\n\n**Chart Recommendation**\n\nA simple bar chart with a single category (valve name) would effectively illustrate the lack of data for this valve."}sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$
sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$ curl -X POST http://localhost:8000/chat -H "Content-Type: application/json"   -d '{"question": "What is the current state of BeetsTomatoes-USSolid valve?"}'
{"summary":"**Valve Status: BeetsTomatoes-USSolid**\n\nThe current state of the BeetsTomatoes-USSolid valve shows no running configuration applied.\n\n**Recommendation:** A bar chart with categorical X-axis (e.g., \" Valve Status\") and a binary Y-axis (e.g., \"Applied\" vs. \"Not Applied\") would effectively visualize this data, highlighting the absence of any running configuration for this valve."}sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$
sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$ curl -X POST http://localhost:8000/chat -H "Content-Type: application/json"   -d '{"question": "Check the control log for recent events?"}'
{"summary":"**Recent Events Summary**\nNo recent events have been reported to the controller log within the past 30 days. The query returned an empty result set.\n\n**Recommended Chart:**\nNone (no data available)"}sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$
sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$ curl -X POST http://localhost:8000/chat -H "Content-Type: application/json"   -d '{"question": "Check the control_log for recent command."}'
{"detail":"SQL execution failed: syntax error at or near \"```\"\nLINE 1: ```sql\n        ^\n"}sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$
sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$ curl -X POST http://localhost:8000/chat -H "Content-Type: application/json"   -d '{"question": "Check the sensor_data for BeetsTomatoes-USSolid."}'
{"detail":"SQL execution failed: syntax error at or near \"^C
sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$ curl -X POST http://localhost:8000/chat -H "Content-Type: application/json"   -d '{"question": "Check the sensor_^Cta for BeetsTomatoes-USSolid."}'
sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$ curl -X POST http://localhost:8000/chat -H "Content-Type: application/json"   -d '{"question": "Check the controlcore sensor_data for recent values."}'
{"detail":"SQL execution failed: syntax error at or near \"```\"\nLINE 1: ```sql\n        ^\n"}sauron@sauron:~/projects/codex_controlcore_agg/sauron_api$
---
Original SQL: SELECT running_config_applied
FROM controlcore.controllers
WHERE controller_id = 'BeetsTomatoes-USSolid' AND config_source = 'valve';
Stripped SQL: SELECT running_config_applied
FROM controllers
WHERE controller_id = 'BeetsTomatoes-USSolid' AND config_source = 'valve';
INFO:     127.0.0.1:34056 - "POST /chat HTTP/1.1" 200 OK
Original SQL: SELECT running_config_applied
FROM controlcore.controllers
WHERE controller_id = 'BeetsTomatoes-USSolid';
Stripped SQL: SELECT running_config_applied
FROM controllers
WHERE controller_id = 'BeetsTomatoes-USSolid';
INFO:     127.0.0.1:39364 - "POST /chat HTTP/1.1" 200 OK
Original SQL: SELECT * FROM controlcore.controller_health WHERE last_reported > (CURRENT_DATE - INTERVAL '30 days');
Stripped SQL: SELECT * FROM controller_health WHERE last_reported > (CURRENT_DATE - INTERVAL '30 days');
INFO:     127.0.0.1:37058 - "POST /chat HTTP/1.1" 200 OK
Original SQL: ```sql
SELECT * FROM controlcore.controllers WHERE controller_id = 'YOUR_CONTROLLER_ID' ORDER BY last_seen DESC LIMIT 1;
```
Stripped SQL: ```sql
SELECT * FROM controllers WHERE controller_id = 'YOUR_CONTROLLER_ID' ORDER BY last_seen DESC LIMIT 1;
```
INFO:     127.0.0.1:37076 - "POST /chat HTTP/1.1" 500 Internal Server Error
Original SQL: ```sql
SELECT *
FROM controlcore.controllers
WHERE controller_id = 'BeetsTomatoes-USSolid'
```
Stripped SQL: ```sql
SELECT *
FROM controllers
WHERE controller_id = 'BeetsTomatoes-USSolid'
```
INFO:     127.0.0.1:37298 - "POST /chat HTTP/1.1" 500 Internal Server Error
Original SQL: ```sql
SELECT * FROM controlcore.controllers WHERE controller_id = 'sensor_data' ORDER BY last_seen DESC LIMIT 1;
```
Stripped SQL: ```sql
SELECT * FROM controllers WHERE controller_id = 'sensor_data' ORDER BY last_seen DESC LIMIT 1;
```
INFO:     127.0.0.1:46250 - "POST /chat HTTP/1.1" 500 Internal Server Error



-----
## Long Term Goals
- Prepare for containerization and field deployment
- Simplify set up and component configuration
- User based access control
- Arduino Controllers with /config topic for live tuning, sensor config changes, even config pull by lightweight boot sketch
- Configs stored on Arduino in a start, run CISCO style. 

## Note for OpenWeather Historical
                   List of relations
 Schema |           Name            |   Type   | Owner
--------+---------------------------+----------+--------
 public | ar_internal_metadata      | table    | sauron
 public | daily_summary_data        | table    | sauron  - Recently gathered and depository for new daily summaries data - Collected ~ 00:05 - 01:00
 public | daily_summary_data_id_seq | sequence | sauron
 public | fincastle_daily           | table    | sauron  - Vetted, often large, historical data for a lat/lon Location
 public | fincastle_hourly          | table    | sauron  - Vetted, often large, historical data for a lat/lon Location
 public | hourly_data               | table    | sauron  - Recently gathered and despository for new hourly historical data - Collected ~ 00:05 - 01:00
 public | locations                 | table    | sauron
 public | locations_id_seq          | sequence | sauron
 public | openweather_data_id_seq   | sequence | sauron
 public | rome_daily                | table    | sauron - Vetted, often large, historical data for a lat/lon Location
 public | rome_hourly               | table    | sauron - Vetted, often large, historical data for a lat/lon Location
 public | schema_migrations         | table    | sauron
(12 rows)

## OpenWeather Forecast database is for the current lat/lon location only - collected every 4 hours


##Weather Page Concept - Subject to Practicality 
🌤️ Weather Tab Layout (Minimalist, Informative)
🧭 Section 1: "Now & Recent Past" Overview
Layout: Two horizontal rows of cards (no charts needed)

Yesterday (OW)	Today (OW so far)	Right Now (on-site Location authoritative sensors if configured)
High: 82°F	High: 79°F	Temp: 77°F
Low: 65°F	Low: 66°F	Wind: 12mph
Rain: 0.25in	Rain: 0.10in	RH: 53%
Wind: 15mph	Wind: 14mph	Overview: "Clear skies, calm conditions."

✅ Purpose: Human-level "how it’s been trending" without charts.

📅 Section 2: Forecast Summary
Title: "Next 2 Days"

Visual: Horizontally stacked day cards (e.g. today, tomorrow, day after)

📆 Wed	📆 Thu	📆 Fri
High: 80°F	High: 78°F	High: 76°F
Low: 67°F	Low: 65°F	Low: 64°F
Rain: 0.15in	0.00in	0.05in
Wind: 12mph	10mph	14mph
Summary: "Partly cloudy."	"Cooler with wind."	"Light rain possible."

🧠 Section 3: AI Overview (Optional overlay or expandable box)
Table overview_data: 
  - `day` column: 0 for the current day and 1 for the next day forecast

"Conditions have been stable with cooling trends overnight and scattered light showers. Expect mild temperatures continuing into the weekend with moderate winds."

Format: Simple paragraph, centered in a card.

📊 Section 4: Comparison Selector (Toggle-driven Stats)
“Compare last X days” → Choose: 1, 5, 10, 15, 20

Dropdown or Button Toggle: “Days: [1] [5] [10] [15] [20]”

Metrics: Avg Max Temp, Min Temp, Avg Wind, Total Rain, Avg RH

Metric	Last 5 Days	Last 15 Days
Max Temp Avg	81°F	84°F
Min Temp Avg	66°F	64°F
Total Rain	0.6 in	2.1 in
Wind Avg	12 mph	10 mph
RH Avg	52%	55%

🔁 Optional: make it auto-refresh daily (cache once a day)

📊 Section 5: Comparison Selector (Toggle-driven Stats) - This is a comparison over years for the current day.
“Compare last X years” → Choose: 1, 5, 10, 15, 20

Dropdown or Button Toggle: “Years: [1] [5] [10] [15] [20]”

Metrics: Avg Max Temp, Min Temp, Avg Wind, Total Rain, Avg RH

Metric          Today   Last 5 Years
Max Temp Avg    81°F    84°F
Min Temp Avg    66°F    64°F
Total Rain      0.6 in  2.1 in
Wind Avg        12 mph  10 mph
RH Avg  52%     55%

🔁 Optional: make it auto-refresh daily (cache once a day)



🔧 No-Fuss Implementation Tips

Data can be fetched preformatted in Python (e.g., calculate high/low/avg for each day range server-side)

Python can be very helpfu, along with additional storage space in files or database tables. If new tables are needed, document them in the database_schemas dir. 

The user has Grafana and full access to the data.  The goal is not to show analysis from every angle.  The intention is to show the important day to day information with some easy, dynamic historical context. 

