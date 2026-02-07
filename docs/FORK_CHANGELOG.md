# Fork Changelog - LiteLLM Integration

**Forked from:** [excessus1/controlcore_pub](https://github.com/excessus1/controlcore_pub)
**Fork:** [mgerasolo/controlcore_pub](https://github.com/mgerasolo/controlcore_pub)
**Date:** February 6, 2026

---

## Overview

This fork integrates ControlCore with LiteLLM for model-agnostic LLM access and adds Open WebUI as a chat frontend. The system is deployed and functional, currently with limited weather data for testing.

---

## New Files Added

### API Layer
| File | Purpose |
|------|---------|
| `gandalf_api/sql_query_handler_litellm.py` | Replaces direct Ollama calls with LiteLLM OpenAI-compatible API |
| `sauron_api/main_standalone.py` | Simplified orchestration API with vector search + OpenAI-compatible endpoints |

### Deployment
| File | Purpose |
|------|---------|
| `docker-compose.openwebui.yml` | Full stack: Open WebUI + Sauron + Gandalf + PostgreSQL |
| `docker-compose.apis.yml` | APIs only (when DB runs separately) |
| `Dockerfile.gandalf` | Python container for Gandalf API |
| `Dockerfile.sauron` | Python container with sentence-transformers |

### Scripts
| File | Purpose |
|------|---------|
| `scripts/load_schema_embeddings_litellm.py` | Load schema embeddings via LiteLLM |
| `scripts/load_schema_embeddings_local.py` | Load embeddings using local sentence-transformers |
| `scripts/fetch_openweather_ytd.py` | Fetch YTD historical data from OpenWeather API |

---

## Architecture Changes

### LLM Integration
- **Before:** Direct Ollama API calls
- **After:** LiteLLM proxy (OpenAI-compatible API)
- **Benefit:** Model-agnostic, can swap SQLCoder/Llama/GPT without code changes

### Prompt Engineering
- Uses SQLCoder-specific prompt format:
  ```
  ### Task
  Generate a SQL query to answer [QUESTION]...[/QUESTION]
  ### Database Schema
  ...
  ### Answer
  [SQL]
  ```

### Embedding Model
- **Before:** nomic-embed-text via API
- **After:** all-mpnet-base-v2 (768 dims) loaded locally
- **Benefit:** No API call for embeddings, faster response

### OpenAI-Compatible Endpoints
Added to Sauron API:
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat endpoint

This enables Open WebUI integration or any OpenAI-compatible client.

---

## New Features

### Query Metadata in Responses
Every response now includes:
- **Location:** Extracted from SQL query
- **Date Range Requested:** What the user asked for
- **Data Available:** Actual date range in database

Example output:
```
The total precipitation in Fincastle for 2026 was 0.57 inches.

---
**Location:** Fincastle | **Date Range Requested:** Year 2026 | **Data Available:** 2026-01-15 to 2026-01-20 (6 records)
```

### Smart Missing Data Detection
When no data is found:
1. Acknowledges the missing data
2. Offers to fetch from OpenWeather API
3. Suggests alternative queries (different dates/locations)

---

## Environment Variables

```bash
# LiteLLM configuration
LITELLM_API_URL=http://your-litellm-host:port/v1
LITELLM_API_KEY=your-key
LITELLM_SQL_MODEL=your-sqlcoder-model
LITELLM_SUMMARY_MODEL=your-summary-model

# Database
PG_HOST=your-db-host
PG_PORT=5432
PG_USER=forecaster
PG_PASSWORD=your-password
```

---

## Deployment Ports

| Service | Port | Purpose |
|---------|------|---------|
| Open WebUI | 3351 | Chat frontend |
| Sauron API | 3352 | Orchestration + OpenAI-compat |
| PostgreSQL | 3353 | Database + pgvector |
| Gandalf API | 3354 | SQL generation + summarization |

---

## Database Schema Additions

```sql
-- For pgvector embeddings (768 dimensions)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE schema_embeddings (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    column_name TEXT,
    content TEXT NOT NULL,
    embedding vector(768) NOT NULL
);

CREATE INDEX ON schema_embeddings
  USING ivfflat (embedding vector_cosine_ops);
```

---

## Known Limitations

1. **Location Map:** Hardcoded `{1: Fincastle, 2: Rome, 3: Roanoke}` in `extract_location_from_sql()` - should query DB dynamically
2. **Cold Start:** Embedding model downloads on first container start (~30s delay)
3. **OpenWeather Script:** Ready but requires One Call API 3.0 subscription

---

## How to Use This Fork

```bash
# Clone the fork
git clone git@github.com:mgerasolo/controlcore_pub.git
cd controlcore_pub

# Copy and configure environment
cp .env.example .env
# Edit .env with your LiteLLM and database credentials

# Deploy with Docker Compose
docker compose -f docker-compose.openwebui.yml up -d

# Load schema embeddings
python scripts/load_schema_embeddings_local.py
```

---

## Pulling Updates from Upstream

```bash
# Add upstream remote (original repo)
git remote add upstream git@github.com:excessus1/controlcore_pub.git

# Fetch and merge
git fetch upstream
git merge upstream/main
```

---

## Phase 2: Command & Control Layer

**Date:** February 6, 2026

### New Files Added

#### IoT Control Layer
| File | Purpose |
|------|---------|
| `sauron_api/mqtt_service.py` | MQTT client for IoT node communication |
| `sauron_api/command_parser.py` | Natural language → structured command parser |
| `sauron_api/safety_engine.py` | Safety rule engine with critical built-in rules |
| `mosquitto.conf` | MQTT broker configuration |
| `database_schemas/node_registry.sql` | Node registry, capabilities, sensor readings, action log tables |
| `docs/DATA_IMPORT_SPEC.md` | Data import specification with Kevin's exact PostgreSQL schema |

### MQTT Architecture
```
User → Sauron (MQTT Client) → Mosquitto (Broker) → SA Nodes (ESP32/Arduino)
                                    ↓
                          PostgreSQL (action_log, sensor_readings)
```

### Command Parser
- Pattern-based parsing for common commands (instant, no API)
- LLM fallback for complex/ambiguous commands
- Confidence threshold (0.7) triggers LLM fallback
- Supports: ON/OFF, SET value, timed actions, schedules, E-stop

### Safety Engine
Built-in critical rules (cannot be disabled):
1. **No watering during freeze** - Blocks irrigation when frost_warning=true
2. **Max 60 min single watering** - Adjusts duration if exceeded
3. **Max 180 min daily watering** - Blocks when daily limit reached
4. **Temperature limits** - 40-90°F enforced
5. **No irrigation during high wind** - Blocks sprinkler operations

Safety decisions: APPROVED, DENIED, MODIFIED, REQUIRES_CONFIRMATION

### Action Audit Logging
All AI-initiated actions logged with:
- Original user request
- Parsed action and parameters
- Safety check result and reasoning
- Execution status (pending → sent → confirmed/failed)
- Timestamp and initiator

### Environment Variables Added
```bash
# MQTT configuration
MQTT_HOST=mqtt
MQTT_PORT=1883
MQTT_TOPIC=controlcore/#
```

### Deployment Changes
- Added Mosquitto container to docker-compose.openwebui.yml
- Ports: 1883 (MQTT), 9001 (WebSocket)
- Persistent storage for messages and logs

---

## Questions or Feedback

Feel free to open an issue or reach out if you have questions about these changes!
