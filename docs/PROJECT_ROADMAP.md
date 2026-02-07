# ControlCore Project Roadmap

**Vision:** Local-first AI control system for IoT sensing and action nodes with optional internet connectivity.

---

## Phase 1: Data Query Foundation ✅ COMPLETE

**Goal:** Prove LLM integration works for natural language data queries.

**Delivered:**
- Text-to-SQL pipeline (User question → SQL → Results → Natural language answer)
- LiteLLM integration for model-agnostic LLM access
- Vector similarity search for schema context (pgvector)
- OpenAI-compatible API endpoints
- Open WebUI chat frontend
- Query metadata (location, date range requested vs available)
- Smart missing data detection with helpful suggestions
- Docker deployment configs

**Architecture:**
```
User → Open WebUI → Sauron API → Gandalf API → LiteLLM
                        ↓
              PostgreSQL + pgvector
```

**Limitations:**
- Read-only (queries data, doesn't execute commands)
- Requires network access to LiteLLM
- No MQTT/IoT integration
- No safety rule checking
- No action logging or learning

---

## Phase 2: Command & Control Layer

**Goal:** Enable natural language commands to IoT nodes with safety validation.

**Core Components:**

### 2.1 MQTT Integration
```
Central Node (Sauron)
    ├── MQTT Client (paho-mqtt)
    ├── Subscribe: controlcore/+/status
    ├── Subscribe: controlcore/+/sensor/#
    └── Publish: controlcore/+/command
```

### 2.2 Node Registry
```sql
CREATE TABLE nodes (
    uuid UUID PRIMARY KEY,
    friendly_name TEXT NOT NULL,
    node_type TEXT,  -- 'sensor', 'actuator', 'hybrid'
    last_seen TIMESTAMP,
    status TEXT,     -- 'online', 'offline', 'error'
    battery_voltage FLOAT,
    metadata JSONB
);

CREATE TABLE node_capabilities (
    id SERIAL PRIMARY KEY,
    node_uuid UUID REFERENCES nodes(uuid),
    capability_type TEXT,  -- 'sensor', 'action'
    name TEXT,             -- 'temperature', 'valve_control'
    unit TEXT,             -- '°F', 'on/off'
    description TEXT,
    constraints JSONB      -- min/max values, allowed states
);
```

### 2.3 Command Parser
Transform natural language to structured commands:
```
Input:  "Turn on the Potato Patch watering till the water detector is wet for 10 minutes"
Output: {
    "target_node": "potato-patch-valve-01",
    "action": "valve_on",
    "condition": {
        "sensor": "potato-patch-moisture-01",
        "state": "wet",
        "duration_minutes": 10
    }
}
```

### 2.4 Safety Rule Engine
```python
class SafetyValidator:
    def validate_command(self, command: Command) -> ValidationResult:
        # Check against static rules
        # Check against node constraints
        # Check against user-defined limits
        # Return: ALLOW, DENY, or REQUIRE_CONFIRMATION
```

### 2.5 Action Audit Log
```sql
CREATE TABLE action_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    initiated_by TEXT,        -- 'user', 'ai', 'schedule', 'rule'
    node_uuid UUID,
    action TEXT,
    parameters JSONB,
    ai_reasoning TEXT,        -- Why AI chose this action
    safety_check_result TEXT,
    execution_result TEXT,
    user_prompt TEXT          -- Original user request if applicable
);
```

---

## Phase 3: Offline-First & Fallback

**Goal:** System operates autonomously without internet, fails safely.

### 3.1 Local LLM Fallback
```
Priority:
1. LiteLLM (remote) - Full capability
2. Local Ollama (on Central Node) - Reduced model
3. Static rule engine - No AI, safe defaults only
```

### 3.2 Static Fallback Rules
```yaml
# fallback_rules.yaml
potato_patch:
  conditions:
    - if: soil_moisture < 30%
      action: valve_on
      duration: 15min
      max_daily: 3
    - if: temperature > 95F AND soil_moisture < 50%
      action: valve_on
      duration: 10min
  safety:
    - never: valve_on when frost_warning
    - max: water_usage_daily < 500gal
```

### 3.3 Offline Mode Detection
```python
class ConnectivityMonitor:
    def check_status(self) -> ConnectivityStatus:
        return {
            "internet": self.ping_external(),
            "litellm": self.ping_litellm(),
            "mqtt_broker": self.ping_mqtt(),
            "mode": "full" | "local_ai" | "fallback"
        }
```

### 3.4 E-Stop / Panic Messaging
```
MQTT Topic: controlcore/emergency/stop
Payload: {"level": "all" | "zone" | "node", "target": "...", "reason": "..."}

All nodes subscribe and immediately:
1. Stop current actions
2. Enter safe state
3. Report status
4. Await manual reset
```

---

## Phase 4: Learning & Adaptation

**Goal:** System learns patterns and user preferences over time.

### 4.1 Context Learning
```sql
CREATE TABLE learned_contexts (
    id SERIAL PRIMARY KEY,
    term TEXT,              -- "hot day"
    context JSONB,          -- {"temperature_min": 85, "humidity_max": 60}
    source TEXT,            -- 'user_defined', 'inferred', 'external'
    confidence FLOAT,
    created_at TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INT
);
```

Example:
```
User says: "It's a hot day, water the potatoes extra"
System learns:
  - "hot day" → temperature > 85°F
  - "potatoes need extra water when hot" → increase duration 50%
```

### 4.2 User Preference Tracking
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    preference_type TEXT,   -- 'watering_schedule', 'notification_level'
    value JSONB,
    learned_from TEXT,      -- 'explicit', 'behavior'
    confidence FLOAT
);
```

### 4.3 Outcome Feedback Loop
```sql
CREATE TABLE action_outcomes (
    id SERIAL PRIMARY KEY,
    action_log_id INT REFERENCES action_log(id),
    outcome TEXT,           -- 'success', 'partial', 'failed'
    sensor_readings JSONB,  -- Before/after measurements
    user_feedback TEXT,     -- 'good', 'too_much', 'not_enough'
    timestamp TIMESTAMP
);
```

### 4.4 Knowledge Base Loading
```python
class KnowledgeManager:
    def load_domain_knowledge(self, domain: str):
        # Load curated knowledge for equipment type
        # e.g., "drip_irrigation", "greenhouse", "hydroponics"

    def load_user_rules(self, user_id: str):
        # Load user's custom rules and preferences
```

---

## Architecture Evolution

### Phase 1 (Current)
```
[Open WebUI] → [Sauron] → [Gandalf] → [LiteLLM]
                  ↓
            [PostgreSQL]
```

### Phase 2-4 (Target)
```
[Web UI] ←→ [Central Node (Sauron)]
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
[MQTT Broker] [PostgreSQL]    [LiteLLM/Local Ollama]
    ↓
┌───┴───┬───────┬───────┐
↓       ↓       ↓       ↓
[SA Node 1] [SA Node 2] [SA Node 3] ...
(ESP32)     (Arduino)   (ESP32)
```

---

## Key Principles (from Kevin)

1. **Local-first:** Central node must work offline
2. **Fail-safe:** Static rules when AI unavailable
3. **Auditable:** All AI decisions logged with reasoning
4. **User-customizable:** Nodes, sensors, actions defined by user
5. **Low-power friendly:** MQTT, battery-aware messaging
6. **Security-aware:** Fingerprinted nodes, no robust encryption assumed
7. **Low daily cost:** Minimize cloud/API dependencies

---

## Next Steps

**Immediate (Phase 2 foundation):**
1. Add MQTT client to Sauron
2. Create node registry tables
3. Implement basic command parser
4. Add action audit logging

**Medium-term:**
5. Safety rule engine
6. Offline detection and fallback
7. E-stop messaging

**Long-term:**
8. Learning and adaptation
9. Domain knowledge loading
10. Outcome feedback integration
