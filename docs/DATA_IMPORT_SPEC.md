# Data Import Specification

This document describes the preferred data formats for importing historical data into ControlCore.

---

## Option 1: CSV Files (Recommended)

CSV is the most portable and easiest to validate. One file per table.

### Weather Data: `daily_summary_data.csv`

```csv
location_name,date,temperature_min,temperature_max,temperature_afternoon,precipitation_total,humidity_afternoon,wind_max_speed,wind_max_direction
Fincastle,2024-01-15,28.5,45.2,42.1,0.12,65,12.5,225
Fincastle,2024-01-16,32.1,48.7,45.3,0.00,58,8.2,180
Roanoke,2024-01-15,30.2,47.8,44.5,0.08,62,15.1,210
```

**Columns:**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| location_name | text | yes | Location name (we'll map to location_id) |
| date | date | yes | YYYY-MM-DD format |
| temperature_min | float | no | Daily minimum temperature (°F) |
| temperature_max | float | no | Daily maximum temperature (°F) |
| temperature_afternoon | float | no | Afternoon temperature (°F) |
| precipitation_total | float | no | Total precipitation (inches) |
| humidity_afternoon | float | no | Afternoon humidity (%) |
| wind_max_speed | float | no | Max wind speed (mph) |
| wind_max_direction | float | no | Wind direction (degrees) |

### Locations: `locations.csv`

```csv
id,name,latitude,longitude,description
1,Fincastle,37.4993,-79.877,Main garden location
2,Rome,34.257,-85.165,Secondary site
3,Roanoke,37.271,-79.9414,Weather station
```

### Sensor Readings (if available): `sensor_readings.csv`

```csv
node_name,capability,timestamp,value,unit
potato-patch-moisture,soil_moisture,2024-01-15T14:30:00Z,45.2,%
potato-patch-moisture,soil_temperature,2024-01-15T14:30:00Z,52.1,°F
main-valve,flow_rate,2024-01-15T14:30:00Z,2.5,gpm
```

### Node Registry (if available): `nodes.csv`

```csv
uuid,friendly_name,node_type,hardware_type,location,description
550e8400-e29b-41d4-a716-446655440001,Potato Patch Sensor,hybrid,esp32,Garden Zone A,Moisture and temp sensor with valve
550e8400-e29b-41d4-a716-446655440002,Main Valve Controller,actuator,arduino,Pump House,Controls main irrigation valve
```

---

## Option 2: PostgreSQL Dump

If already using PostgreSQL, a dump is fastest:

```bash
# Export specific tables
pg_dump -h localhost -U username -d database_name \
  --table=daily_summary_data \
  --table=locations \
  --table=sensor_readings \
  --data-only \
  --format=plain \
  -f export.sql

# Or CSV export from psql
\copy daily_summary_data TO 'daily_summary_data.csv' WITH CSV HEADER;
\copy locations TO 'locations.csv' WITH CSV HEADER;
```

---

## Option 3: JSON Lines (JSONL)

One JSON object per line. Good for nested/complex data.

### `daily_weather.jsonl`
```json
{"location": "Fincastle", "date": "2024-01-15", "temp": {"min": 28.5, "max": 45.2}, "precip": 0.12}
{"location": "Fincastle", "date": "2024-01-16", "temp": {"min": 32.1, "max": 48.7}, "precip": 0.00}
```

### `sensor_readings.jsonl`
```json
{"node": "potato-patch", "sensor": "moisture", "ts": "2024-01-15T14:30:00Z", "value": 45.2, "unit": "%"}
{"node": "potato-patch", "sensor": "temperature", "ts": "2024-01-15T14:30:00Z", "value": 52.1, "unit": "F"}
```

---

## Data We're Most Interested In

**Priority 1 - Weather Data:**
- Daily summaries (temp min/max, precipitation, humidity, wind)
- Date range covered
- Locations with coordinates

**Priority 2 - Sensor Readings (if available):**
- Historical sensor data from any IoT nodes
- Timestamps and values
- What sensors/capabilities exist

**Priority 3 - Node Configuration (if available):**
- What nodes exist
- What sensors/actions each has
- UUID mappings

---

## Import Process

Once we receive the data, we'll:

1. Validate CSV structure
2. Map location names to location_ids (or create new locations)
3. Bulk import using PostgreSQL COPY:
   ```sql
   COPY daily_summary_data FROM 'daily_summary_data.csv' WITH CSV HEADER;
   ```
4. Verify row counts and date ranges
5. Update schema embeddings if new columns/tables

---

## Questions for Kevin

1. **Date range:** What's the earliest and latest date in your data?
2. **Locations:** Which locations have data? (Fincastle, Rome, others?)
3. **Data source:** Is this from OpenWeather API, local sensors, or both?
4. **Sensor data:** Do you have historical readings from ESP32/Arduino nodes?
5. **Database:** Are you using PostgreSQL, SQLite, or something else?

---

## File Transfer

Options for getting files to us:
- **GitHub:** Add to a branch or create a data release
- **Direct:** Email/share CSV files (if small)
- **S3/Cloud:** Upload to shared bucket

For large datasets (>100MB), a PostgreSQL dump or compressed CSV is preferred.
