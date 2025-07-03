# Codex ControlCore Suite

This repo unifies three primary applications under the ControlCore irrigation and environmental monitoring system:

- `openweather`: Gathers and logs weather data from OpenWeather API
- `station_viewer`: Displays sensor and station data in a modern UI
- `controlcore_ai`: Provides contextual watering advice and decision logic

## Configuration

Copy `.env.example` to `.env` and provide real values for the database and MQTT
settings used by all modules. Set `NEXT_PUBLIC_MQTT_WS_URL` to the WebSocket URL
for your broker (e.g. `ws://localhost:9001`). Install the Python dependencies
with `pip install -r requirements.txt` after creating your virtual environment.

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




