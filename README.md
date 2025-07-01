# Codex ControlCore Suite

This repo unifies three primary applications under the ControlCore irrigation and environmental monitoring system:

- `openweather`: Gathers and logs weather data from OpenWeather API
- `station_viewer`: Displays sensor and station data in a modern UI
- `controlcore_ai`: Provides contextual watering advice and decision logic

## Configuration

Copy `.env.example` to `.env` and provide real values for the database and MQTT
settings used by all modules.  Install the Python dependencies with
`pip install -r requirements.txt` after creating your virtual environment.

## Planned Structure

- Each module remains in its own subdirectory
- Shared configs and common code go in `shared/`
- A lightweight controller script coordinates execution

### Control AI Master

The master runner at `controlcore_ai.core.master` can be invoked periodically
via cron or a systemd timer. It always runs the watering `runner` and triggers
`advisor` and `forecast_regression` after their configured intervals elapse.
Use the environment variables `ADVISOR_INTERVAL_MINUTES` and
`FORECAST_REGRESSION_INTERVAL_MINUTES` or pass `--advisor-interval` and
`--forecast-interval` to adjust timings.

See [docs/forecast_accuracy.md](docs/forecast_accuracy.md) for details on the forecast regression workflow.

## Short Term Goals

- Enable unified testing and Codex-assisted review
- Standardize config and logging across modules

## Long Term Goals
- Prepare for containerization and field deployment


## Need to update the controlcore_ai.runner with proper command calls:
 id |    station     |    controller_id    |         sensor_id          | sensor_type | command | value |  unit   |      source      |  requestor_id   |          received_at          |                                     source_id                                      | du
ration | timestamp
----+----------------+---------------------+----------------------------+-------------+---------+-------+---------+------------------+-----------------+-------------------------------+------------------------------------------------------------------------------------+---
-------+------------


 60 | garden-hydrant | uno-r4-wifi-primary | BeetsTomatoes-USSolid      | valve-state | open    |   180 | seconds | manual_override  | web_app         | 2025-06-29 05:40:17-04        | excessus-home_garden-hydrant_uno-r4-wifi-primary_valve-state_BeetsTomatoes-USSolid |          |
 61 | garden-hydrant | uno-r4-wifi-primary | BeetsTomatoes-USSolid      | valve-state | open    |   180 | seconds | manual_override  | web_app         | 2025-06-29 16:20:53-04        | excessus-home_garden-hydrant_uno-r4-wifi-primary_valve-state_BeetsTomatoes-USSolid |          |
 62 | garden-hydrant | uno-r4-wifi-primary | CucumberWatermelon-USSolid |             | open    |       |         | advisor_schedule | watering_runner | 2025-06-30 00:09:40.916298-04 |                                                                                    |     5400 | 1751256581
 63 | garden-hydrant | uno-r4-wifi-primary | BeetsTomatoes-USSolid      |             | open    |       |         | advisor_schedule | watering_runner | 2025-06-30 00:09:40.916298-04 |                                                                                    |     3600 | 1751256581
 64 | garden-hydrant | uno-r4-wifi-primary | BeetsTomatoes-USSolid      | valve-state | open    |   180 | seconds | manual_override  | web_app         | 2025-06-30 04:10:43-04        | excessus-home_garden-hydrant_uno-r4-wifi-primary_valve-state_BeetsTomatoes-USSolid |          |
(63 rows)


