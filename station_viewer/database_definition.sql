CREATE USER controlcore_user WITH PASSWORD '34dfRT56gh67';
GRANT CONNECT ON DATABASE controlcore TO controlcore_user;
GRANT USAGE ON SCHEMA public TO controlcore_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO controlcore_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO controlcore_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO controlcore_user;


CREATE DATABASE controlcore;

\c controlcore

-- Enable Timescale
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Controllers
CREATE TABLE controllers (
    controller_id TEXT PRIMARY KEY,
    station_id TEXT,
    last_seen TIMESTAMPTZ,
    config_source TEXT,
    startup_config_hash TEXT,
    running_config_applied BOOLEAN
);

-- Boot logs
CREATE TABLE controller_boot_log (
    controller_id TEXT,
    boot_time BIGINT,
    startup_config_hash TEXT,
    running_config_applied BOOLEAN,
    sensors_loaded JSONB,
    received_at TIMESTAMPTZ DEFAULT now()
);

-- Sensor assignments
CREATE TABLE sensor_assignments (
    controller_id TEXT,
    pin INTEGER,
    sensor_id TEXT,
    sensor_type TEXT,
    unit TEXT,
    location_hint TEXT,
    config_source TEXT,
    assigned_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (controller_id, pin)
);

-- Sensor data (Timescale)
CREATE TABLE sensor_data (
    sensor_id TEXT,
    controller_id TEXT,
    station_id TEXT,
    pin INTEGER,
    value REAL,
    unit TEXT,
    source_id TEXT,
    uptime INTEGER,
    received_at TIMESTAMPTZ DEFAULT now()
);

-- Convert to hypertable
SELECT create_hypertable('sensor_data', 'received_at');

CREATE INDEX IF NOT EXISTS idx_sensor_data_source_id ON sensor_data(source_id);





--- CONTROL MESSAGE STORAGE NOT YET IMPLEMENTED

CREATE TABLE control_log (
    id SERIAL PRIMARY KEY,
    station TEXT NOT NULL,
    controller_id TEXT NOT NULL,
    sensor_id TEXT,
    sensor_type TEXT,
    command TEXT NOT NULL,
    value REAL,
    unit TEXT,
    source TEXT, -- e.g., "manual_override", "automated_policy", "dashboard_click"
    requestor_id TEXT, -- e.g., user or process name
    received_at TIMESTAMPTZ DEFAULT now()
);


