from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os
import json

app = FastAPI()

# Default model fallbacks
SQL_MODEL = os.getenv("OLLAMA_SQL_MODEL", "deepseek-coder:6.7b")
SUMMARY_MODEL = os.getenv("OLLAMA_SUMMARY_MODEL", "llama3")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

class SQLRequest(BaseModel):
    question: str
    schema: str
    context: list[dict] | None = None

class AnalyzeRequest(BaseModel):
    question: str
    sql: str
    rows: list[dict]

class RephraseRequest(BaseModel):
    text: str

def build_sql_prompt(question: str, schema: str, context: list[dict] | None = None) -> str:
    """Return the prompt for the SQL‑generation model.

    The schema may be a markdown list of tables and columns.  Present it in a
    JSON code block so the language model receives a compact representation.
    A short example query is included before the actual user question to
    demonstrate the expected table reference format.
    """

    example = "SELECT * FROM table LIMIT 5;"
    formatted_schema = f"```json\n{schema}\n```"

    prompt = (
        "You are an AI assistant that generates SQL queries for weather and "
        "environmental databases. The databases use PostgreSQL syntax.\n\n"
        f"Schema:\n{formatted_schema}\n"
    )

    if context:
        ctx_json = json.dumps(context, indent=2)
        prompt += f"\nHints:\n```json\n{ctx_json}\n```"

    prompt += (
        "\n\nEach listed database is separate. Use table names directly without "
        "prefixing them with the database name.\n\n"
        "Example query using the schema above:\n"
        f"```sql\n{example}\n```\n\n"
        "Use **only** the table names exactly as they appear in the schema. Do "
        "not guess or invent new table names.\n\n"
        "User question:\n"
        f"{question} postgres\n\n"
        "Only return a valid SQL query. Do not explain it."
        " Respond with the SQL statement only—no commentary, no Markdown fences."
    )

    return prompt

def build_summary_prompt(question: str, sql: str, rows: list[dict]) -> str:
    return f"""You are a Markdown report writer for a weather analytics system.

A user asked:
{question}

The system generated and executed the following SQL query:
{sql}

Here are the results (as JSON rows):
{rows}

Write a short Markdown summary that presents the key insight.
Do **not** re-explain SQL. 
If the data is numeric, mention totals or trends.
If the data spans time or categories, suggest a chart type and describe axes (e.g., "X-axis is day, Y-axis is rainfall in inches").
Only include the summary and chart recommendation.
"""

async def call_ollama(prompt: str, model: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()

@app.post("/rephrase")
async def rephrase(req: RephraseRequest):
    prompt = (
        "Clean and simplify this question for a coding model. "
        "Clarify any ambiguous date ranges or metrics if possible:\n"
        f"{req.text}"
    )
    response = await call_ollama(prompt, model="llama3")
    return {"text": response}

@app.post("/generate-sql")
async def generate_sql(req: SQLRequest):
    prompt = build_sql_prompt(req.question, req.schema, req.context)
    response = await call_ollama(prompt, model=SQL_MODEL)
    return {"sql": response}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    prompt = build_summary_prompt(req.question, req.sql, req.rows)
    response = await call_ollama(prompt, model=SUMMARY_MODEL)
    return {"summary": response}
