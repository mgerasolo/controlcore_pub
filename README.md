# Codex ControlCore Suite

This repo unifies three primary applications under the ControlCore irrigation and environmental monitoring system:

- `openweather`: Gathers and logs weather data from OpenWeather API
- `station_viewer`: Displays sensor and station data in a modern UI
- `controlcore_ai`: Provides contextual watering advice and decision logic

## Planned Structure

- Each module remains in its own subdirectory
- Shared configs and common code go in `shared/`
- A lightweight controller script coordinates execution

## Short Term Goals

- Enable unified testing and Codex-assisted review
- Standardize config and logging across modules

## Long Term Goals
- Prepare for containerization and field deployment
