from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
import httpx
import re
import sqlparse
import json
import datetime
import logging
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import Keyword, Whitespace

from shared import load_environment, connect_using_env
from sauron_api.sql_utils import run_sql
from shared.table_schema import collect_table_schema
from shared.schema_introspect import list_public_tables

load_environment()

app = FastAPI()

GANDALF_SQL_URL = os.getenv("GANDALF_SQL_URL", "http://localhost:9001/generate-sql")
GANDALF_ANALYZE_URL = os.getenv("GANDALF_ANALYZE_URL", "http://localhost:9001/analyze")
GANDALF_REPHRASE_URL = os.getenv("GANDALF_REPHRASE_URL", "http://localhost:9001/rephrase")

class ChatRequest(BaseModel):
    question: str

# Databases to introspect for table names
DB_NAMES = [
    "openweather_historical",
    "openweather_forecast",
    "controlcore",
]


def build_db_tables() -> dict:
    """Return mapping of database names to their public tables."""
    tables = {}
    for name in DB_NAMES:
        tbls = list_public_tables(name)
        logging.debug("Discovered tables for %s: %s", name, tbls)
        tables[name] = tbls
    return tables


# Valid tables for each known schema
DB_TABLES = build_db_tables()

def _extract_table_identifiers(stmt):
    tables = []
    tokens = list(stmt.tokens)
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.is_group:
            tables.extend(_extract_table_identifiers(token))
        if token.ttype is Keyword and token.value.upper() in ("FROM", "JOIN", "UPDATE", "INTO"):
            j = i + 1
            while j < len(tokens) and tokens[j].ttype is Whitespace:
                j += 1
            if j < len(tokens):
                next_tok = tokens[j]
                if isinstance(next_tok, IdentifierList):
                    for ident in next_tok.get_identifiers():
                        tables.append(ident)
                elif isinstance(next_tok, Identifier):
                    tables.append(next_tok)
        i += 1
    return tables

def strip_fake_schemas(sql: str) -> str:
    """Remove schema prefixes for tables that don't exist in that schema."""
    parsed = sqlparse.parse(sql)
    if not parsed:
        return sql
    stmt = parsed[0]
    tables = _extract_table_identifiers(stmt)
    replacements = []
    for ident in tables:
        schema = ident.get_parent_name()
        table = ident.get_real_name()
        if schema and table and table not in DB_TABLES.get(schema, []):
            replacements.append((f"{schema}.{table}", table))
    for old, new in replacements:
        sql = sql.replace(old, new)
    return sql

def guess_db(question: str) -> str:
    q = question.lower()
    if "forecast" in q or "predicted" in q:
        return "openweather_forecast"
    elif "rain" in q or "historical" in q or "temperature in" in q:
        return "openweather_historical"
    else:
        return "controlcore"

def db_from_sql(sql: str) -> str | None:
    sql_lower = sql.lower()
    if "openweather_forecast." in sql_lower:
        return "openweather_forecast"
    if "openweather_historical." in sql_lower:
        return "openweather_historical"
    return None

def safe_serialize(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)

def clean_sql_block(query: str) -> str:
    # Remove markdown formatting if present
    if query.strip().startswith("```sql"):
        query = query.strip().strip("```sql").strip("```").strip()

    # Use sqlparse to extract only the first statement (ignore commentary or explanations)
    parsed = sqlparse.parse(query)
    if not parsed:
        return query

    stmt = parsed[0].value.strip()
    return stmt

def validate_tables(sql: str) -> None:
    """Ensure all referenced tables exist in the known schemas."""
    parsed = sqlparse.parse(sql)
    if not parsed:
        return

    stmt = parsed[0]
    identifiers = _extract_table_identifiers(stmt)

    # Build a set of valid table names without schema for quick lookup
    all_tables = set()
    for tables in DB_TABLES.values():
        all_tables.update(tables)

    for ident in identifiers:
        table = ident.get_real_name()
        if not table:
            continue
        schema = ident.get_parent_name()
        if schema:
            if table not in DB_TABLES.get(schema, []):
                raise HTTPException(status_code=400, detail=f"unknown table: {table}")
        else:
            if table not in all_tables:
                raise HTTPException(status_code=400, detail=f"unknown table: {table}")


def validate_sql(query: str) -> None:
    """Perform basic sanity checks on the SQL before execution."""
    stripped = query.strip()
    if not stripped:
        raise ValueError("empty SQL")
    # Simple balanced parentheses check
    depth = 0
    for ch in stripped:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced parentheses")
    if depth != 0:
        raise ValueError("unbalanced parentheses")

# Map database names to the environment variables holding credentials
DB_USER_VARS = {
    "controlcore": ("CONTROLCORE_USER", "CONTROLCORE_PW"),
    "openweather_historical": ("OPENHIST_USER", "OPENHIST_PW"),
    "openweather_forecast": ("OPENFORE_USER", "OPENFORE_PW"),
}

@app.post("/chat")
async def chat(req: ChatRequest):
    schema = collect_table_schema(req.question)

    # Step 1: Rephrase and ask Gandalf to generate SQL
    async with httpx.AsyncClient() as client:
        rep_resp = await client.post(GANDALF_REPHRASE_URL, json={"text": req.question})
        rep_resp.raise_for_status()
        clean_q = rep_resp.json().get("text", req.question)

        gen_resp = await client.post(GANDALF_SQL_URL, json={"question": clean_q, "schema": schema})
        gen_resp.raise_for_status()
        sql = gen_resp.json().get("sql")

    if not sql:
        raise HTTPException(status_code=500, detail="Gandalf did not return SQL")

    logging.info("Original SQL: %s", sql)

    detected = db_from_sql(sql)
    sql = strip_fake_schemas(sql)
    sql = clean_sql_block(sql)
    validate_tables(sql)

    try:
        validate_sql(sql)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    logging.info("Stripped SQL: %s", sql)

    # Step 2: Pick database connection
    dbname = detected or guess_db(req.question)

    try:
        user_var, pw_var = DB_USER_VARS.get(dbname, ("PG_USER", "PG_PASSWORD"))
        with connect_using_env(dbname, user_var, pw_var) as conn:
            result = run_sql(conn, sql)
    except HTTPException as e:
        # Propagate user-facing errors from run_sql
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL execution failed: {e}")

    # Step 3: Ask Gandalf to analyze
    safe_rows = [
        {k: safe_serialize(v) for k, v in row.items()} for row in result
    ]

    async with httpx.AsyncClient() as client:
        final_resp = await client.post(GANDALF_ANALYZE_URL, json={
            "question": req.question,
            "sql": sql,
            "rows": safe_rows
        })
        final_resp.raise_for_status()
        data = final_resp.json()

    return data

