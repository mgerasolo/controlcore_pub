from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
import httpx

from shared import load_environment, connect_using_env
from shared.table_schema import collect_table_schema
from sauron_api.sql_utils import run_sql

load_environment()

app = FastAPI()

GANDALF_SQL_URL = os.getenv("GANDALF_SQL_URL", "http://192.168.100.40:9001/generate-sql")
GANDALF_ANALYZE_URL = os.getenv("GANDALF_ANALYZE_URL", "http://192.168.100.40:9001/analyze")

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(req: ChatRequest):
    schema = collect_table_schema(req.question)

    # Step 1: Get SQL from Gandalf
    async with httpx.AsyncClient() as client:
        gen_resp = await client.post(GANDALF_SQL_URL, json={"question": req.question, "schema": schema})
        gen_resp.raise_for_status()
        sql = gen_resp.json().get("sql")

    if not sql:
        raise HTTPException(status_code=500, detail="Gandalf did not return SQL")

    # Step 2: Execute SQL against the local DB
    try:
        with connect_using_env("controlcore", "PG_USER", "PG_PASSWORD") as conn:
            print(sql)
            rows = run_sql(conn, sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL execution failed: {e}")

    # Step 3: Send results to Gandalf for analysis
    async with httpx.AsyncClient() as client:
        final_resp = await client.post(GANDALF_ANALYZE_URL, json={
            "question": req.question,
            "sql": sql,
            "rows": rows
        })
        final_resp.raise_for_status()
        data = final_resp.json()

    return data
