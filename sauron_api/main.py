from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
import httpx
import re

from shared import load_environment, connect_using_env
from sauron_api.sql_utils import run_sql
from shared.table_schema import collect_table_schema

load_environment()

app = FastAPI()

GANDALF_SQL_URL = os.getenv("GANDALF_SQL_URL", "http://localhost:9001/generate-sql")
GANDALF_ANALYZE_URL = os.getenv("GANDALF_ANALYZE_URL", "http://localhost:9001/analyze")

class ChatRequest(BaseModel):
    question: str

def strip_fake_schemas(sql: str) -> str:
    """Removes hallucinated schema prefixes like openweather_forecast.*"""
    return re.sub(r"\b(openweather_forecast|openweather_historical|controlcore)\.", "", sql)

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

# Map database names to the environment variables holding credentials
DB_USER_VARS = {
    "controlcore": ("CONTROLCORE_USER", "CONTROLCORE_PW"),
    "openweather_historical": ("OPENHIST_USER", "OPENHIST_PW"),
    "openweather_forecast": ("OPENFORE_USER", "OPENFORE_PW"),
}

@app.post("/chat")
async def chat(req: ChatRequest):
    schema = collect_table_schema(req.question)

    # Step 1: Ask Gandalf to generate SQL
    async with httpx.AsyncClient() as client:
        gen_resp = await client.post(GANDALF_SQL_URL, json={"question": req.question, "schema": schema})
        gen_resp.raise_for_status()
        sql = gen_resp.json().get("sql")

    if not sql:
        raise HTTPException(status_code=500, detail="Gandalf did not return SQL")

    print("Original SQL:", sql)

    detected = db_from_sql(sql)
    sql = strip_fake_schemas(sql)
    print("Stripped SQL:", sql)

    # Step 2: Pick database connection
    dbname = detected or guess_db(req.question)

    try:
        user_var, pw_var = DB_USER_VARS.get(dbname, ("PG_USER", "PG_PASSWORD"))
        with connect_using_env(dbname, user_var, pw_var) as conn:
            result = run_sql(conn, sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL execution failed: {e}")

    # Step 3: Ask Gandalf to analyze
    async with httpx.AsyncClient() as client:
        final_resp = await client.post(GANDALF_ANALYZE_URL, json={
            "question": req.question,
            "sql": sql,
            "rows": result
        })
        final_resp.raise_for_status()
        data = final_resp.json()

    return data
