# Station Viewer

A local-first sensor and control platform for Arduino-based agricultural systems.

This project combines a Next.js-based UI, MQTT messaging, and lightweight Python services to enable real-time observation, control, and historical data visualization for field-deployed microcontroller stations.

## 🔧 Core Features

- 🖥 Web-based dashboard (Next.js) for live sensor monitoring and control
- 📡 MQTT messaging system with command validation and structured payloads
- 🌱 Arduino sketch for structured sensor broadcast and event-based triggers
- 🧠 Early groundwork for an AI-driven decision support layer (water, cover, crop rotate, harvest, alert)

## 📑 Sensor Abstraction

Sensor readings are treated as raw facts. Each reading is paired with metadata describing the `sensor_id`,
canonical `sensor_type`, unit, and source controller. Current canonical `sensor_type` values are:

- `temperature`
- `humidity`
- `barometric-pressure`
- `water-pressure`
- `valve-state`
- `soil-moisture`
- `light-intensity`

Frontend components and database logic rely on these strings for grouping and presentation.

Each reading includes two identifiers:

- **`sensor_id`** – human-defined label used in topics and UI
- **`source_id`** – system-generated `LOCATION_STATION_CONTROLLER_type_sensor_id` value for traceability

## 📦 Repo Structure

.
├── app/ # Next.js app entry
├── arduino/ # Arduino sketch for station firmware
├── components/ # React UI components
├── lib/ # Shared utilities
├── python/ # Backend Python services for data ingestion
├── public/ # Static assets
├── styles/ # Tailwind styling
├── types/ # TypeScript interfaces
└── database_definition.sql

### Python Service Configuration

Use dot_env

Install dependencies with `pip install -r python/requirements.txt`.

## 📈 What's Next

- Historical analysis via TimescaleDB or InfluxDB
- AI prediction framework for field actions
- Sync-ready version for deployment beyond LAN
- Italian localization & region-specific tuning

## 🚧 Status

Currently under development. Arduino sketch + dashboard + Python service are functional locally.

## 🤝 Collaboration

Open to feedback, collaborators, or just curious minds. Reach out if you're interested in applying this system in a real-world context (especially agriculture or environmental sensing).

---
For more on architecture, message format, and implementation notes, see [README_DETAILS.md](./README_DETAILS.md).

