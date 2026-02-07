"""
Gandalf API - Modified for LiteLLM + SQLCoder

Changes from original:
1. Uses OpenAI-compatible API (LiteLLM) instead of Ollama native API
2. Uses SQLCoder-specific prompt format for SQL generation
3. Configurable via LITELLM_* environment variables
"""

from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
from openai import AsyncOpenAI

app = FastAPI(title="Gandalf API - Middle Earth Forecaster")

# LiteLLM configuration
LITELLM_API_URL = os.getenv("LITELLM_API_URL", "http://10.0.0.27:2764/v1")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "sk-21cFr6t5HDbW-KxJY8NbWg")
SQL_MODEL = os.getenv("LITELLM_SQL_MODEL", "jarvis-sqlcoder")
SUMMARY_MODEL = os.getenv("LITELLM_SUMMARY_MODEL", "jarvis-llama31")

# Async OpenAI client pointing to LiteLLM
client = AsyncOpenAI(
    api_key=LITELLM_API_KEY,
    base_url=LITELLM_API_URL
)


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


def build_sqlcoder_prompt(question: str, schema: str, context: list[dict] | None = None) -> str:
    """Build prompt using SQLCoder's expected format.

    SQLCoder expects a specific structure:
    ### Task
    ### Database Schema (as DDL)
    ### Answer
    """

    # Add context hints if available
    hints = ""
    if context:
        hint_lines = [f"- {h.get('table', '')}.{h.get('column', '')}: {h.get('description', '')}"
                      for h in context if h.get('table')]
        if hint_lines:
            hints = "\n\nRelevant columns:\n" + "\n".join(hint_lines)

    prompt = f"""### Task
Generate a SQL query to answer [QUESTION]{question}[/QUESTION]{hints}

### Database Schema
The query will run on a database with the following schema:
{schema}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{question}[/QUESTION]
[SQL]"""

    return prompt


def detect_missing_data(rows: list[dict]) -> bool:
    """Detect if query results indicate missing data."""
    if not rows:
        return True
    # Check if all values in first row are None
    if rows and all(v is None for v in rows[0].values()):
        return True
    return False


def build_summary_prompt(question: str, sql: str, rows: list[dict]) -> str:
    """Build prompt for summarizing SQL results."""

    # Detect missing data scenario
    is_missing_data = detect_missing_data(rows)

    # Limit rows to prevent token overflow
    display_rows = rows[:20] if len(rows) > 20 else rows
    rows_json = json.dumps(display_rows, indent=2, default=str)

    if is_missing_data:
        return f"""You are a helpful assistant for a weather analytics system called "Middle Earth Forecaster".

A user asked: "{question}"

The system executed this SQL query:
```sql
{sql}
```

Results: The query returned no data or NULL values.

Write a helpful response that:
1. Acknowledges we don't have data for their request
2. Offers to fetch the data from OpenWeather API (mention they can ask you to "fetch weather data for [location]")
3. Suggests alternative queries they could try (e.g., different date range or available locations: Fincastle, Roanoke, Rome)

Be friendly and helpful. End with an actionable suggestion."""
    else:
        return f"""You are a helpful assistant for a weather analytics system called "Middle Earth Forecaster".

A user asked: "{question}"

The system executed this SQL query:
```sql
{sql}
```

Results ({len(rows)} rows{', showing first 20' if len(rows) > 20 else ''}):
```json
{rows_json}
```

Write a clear, friendly response that:
1. Directly answers their question
2. Highlights the key insight from the data
3. If applicable, mentions any trends or notable values

Keep your response concise but complete. Do not explain the SQL query."""


async def call_llm(prompt: str, model: str, max_tokens: int = 500) -> str:
    """Call LiteLLM using OpenAI-compatible API."""

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0  # Deterministic for SQL generation
    )

    return response.choices[0].message.content.strip()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "models": {"sql": SQL_MODEL, "summary": SUMMARY_MODEL}}


@app.post("/rephrase")
async def rephrase(req: RephraseRequest):
    """Clean and simplify user questions."""

    prompt = f"""Clean and simplify this question for a SQL database query.
Clarify any ambiguous date ranges (e.g., "last week" → specific dates).
Keep the core question intact.

Question: {req.text}

Simplified question:"""

    response = await call_llm(prompt, model=SUMMARY_MODEL, max_tokens=200)
    return {"text": response}


@app.post("/generate-sql")
async def generate_sql(req: SQLRequest):
    """Generate SQL query using SQLCoder."""

    prompt = build_sqlcoder_prompt(req.question, req.schema, req.context)
    response = await call_llm(prompt, model=SQL_MODEL, max_tokens=500)

    # Clean up response - SQLCoder sometimes includes extra text
    sql = response.strip()

    # Remove markdown fencing if present
    if sql.startswith("```sql"):
        sql = sql[6:]
    if sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]

    return {"sql": sql.strip()}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """Analyze SQL results and provide natural language summary."""

    prompt = build_summary_prompt(req.question, req.sql, req.rows)
    response = await call_llm(prompt, model=SUMMARY_MODEL, max_tokens=500)
    return {"summary": response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3354)
