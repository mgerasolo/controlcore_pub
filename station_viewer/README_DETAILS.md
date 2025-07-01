# ControlCore Station Viewer

A real-time MQTT-based monitoring and control dashboard for field-deployed Arduino stations.

This project includes:
- A **Next.js + V0-designed** frontend for real-time sensor data visualization and manual override control
- An **Arduino sketch** for publishing sensor readings and responding to control commands over MQTT
- Screenshots and example data to guide consistent layout and integration

---

## 🚀 Features

- Live MQTT subscription to `controlcore/#` using WebSocket
- **Physical View**: Groups sensors by physical `station → controller → sensors`
- **Logical View**: Groups sensors by functional `sensor_type`
- **Manual Overrides**: Send MQTT commands to control devices by `sensor_id`
- Commands include a `source_id` for tracing the originating sensor path
- Sensor freshness, pin, controller, and unit displayed
- Designed for small garden control systems and scale-out field deployments

## Sensor Abstraction

Sensor readings represent raw facts from the field. Each message contains a user
-defined `sensor_id` for display and a system-derived `source_id` for tracing.
Multiple metrics can share the same `sensor_id` when a physical module (e.g.
SHT31-D) exposes several data channels.

Example:

```json
{ "sensor_id": "StationExt-SHT-1", "sensor_type": "temperature", "value": 26.4, "unit": "°C", "source_id": "excessus-home_garden-hydrant_uno-r4-wifi-primary_temperature_StationExt-SHT-1" }
{ "sensor_id": "StationExt-SHT-1", "sensor_type": "humidity", "value": 43.1, "unit": "%RH", "source_id": "excessus-home_garden-hydrant_uno-r4-wifi-primary_humidity_StationExt-SHT-1" }
```

### Sensor Calibration

`SensorConfig.h` defines `offset` and `scale` fields. Each read function
applies `(raw + offset) * scale` before publishing. Adjust these per sensor to
calibrate measurements.

---

## 📁 Project Structure - Dev Reference - Designed to support modular frontend updates via [Vercel V0](https://v0.dev) and backend/firmware linting with OpenAI Codex.

```
codex_station_viewer/
├── arduino/                   # Arduino sketch and config for the station
│   ├── codex_station_viewer.ino
│   └── lib/ControlCore_Config.h
|   └-- lib/SensorConfig.h
|   └-- lib/WiFiCredentials.h
├── components/                # UI Components (cards, tabs, layout)
├── lib/                       # MQTT client and sensor grouping logic
├── types/                     # Shared types (e.g., SensorReading)
├── screenshots/               # UI screenshots with expected display states
├── public/                    # Static assets
├── app/                       # Next.js routing (V0 layout)
├── next.config.mjs            # Webpack fallback for MQTT compatibility
└── ...
```

---

## 📡 MQTT Message Format

Arduino publishes messages in this format to `controlcore/data/...`:

```json
{
  "station": "garden-hydrant",
  "controller": "uno-r4-wifi-primary",
  "sensor_id": "BeetsTomatoes-USSolid",
  "sensor_type": "water-pressure",
  "unit": "PSI",
  "value": 3.7,
  "pin": 14,
  "timestamp": 1724537123,
  "source_id": "excessus-home_garden-hydrant_uno-r4-wifi-primary_water-pressure_BeetsTomatoes-USSolid"
}
```

`timestamp` values use Unix epoch seconds synchronized from NTP at startup.

Example MQTT messages "on-the-wire":
$mosquitto_sub -h localhost -p 1883 -t 'controlcore/#'
{"station":"garden-hydrant","controller":"uno-r4-wifi-primary","sensor_id":"BeetsTomatoes-Valve","sensor_type":"valve-state","unit":"state","value":1,"pin":-1,"timestamp":1750489785,"source_id":"excessus-home_garden-hydrant_uno-r4-wifi-primary_valve-state_BeetsTomatoes-Valve"}
{"station":"garden-hydrant","controller":"uno-r4-wifi-primary","sensor_id":"BeetsTomatoes-USSolid","sensor_type":"water-pressure","unit":"PSI","value":106,"pin":14,"timestamp":1750489785,"source_id":"excessus-home_garden-hydrant_uno-r4-wifi-primary_water-pressure_BeetsTomatoes-USSolid"}
{"station":"garden-hydrant","controller":"uno-r4-wifi-primary","sensor_id":"BeetsTomatoes-Grieda","sensor_type":"water-flow","unit":"L/min","value":316,"pin":2,"timestamp":1750489785,"source_id":"excessus-home_garden-hydrant_uno-r4-wifi-primary_water-flow_BeetsTomatoes-Grieda"}


---

## 🧠 Logical View Grouping

Sensors are grouped by `sensor_type` for display. Canonical values include:

- `temperature`
- `humidity`
- `barometric-pressure`
- `water-pressure`
- `valve-state`
- `soil-moisture`
- `light-intensity`

---

## 🧪 All Commands - AI, Simple Automation, and Manual

Send commands to:
```
controlcore/command/...
```

Payload:
```json
{
  "station": "garden-hydrant",
  "controller": "uno-r4-wifi-primary",
  "sensor_id": "BeetsTomatoes-Valve",
  "sensor_type": "valve-state",
  "unit": "seconds",
  "value": 300,
  "command": "open",
  "source": "manual_override",
  "requestor_id": "kevin_cli",
  "timestamp": 162,
  "source_id": "excessus-home_garden-hydrant_uno-r4-wifi-primary_valve-state_BeetsTomatoes-Valve"
}
```

If the value is 0 or exceeds 900 seconds with `unit: "seconds"`, the Arduino defaults to a 15-minute timeout to prevent accidental continuous watering.


Command Fields:
 - station: the sub-region area / physical container
 - controller: the controller physically wired to the sensor/control module
 - sensor_id: the globally unique identifier for the target sensor or actuator
 - sensor_type: one of the canonical types (e.g., temperature, valve-state)
 - unit: measurement or configuration units (e.g., L/min, state, seconds, °C)
 - command: action label (e.g., "open", "set_high", "calibrate")
 - value: numeric input or literal state (e.g., 1, 95, 300)
 - source_id: full path at the moment in time. used for tracing.

This distinction allows flexible command types: timed activations, range setting, configuration changes, simple on/off, etc.

✅ For time-limited actuator commands like valves, use unit: "seconds" and value: <duration_in_seconds>.
The command "open" with "value": 300 and "unit": "seconds" means: open for 5 minutes.

***Detailed Examples of possible actuator implemetation at the end of document***

---

## 📸 Screenshots

Note: Screenshots not included in this repo snapshot — please refer to live UI or development build for layout reference.

---

## 🧰 Stack

- Frontend: [Next.js 15] with UI designed using [V0.dev](https://v0.dev)
- MQTT: [mqtt.js](https://github.com/mqttjs/MQTT.js) via WebSocket
- Arduino board: UNO R4 WiFi with relay + analog + pulse sensors

---

## 📦 Setup Instructions

```bash
pnpm install
pnpm dev  # Start local dev server
```
```bash
pip install -r ../requirements.txt
SENSOR_DB_URL="postgresql://controlcore_user:secret@localhost/controlcore" \
  MQTT_HOST=localhost python python/src/services/cc_data_manager.py
```

Ensure you have a running MQTT broker (e.g., Mosquitto) with WebSocket support on port 9001.

---

## 👷 Future Enhancements

- Sensor tag-based grouping
  - More expansion on the VLAN concept where the user can custom group devices
- Multi-station field UI view
  - The Station Viewer can filter for field use to a manageable number of stations
  - A higher level Location Viewer, would show a comprehensive view of the stations, weather, historical, predictive, etc UI
- Extend User Customization
  - Configurable color rules for stale or alarming values
  - Set the broker in an accessible config file for both Arduino and webpage
  - Extend sensor definitions from the sketches into a companion file users can easily customize
- Notifications - on page, email, SMS
  - Monitoring, activity, proactive suggestions


##🛠 In-Progress: /config Topic for Real-Time Reconfiguration
  While current control messages target immediate actions (e.g., "open valve", "set threshold"), the system is built to support more dynamic behavior.

  We are planning to introduce a dedicated configuration topic:
  --  controlcore/config/...
  
  This new channel will support structured, broadcasted configuration updates. Its goals include:

  🔧 Dynamic reconfiguration of sensor modules

  🧠 Multi-parameter updates for complex controllers

  📏 Changes to operational thresholds, sampling rates, calibration offsets, etc.

  All configuration messages will follow the same structured format as data and control messages (station, sensor_id, sensor_type, etc.). Like sensor readings, configuration state will be:

  ✅ Broadcast once per change

  🔁 Periodically rebroadcast (e.g., hourly) for state continuity

  📡 Passively confirmable by observing message history — no dedicated ACK/NACK required

  🎯 Design Principle: All node behavior should be observable and inferable through MQTT broadcast alone. Nothing is trusted unless reasserted.


