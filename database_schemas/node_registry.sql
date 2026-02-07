-- Node Registry Schema for ControlCore Phase 2
-- Manages IoT sensing/action nodes and their capabilities

-- Nodes table: Tracks all registered SA (Sensing/Action) nodes
CREATE TABLE IF NOT EXISTS nodes (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    friendly_name TEXT NOT NULL,
    node_type TEXT NOT NULL CHECK (node_type IN ('sensor', 'actuator', 'hybrid')),
    description TEXT,
    location TEXT,
    status TEXT DEFAULT 'unknown' CHECK (status IN ('online', 'offline', 'error', 'unknown')),
    last_seen TIMESTAMP WITH TIME ZONE,
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    battery_voltage FLOAT,
    firmware_version TEXT,
    hardware_type TEXT,  -- 'esp32', 'arduino', 'raspberry_pi', etc.
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Node capabilities: What each node can sense or do
CREATE TABLE IF NOT EXISTS node_capabilities (
    id SERIAL PRIMARY KEY,
    node_uuid UUID NOT NULL REFERENCES nodes(uuid) ON DELETE CASCADE,
    capability_type TEXT NOT NULL CHECK (capability_type IN ('sensor', 'action')),
    name TEXT NOT NULL,              -- 'temperature', 'valve_control', 'moisture'
    display_name TEXT,               -- 'Soil Temperature', 'Main Valve'
    unit TEXT,                       -- '°F', 'on/off', '%'
    data_type TEXT DEFAULT 'float',  -- 'float', 'int', 'bool', 'string', 'enum'
    constraints JSONB DEFAULT '{}',  -- {"min": 0, "max": 100, "allowed": ["on", "off"]}
    description TEXT,
    mqtt_topic TEXT,                 -- Specific topic for this capability
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(node_uuid, capability_type, name)
);

-- Sensor readings: Historical data from sensors
CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    node_uuid UUID NOT NULL REFERENCES nodes(uuid) ON DELETE CASCADE,
    capability_name TEXT NOT NULL,
    value JSONB NOT NULL,            -- Flexible: {"temperature": 72.5} or {"state": "on"}
    raw_value TEXT,                  -- Original value from MQTT
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    quality TEXT DEFAULT 'good'      -- 'good', 'suspect', 'bad'
);

-- Action log: All commands sent to nodes (AI decisions must be recorded)
CREATE TABLE IF NOT EXISTS action_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    initiated_by TEXT NOT NULL,      -- 'user', 'ai', 'schedule', 'rule', 'fallback'
    initiator_id TEXT,               -- User ID, rule name, etc.
    node_uuid UUID REFERENCES nodes(uuid),
    capability_name TEXT,
    action TEXT NOT NULL,            -- 'valve_on', 'set_temperature', etc.
    parameters JSONB DEFAULT '{}',   -- {"duration_minutes": 10, "target_value": 72}
    original_request TEXT,           -- Original user prompt if applicable
    ai_reasoning TEXT,               -- Why AI chose this action
    safety_check_result TEXT,        -- 'approved', 'denied', 'modified'
    safety_notes TEXT,               -- Why safety check passed/failed
    execution_status TEXT DEFAULT 'pending',  -- 'pending', 'sent', 'confirmed', 'failed'
    execution_result JSONB,          -- Response from node
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Safety rules: Constraints that must be checked before actions
CREATE TABLE IF NOT EXISTS safety_rules (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    rule_type TEXT NOT NULL,         -- 'never', 'always', 'limit', 'require'
    priority INT DEFAULT 100,        -- Lower = higher priority
    enabled BOOLEAN DEFAULT true,
    conditions JSONB NOT NULL,       -- {"sensor": "frost_warning", "value": true}
    action_constraint JSONB NOT NULL, -- {"action": "valve_on", "result": "deny"}
    applies_to JSONB,                -- {"nodes": ["*"], "capabilities": ["valve_*"]}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learned contexts: System learns patterns over time
CREATE TABLE IF NOT EXISTS learned_contexts (
    id SERIAL PRIMARY KEY,
    term TEXT NOT NULL,              -- "hot day", "dry conditions"
    context JSONB NOT NULL,          -- {"temperature_min": 85, "humidity_max": 60}
    source TEXT NOT NULL,            -- 'user_defined', 'inferred', 'external'
    confidence FLOAT DEFAULT 0.5,
    usage_count INT DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fallback rules: Static rules when AI/internet unavailable
CREATE TABLE IF NOT EXISTS fallback_rules (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    priority INT DEFAULT 100,
    enabled BOOLEAN DEFAULT true,
    conditions JSONB NOT NULL,       -- {"sensor": "soil_moisture", "operator": "<", "value": 30}
    actions JSONB NOT NULL,          -- [{"node": "valve-01", "action": "on", "duration": 15}]
    constraints JSONB,               -- {"max_daily_activations": 3}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status);
CREATE INDEX IF NOT EXISTS idx_nodes_last_seen ON nodes(last_seen);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_node ON sensor_readings(node_uuid, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_time ON sensor_readings(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_action_log_node ON action_log(node_uuid, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_action_log_time ON action_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_action_log_initiated ON action_log(initiated_by, timestamp DESC);

-- Trigger to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_nodes_updated_at
    BEFORE UPDATE ON nodes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_safety_rules_updated_at
    BEFORE UPDATE ON safety_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER update_learned_contexts_updated_at
    BEFORE UPDATE ON learned_contexts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
