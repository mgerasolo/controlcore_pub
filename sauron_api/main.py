from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
import httpx

from shared import load_environment, connect_using_env
from shared.table_schema import collect_table_schema

load_environment()

app = FastAPI()

DEEPSEEK_URL = os.getenv("DEEPSEEK_URL", "http://localhost:8001")

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(req: ChatRequest):
    schema = collect_table_schema(req.question)

    async with httpx.AsyncClient() as client:
        gen_resp = await client.post(f"{DEEPSEEK_URL}/generate-sql", json={"question": req.question, "schema": schema})
        gen_resp.raise_for_status()
        sql = gen_resp.json().get("sql")

    if not sql:
        raise HTTPException(status_code=500, detail="DeepSeek did not return SQL")

    try:
        with connect_using_env("controlcore", "PG_USER", "PG_PASSWORD") as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL execution failed: {e}")

    async with httpx.AsyncClient() as client:
        final_resp = await client.post(f"{DEEPSEEK_URL}/analyze", json={"question": req.question, "sql": sql, "rows": rows})
        final_resp.raise_for_status()
        data = final_resp.json()

    return data
