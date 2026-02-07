"""
Sauron API - Simplified standalone version for Middle Earth Forecaster

Orchestrates the Text-to-SQL pipeline:
1. Receive user question
2. Parse intent (query vs action vs control)
3. For queries: Generate SQL, execute, summarize
4. For actions: Route to MQTT and execute on IoT nodes
5. Return natural language response
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import psycopg2
import httpx
import json
import datetime
import logging
import re
from typing import Optional
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector

# Local imports
from .command_parser import CommandParser, IntentType, ActionType, ParsedCommand, create_command_parser
from .mqtt_service import MQTTService, MQTTConfig, create_mqtt_service
from .safety_engine import SafetyEngine, SafetyDecision, SafetyContext, create_safety_engine

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Sauron API - Middle Earth Forecaster")

# Add CORS for Open WebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PG_HOST = os.getenv("PG_HOST", "10.0.0.33")
PG_PORT = os.getenv("PG_PORT", "3353")
PG_USER = os.getenv("PG_USER", "forecaster")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DATABASE = "forecaster"

GANDALF_SQL_URL = os.getenv("GANDALF_SQL_URL", "http://10.0.0.33:3354/generate-sql")
GANDALF_ANALYZE_URL = os.getenv("GANDALF_ANALYZE_URL", "http://10.0.0.33:3354/analyze")
GANDALF_REPHRASE_URL = os.getenv("GANDALF_REPHRASE_URL", "http://10.0.0.33:3354/rephrase")

# Schema embedding model (same as ControlCore)
SCHEMA_MODEL_NAME = "all-mpnet-base-v2"
_schema_model = None

# Command parser, MQTT service, and safety engine (lazy-loaded)
_command_parser: Optional[CommandParser] = None
_mqtt_service: Optional[MQTTService] = None
_safety_engine: Optional[SafetyEngine] = None


def get_command_parser() -> CommandParser:
    """Lazy-load the command parser."""
    global _command_parser
    if _command_parser is None:
        logger.info("Initializing command parser...")
        _command_parser = create_command_parser(use_llm=True)
    return _command_parser


def get_mqtt_service() -> Optional[MQTTService]:
    """Lazy-load the MQTT service."""
    global _mqtt_service
    if _mqtt_service is None:
        mqtt_host = os.getenv("MQTT_HOST")
        if mqtt_host:
            logger.info(f"Initializing MQTT service to {mqtt_host}...")
            _mqtt_service = create_mqtt_service()
            _mqtt_service.connect()
        else:
            logger.warning("MQTT_HOST not set, MQTT service disabled")
    return _mqtt_service


def get_safety_engine() -> SafetyEngine:
    """Lazy-load the safety engine."""
    global _safety_engine
    if _safety_engine is None:
        logger.info("Initializing safety engine...")
        _safety_engine = create_safety_engine()
    return _safety_engine


class ChatRequest(BaseModel):
    question: str


class QueryMetadata(BaseModel):
    location: str | None = None
    date_range_requested: str | None = None
    date_range_with_data: str | None = None


class ChatResponse(BaseModel):
    summary: str
    sql: str | None = None
    row_count: int | None = None
    metadata: QueryMetadata | None = None


# OpenAI-compatible models for Open WebUI
class OpenAIMessage(BaseModel):
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    model: str = "forecaster"
    messages: list[OpenAIMessage]
    stream: bool = False


class OpenAIChatChoice(BaseModel):
    index: int
    message: OpenAIMessage
    finish_reason: str = "stop"


class OpenAIChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str = "forecaster"
    choices: list[OpenAIChatChoice]


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE
    )


def get_schema_model():
    """Lazy-load the embedding model."""
    global _schema_model
    if _schema_model is None:
        logger.info(f"Loading embedding model: {SCHEMA_MODEL_NAME}")
        _schema_model = SentenceTransformer(SCHEMA_MODEL_NAME)
    return _schema_model


def retrieve_schema_context(question: str, top_n: int = 5) -> list[dict]:
    """Find relevant schema elements via vector similarity search."""
    model = get_schema_model()
    vector = model.encode(question).tolist()

    conn = get_db_connection()
    register_vector(conn)

    with conn.cursor() as cur:
        cur.execute(
            """SELECT table_name, column_name, content
               FROM schema_embeddings
               ORDER BY embedding <-> %s::vector
               LIMIT %s""",
            (vector, top_n),
        )
        rows = cur.fetchall()

    conn.close()

    return [
        {"table": t, "column": c, "description": d}
        for t, c, d in rows
    ]


def get_table_schema() -> str:
    """Get DDL-style schema for SQLCoder."""
    conn = get_db_connection()

    with conn.cursor() as cur:
        # Get table definitions
        cur.execute("""
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name IN ('locations', 'daily_summary_data', 'hourly_data')
            ORDER BY table_name, ordinal_position
        """)
        columns = cur.fetchall()

    conn.close()

    # Build DDL-style schema
    tables = {}
    for table, column, dtype, nullable in columns:
        if table not in tables:
            tables[table] = []
        null_str = "" if nullable == "YES" else " NOT NULL"
        tables[table].append(f"  {column} {dtype.upper()}{null_str}")

    schema_parts = []
    for table, cols in tables.items():
        schema_parts.append(f"CREATE TABLE {table} (\n" + ",\n".join(cols) + "\n);")

    return "\n\n".join(schema_parts)


def extract_location_from_sql(sql: str) -> str | None:
    """Extract location name from SQL query."""
    # Look for location_id = N pattern
    loc_id_match = re.search(r"location_id\s*=\s*(\d+)", sql, re.IGNORECASE)
    if loc_id_match:
        loc_id = int(loc_id_match.group(1))
        loc_map = {1: "Fincastle", 2: "Rome", 3: "Roanoke"}
        return loc_map.get(loc_id)

    # Look for location name in WHERE clause
    name_match = re.search(r"name\s*=\s*['\"](\w+)['\"]", sql, re.IGNORECASE)
    if name_match:
        return name_match.group(1)

    # Look for location name in LIKE clause
    like_match = re.search(r"name\s+(?:I?LIKE)\s*['\"]%?(\w+)%?['\"]", sql, re.IGNORECASE)
    if like_match:
        return like_match.group(1)

    return None


def extract_date_range_from_sql(sql: str) -> str | None:
    """Extract date range from SQL query."""
    # Look for BETWEEN dates
    between_match = re.search(
        r"(?:date|created_at)\s+BETWEEN\s+['\"]?(\d{4}-\d{2}-\d{2})['\"]?\s+AND\s+['\"]?(\d{4}-\d{2}-\d{2})['\"]?",
        sql, re.IGNORECASE
    )
    if between_match:
        return f"{between_match.group(1)} to {between_match.group(2)}"

    # Look for >= and <= date patterns
    gte_match = re.search(r"(?:date|created_at)\s*>=\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?", sql, re.IGNORECASE)
    lte_match = re.search(r"(?:date|created_at)\s*<=\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?", sql, re.IGNORECASE)
    if gte_match and lte_match:
        return f"{gte_match.group(1)} to {lte_match.group(1)}"
    elif gte_match:
        return f"from {gte_match.group(1)}"
    elif lte_match:
        return f"through {lte_match.group(1)}"

    # Look for single date = condition
    eq_match = re.search(r"(?:date|created_at)\s*=\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?", sql, re.IGNORECASE)
    if eq_match:
        return eq_match.group(1)

    # Look for year extraction (handles table.column patterns)
    year_match = re.search(r"EXTRACT\s*\(\s*YEAR\s+FROM\s+[\w.]+\s*\)\s*=\s*(\d{4})", sql, re.IGNORECASE)
    if year_match:
        return f"Year {year_match.group(1)}"

    # Look for date_trunc patterns
    trunc_match = re.search(r"date_trunc\s*\(\s*['\"]year['\"]\s*,\s*[\w.]+\s*\)\s*=\s*['\"]?(\d{4})", sql, re.IGNORECASE)
    if trunc_match:
        return f"Year {trunc_match.group(1)}"

    return None


def get_actual_data_range(location_name: str | None) -> str | None:
    """Query database for actual date range with data."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if location_name:
                cur.execute("""
                    SELECT MIN(d.date), MAX(d.date), COUNT(*)
                    FROM daily_summary_data d
                    JOIN locations l ON d.location_id = l.id
                    WHERE LOWER(l.name) = LOWER(%s)
                """, (location_name,))
            else:
                cur.execute("""
                    SELECT MIN(date), MAX(date), COUNT(*)
                    FROM daily_summary_data
                """)
            result = cur.fetchone()
            if result and result[0] and result[1]:
                min_date, max_date, count = result
                return f"{min_date} to {max_date} ({count} records)"
    except Exception as e:
        logger.warning(f"Error getting data range: {e}")
    finally:
        conn.close()
    return None


def clean_sql(sql: str) -> str:
    """Clean up SQL response."""
    text = sql.strip()

    # Remove markdown fencing
    if text.startswith("```sql"):
        text = text[6:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    # Find SELECT or WITH statement
    match = re.search(r"(?is)(SELECT|WITH)\b", text)
    if match:
        text = text[match.start():]

    return text.strip()


def safe_serialize(obj):
    """Serialize objects for JSON."""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    return str(obj)


def execute_sql(sql: str) -> list[dict]:
    """Execute SQL and return results as list of dicts."""
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    finally:
        conn.close()


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "service": "sauron"}


async def handle_action_command(parsed: ParsedCommand) -> ChatResponse:
    """Handle action commands (controlling devices)."""
    mqtt = get_mqtt_service()
    safety = get_safety_engine()

    if not mqtt or not mqtt.connected:
        return ChatResponse(
            summary="Cannot execute action: MQTT service is not connected. IoT control is currently unavailable.",
            sql=None,
            row_count=None,
            metadata=None
        )

    # Resolve target node
    target = parsed.target_node
    if not target:
        return ChatResponse(
            summary="I couldn't determine which device you want to control. Please specify a device name.",
            sql=None,
            row_count=None,
            metadata=None
        )

    # Build action command
    action = f"{parsed.capability}_{parsed.action_type.value}" if parsed.capability else parsed.action_type.value
    params = parsed.parameters.copy()

    # SAFETY CHECK - All AI actions must pass safety rules
    safety_result = safety.check_action(
        action=action,
        parameters=params,
        initiated_by="ai"
    )

    # Handle safety decision
    if safety_result.decision == SafetyDecision.DENIED:
        logger.warning(f"Action DENIED by safety: {safety_result.reason}")
        return ChatResponse(
            summary=f"Action blocked by safety rule: {safety_result.reason}\n\n"
                   f"Rule: {safety_result.rule_name}",
            sql=None,
            row_count=None,
            metadata=QueryMetadata(location=target)
        )

    if safety_result.decision == SafetyDecision.REQUIRES_CONFIRMATION:
        return ChatResponse(
            summary=f"This action requires human confirmation: {safety_result.reason}\n\n"
                   f"Please confirm you want to proceed with: {action} on {target}",
            sql=None,
            row_count=None,
            metadata=QueryMetadata(location=target)
        )

    # Apply modifications if safety engine adjusted parameters
    if safety_result.decision == SafetyDecision.MODIFIED and safety_result.modified_params:
        logger.info(f"Action modified by safety: {params} -> {safety_result.modified_params}")
        params = safety_result.modified_params

    # Log the action (will be stored in action_log table)
    conn = get_db_connection()
    action_id = None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO action_log
                (initiated_by, initiator_id, action, parameters, original_request,
                 safety_check_result, safety_notes, execution_status)
                VALUES ('ai', 'sauron', %s, %s, %s, %s, %s, 'pending')
                RETURNING id
            """, (action, json.dumps(params), parsed.original_text,
                  safety_result.decision.value, safety_result.reason))
            action_id = cur.fetchone()[0]
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to log action: {e}")
        conn.rollback()
    finally:
        conn.close()

    # Send command via MQTT
    node_uuid = mqtt.get_node_status(target)
    if not node_uuid:
        # Try by friendly name
        node_uuid = target  # For now, use target as-is

    success = mqtt.send_command(
        node_uuid=node_uuid if isinstance(node_uuid, str) else target,
        action=action,
        parameters=params,
        action_id=action_id
    )

    if success:
        # Build response
        action_desc = f"{'turning on' if parsed.action_type == ActionType.ON else 'turning off'}" if parsed.action_type in (ActionType.ON, ActionType.OFF) else f"setting"
        duration_msg = f" for {params.get('duration_minutes')} minutes" if 'duration_minutes' in params else ""
        value_msg = f" to {params.get('value')}" if 'value' in params else ""

        summary = f"Command sent: {action_desc} {target}{value_msg}{duration_msg}. Waiting for node confirmation."

        # Add safety modification note if applicable
        if safety_result.decision == SafetyDecision.MODIFIED:
            summary += f"\n\n*Note: Parameters adjusted by safety rule - {safety_result.reason}*"
    else:
        summary = f"Failed to send command to {target}. The node may be offline."

    return ChatResponse(
        summary=summary,
        sql=None,
        row_count=None,
        metadata=QueryMetadata(location=target)
    )


async def handle_control_command(parsed: ParsedCommand) -> ChatResponse:
    """Handle control commands (system-level operations)."""
    mqtt = get_mqtt_service()

    if parsed.control_type == "e_stop":
        if mqtt and mqtt.connected:
            mqtt.send_emergency_stop(
                level=parsed.scope or "all",
                reason=parsed.original_text
            )
            return ChatResponse(
                summary="EMERGENCY STOP activated! All nodes have been commanded to halt operations.",
                sql=None,
                row_count=None,
                metadata=None
            )
        else:
            return ChatResponse(
                summary="EMERGENCY STOP requested but MQTT is not connected. Manual intervention may be required!",
                sql=None,
                row_count=None,
                metadata=None
            )

    elif parsed.control_type == "list_nodes":
        if mqtt:
            nodes = mqtt.get_all_nodes()
            if nodes:
                node_list = "\n".join([f"- {n['friendly_name']} ({n['status']})" for n in nodes])
                return ChatResponse(
                    summary=f"Registered nodes:\n{node_list}",
                    sql=None,
                    row_count=len(nodes),
                    metadata=None
                )
            else:
                return ChatResponse(
                    summary="No nodes are currently registered in the system.",
                    sql=None,
                    row_count=0,
                    metadata=None
                )
        return ChatResponse(
            summary="Node listing unavailable: MQTT service not connected.",
            sql=None,
            row_count=None,
            metadata=None
        )

    elif parsed.control_type == "status":
        if mqtt and parsed.target_node:
            status = mqtt.get_node_status(parsed.target_node)
            if status:
                return ChatResponse(
                    summary=f"Node {status['friendly_name']}: {status['status']}\n"
                           f"Last seen: {status.get('last_seen', 'unknown')}\n"
                           f"Battery: {status.get('battery_voltage', 'N/A')}V\n"
                           f"Firmware: {status.get('firmware_version', 'unknown')}",
                    sql=None,
                    row_count=None,
                    metadata=None
                )
        return ChatResponse(
            summary=f"Could not find status for node: {parsed.target_node}",
            sql=None,
            row_count=None,
            metadata=None
        )

    return ChatResponse(
        summary=f"Control command '{parsed.control_type}' acknowledged but not yet implemented.",
        sql=None,
        row_count=None,
        metadata=None
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main chat endpoint - orchestrates the Text-to-SQL pipeline."""

    logger.info(f"Question: {req.question}")

    # Step 0: Parse intent to determine routing
    parser = get_command_parser()
    parsed = parser.parse(req.question)

    logger.info(f"Parsed intent: {parsed.intent.value} (confidence: {parsed.confidence:.2f})")

    # Route based on intent
    if parsed.intent == IntentType.ACTION and parsed.confidence >= 0.7:
        return await handle_action_command(parsed)

    if parsed.intent == IntentType.CONTROL and parsed.confidence >= 0.7:
        return await handle_control_command(parsed)

    # Default: treat as query (weather/data question)

    # Step 1: Get schema context via vector search
    context = retrieve_schema_context(req.question)
    logger.info(f"Schema hints: {[h.get('table') for h in context]}")

    # Step 2: Get table schema
    schema = get_table_schema()

    # Step 3: Call Gandalf to generate SQL
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Optional: rephrase the question first
            # rep_resp = await client.post(GANDALF_REPHRASE_URL, json={"text": req.question})
            # clean_q = rep_resp.json().get("text", req.question)

            gen_resp = await client.post(
                GANDALF_SQL_URL,
                json={"question": req.question, "schema": schema, "context": context}
            )
            gen_resp.raise_for_status()
            sql = gen_resp.json().get("sql")

        except httpx.HTTPError as e:
            logger.error(f"Gandalf error: {e}")
            raise HTTPException(status_code=500, detail=f"Gandalf API error: {e}")

    if not sql:
        raise HTTPException(status_code=500, detail="Gandalf did not return SQL")

    sql = clean_sql(sql)
    logger.info(f"Generated SQL: {sql}")

    # Extract metadata from SQL
    location = extract_location_from_sql(sql)
    date_range_requested = extract_date_range_from_sql(sql)
    date_range_with_data = get_actual_data_range(location)

    logger.info(f"Metadata - Location: {location}, Requested: {date_range_requested}, Available: {date_range_with_data}")

    # Step 4: Execute the SQL
    try:
        rows = execute_sql(sql)
        logger.info(f"Query returned {len(rows)} rows")
    except Exception as e:
        logger.error(f"SQL execution error: {e}")
        raise HTTPException(status_code=500, detail=f"SQL error: {e}")

    # Step 5: Call Gandalf to summarize results
    safe_rows = [{k: safe_serialize(v) for k, v in row.items()} for row in rows]

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            analyze_resp = await client.post(
                GANDALF_ANALYZE_URL,
                json={"question": req.question, "sql": sql, "rows": safe_rows}
            )
            analyze_resp.raise_for_status()
            summary = analyze_resp.json().get("summary", "No summary available.")

        except httpx.HTTPError as e:
            logger.error(f"Gandalf analyze error: {e}")
            summary = f"Query executed successfully. Returned {len(rows)} rows."

    return ChatResponse(
        summary=summary,
        sql=sql,
        row_count=len(rows),
        metadata=QueryMetadata(
            location=location,
            date_range_requested=date_range_requested,
            date_range_with_data=date_range_with_data
        )
    )


# ============ OpenAI-compatible endpoints for Open WebUI ============

@app.get("/v1/models")
async def list_models():
    """OpenAI-compatible model listing."""
    return {
        "object": "list",
        "data": [
            {
                "id": "forecaster",
                "object": "model",
                "created": 1704067200,
                "owned_by": "middle-earth"
            }
        ]
    }


@app.post("/v1/chat/completions")
async def openai_chat(req: OpenAIChatRequest):
    """OpenAI-compatible chat completion endpoint."""
    import time
    import uuid

    # Extract the user's question from messages
    user_messages = [m for m in req.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found")

    question = user_messages[-1].content
    logger.info(f"OpenAI compat - Question: {question}")

    # Use our existing chat logic
    try:
        result = await chat(ChatRequest(question=question))
        content = result.summary

        # Add metadata section
        if result.metadata:
            meta = result.metadata
            meta_parts = []
            if meta.location:
                meta_parts.append(f"**Location:** {meta.location}")
            if meta.date_range_requested:
                meta_parts.append(f"**Date Range Requested:** {meta.date_range_requested}")
            if meta.date_range_with_data:
                meta_parts.append(f"**Data Available:** {meta.date_range_with_data}")

            if meta_parts:
                content += "\n\n---\n" + " | ".join(meta_parts)

        if result.sql:
            content += f"\n\n**SQL Query:**\n```sql\n{result.sql}\n```"
        if result.row_count is not None:
            content += f"\n\n*({result.row_count} rows returned)*"
    except HTTPException as e:
        content = f"Error: {e.detail}"

    return OpenAIChatResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        created=int(time.time()),
        model="forecaster",
        choices=[
            OpenAIChatChoice(
                index=0,
                message=OpenAIMessage(role="assistant", content=content)
            )
        ]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3352)
