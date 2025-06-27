# TODO

---
System Messaging Completion Checklist

- [ ] Refactor water valve control message to include full metadata

The front end and Arduino firmware now use the unified control message structure described in README.md.

---
## 🧪 MQTT Message Refactor (Codex)

- [X] Manual valve commands from the webpage publish messages like:

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
  "requestor_id": "web_app",
  "timestamp": 162,
  "source_id": "excessus-home_garden-hydrant_uno-r4-wifi-primary_valve-state_BeetsTomatoes-Valve"
}
```

### New Issues from Sensor Abstraction Refactor
- [X] Reading logic per `sensor_type` is stubbed and needs proper drivers
- [x] Extend `cc_data_manager.py` to validate canonical `sensor_type` values
- [x] Modify `cc_data_manager.py` to store the new `source_id` field
- [x] Parameterize DB and MQTT configuration via dot env


### New Issues from Abstraction Refactor Attempt 2

The codex_station_viewer.ino needs to be scrubbed for consistency and flexibility:

Sample errors when compiling:
In file included from C:\Users\exces\OneDrive\Documents\Arduino\codex_station_viewer\codex_station_viewer.ino:12:0:
C:\Users\exces\OneDrive\Documents\Arduino\codex_station_viewer\lib\SensorConfig.h:88:1: error: invalid conversion from 'int' to 'const char*' [-fpermissive]
invalid conversion from 'float (*)(const SensorConfig&)' to 'int' [-fpermissive]
cannot convert 'const char*' to 'float (*)(const SensorConfig&)' in initialization
invalid conversion from 'uint8_t {aka unsigned char}' to 'const char*' [-fpermissive]
invalid conversion from 'float (*)(const SensorConfig&)' to 'int' [-fpermissive]
[...]
Compilation error: invalid conversion from 'int' to 'const char*' [-fpermissive]