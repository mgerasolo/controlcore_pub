# Data Import Specification

This document describes the preferred data formats for importing historical data into ControlCore.

Since Kevin's source database is PostgreSQL (the original ControlCore), we can use direct PostgreSQL exports.

---

## Option 1: PostgreSQL Dump (Recommended)

Since Kevin's database uses the same schema as ControlCore, the fastest approach is a pg_dump:

```bash
# Connect to your PostgreSQL database
psql -h localhost -U sauron -d your_database

# Export all weather data tables (data only, no schema)
pg_dump -h localhost -U sauron -d your_database \
  --table=daily_summary_data \
  --table=hourly_data \
  --table=fincastle_daily \
  --table=fincastle_hourly \
  --table=rome_daily \
  --table=rome_hourly \
  --table=locations \
  --data-only \
  --format=plain \
  -f controlcore_data_export.sql
```

This will give us the exact data with location_id references preserved.

---

## Option 2: CSV Exports (Alternative)

If you prefer CSV, run these from within `psql`:

```sql
-- Connect first
psql -h localhost -U sauron -d your_database

-- Export each table to CSV
\copy locations TO 'locations.csv' WITH CSV HEADER;
\copy daily_summary_data TO 'daily_summary_data.csv' WITH CSV HEADER;
\copy hourly_data TO 'hourly_data.csv' WITH CSV HEADER;
\copy fincastle_daily TO 'fincastle_daily.csv' WITH CSV HEADER;
\copy fincastle_hourly TO 'fincastle_hourly.csv' WITH CSV HEADER;
\copy rome_daily TO 'rome_daily.csv' WITH CSV HEADER;
\copy rome_hourly TO 'rome_hourly.csv' WITH CSV HEADER;
```

---

## Kevin's Exact Table Schemas

Based on `openweather_historical.sql`, here are the table structures:

### `daily_summary_data` (Main weather data)
| Column | Type | Description |
|--------|------|-------------|
| id | integer | Primary key |
| lat | numeric(10,6) | Latitude |
| lon | numeric(10,6) | Longitude |
| tzoff | integer | Timezone offset |
| date | integer | **Unix timestamp** (not date!) |
| units | text | Unit system used |
| cloud_cover_afternoon | integer | Cloud cover % |
| humidity_afternoon | integer | Humidity % |
| precipitation_total | real | Total precipitation |
| temperature_min | real | Daily min temp |
| temperature_max | real | Daily max temp |
| temperature_afternoon | real | Afternoon temp |
| temperature_night | real | Night temp |
| temperature_evening | real | Evening temp |
| temperature_morning | real | Morning temp |
| pressure_afternoon | integer | Atmospheric pressure |
| wind_max_speed | real | Max wind speed |
| wind_max_direction | integer | Wind direction (degrees) |
| location_id | integer | FK to locations |

### `hourly_data` (Detailed hourly readings)
| Column | Type | Description |
|--------|------|-------------|
| id | integer | Primary key |
| dt | integer | Unix timestamp |
| lat, lon | numeric(10,6) | Coordinates |
| tz | text | Timezone name |
| tzoff | integer | Timezone offset |
| sunrise, sunset | integer | Unix timestamps |
| temp | real | Temperature |
| feels_like | real | "Feels like" temp |
| pressure | integer | Atmospheric pressure |
| humidity | integer | Humidity % |
| dew_point | real | Dew point |
| vis | real | Visibility |
| description | text | Weather description |
| clouds | integer | Cloud cover |
| wind_speed | real | Wind speed |
| wind_deg | integer | Wind direction |
| location_id | integer | FK to locations |

### `locations`
| Column | Type | Description |
|--------|------|-------------|
| id | integer | Primary key |
| friendly_name | text | Display name (Fincastle, Rome, etc.) |
| official_station_name | text | Weather station name |
| lat_detail | double precision | Precise latitude |
| lon_detail | double precision | Precise longitude |
| lat_rounded, lon_rounded | real | Rounded coordinates |
| zip_code | text | ZIP code |
| controlcore_location_id | text | ControlCore reference |

### Location-specific tables
- `fincastle_daily`, `rome_daily` - Same structure as `daily_summary_data`
- `fincastle_hourly`, `rome_hourly` - Same structure as `hourly_data`

---

## Important Notes

1. **Date format**: The `date` column is a **Unix timestamp** (integer seconds since epoch), not a date string
2. **Location-specific tables**: These appear to be partitioned copies; we can import either the main tables or location-specific ones
3. **Utility functions**: The export includes `celsius_to_fahrenheit()` and `extract_date()` which we can use
4. **Foreign keys**: All tables reference `locations.id`

---

## Data We Need

**Priority 1 - Weather Data:**
- `locations` - Location definitions (required first for FK references)
- `daily_summary_data` - Daily weather summaries
- `hourly_data` - Detailed hourly readings (optional, larger dataset)

**Priority 2 - Location-Specific Tables (if used):**
- `fincastle_daily`, `fincastle_hourly`
- `rome_daily`, `rome_hourly`

**Priority 3 - Future IoT Data (Phase 2+):**
- Sensor readings from ESP32/Arduino nodes
- Node configurations
- Historical action logs

---

## Import Process

Once we receive the data, we'll:

1. Import `locations` first (provides FK references)
2. Import weather tables (`daily_summary_data`, `hourly_data`)
3. Verify row counts and date ranges:
   ```sql
   SELECT COUNT(*),
          TO_TIMESTAMP(MIN(date)) as earliest,
          TO_TIMESTAMP(MAX(date)) as latest
   FROM daily_summary_data;
   ```
4. Update schema embeddings for the Text-to-SQL pipeline

---

## Quick Data Check Commands

Run these in your database to see what you have:

```sql
-- Check locations
SELECT id, friendly_name, lat_detail, lon_detail FROM locations;

-- Check date range for daily data
SELECT location_id, COUNT(*) as records,
       TO_TIMESTAMP(MIN(date)) as earliest,
       TO_TIMESTAMP(MAX(date)) as latest
FROM daily_summary_data
GROUP BY location_id;

-- Check hourly data volume
SELECT location_id, COUNT(*) as records
FROM hourly_data
GROUP BY location_id;

-- Total size estimate
SELECT pg_size_pretty(pg_total_relation_size('daily_summary_data')) as daily_size,
       pg_size_pretty(pg_total_relation_size('hourly_data')) as hourly_size;
```

---

## File Transfer Options

1. **GitHub Release** (recommended for versioned data):
   - Create a release on your repo
   - Attach the SQL dump or compressed CSVs

2. **Direct Share**:
   - For smaller exports (<50MB), email or cloud share works

3. **Compressed Transfer**:
   ```bash
   # Compress the export
   gzip controlcore_data_export.sql
   # Result: controlcore_data_export.sql.gz
   ```

---

## Questions Answered

Based on the schema dump:
- **Database:** PostgreSQL (v17.5)
- **Locations:** Fincastle, Rome (location-specific tables exist)
- **Data source:** OpenWeather API (table names confirm this)
- **Date format:** Unix timestamps (integer), not date strings
