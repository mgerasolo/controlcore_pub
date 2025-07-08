#!/usr/bin/env python3
"""Load schema embeddings from JSON files into Postgres."""
from __future__ import annotations

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
from psycopg2.extras import execute_values

from shared.env_utils import load_environment, connect_using_env

MODEL_NAME = "all-mpnet-base-v2"  # 768-dim embeddings


def build_rows(path: Path, model: SentenceTransformer) -> list[tuple]:
    data = json.loads(path.read_text())
    rows: list[tuple] = []
    for table in data.get("tables", []):
        tname = table.get("table")
        desc = table.get("description")
        if desc:
            vec = model.encode(desc).tolist()
            rows.append((tname, None, desc, vec, path.name, "description"))

        for col, cdesc in (table.get("columns") or {}).items():
            vec = model.encode(cdesc).tolist()
            rows.append((tname, col, cdesc, vec, path.name, "column"))

        for alias in table.get("aliases", []) or []:
            vec = model.encode(alias).tolist()
            rows.append((tname, None, alias, vec, path.name, "alias"))

        for example in table.get("example_queries", []) or []:
            vec = model.encode(example).tolist()
            rows.append((tname, None, example, vec, path.name, "example"))
    return rows


def main() -> None:
    load_environment()
    model = SentenceTransformer(MODEL_NAME)
    base = Path("database_schemas/vector_embeddings")
    all_rows: list[tuple] = []
    for json_file in sorted(base.glob("*.json")):
        all_rows.extend(build_rows(json_file, model))

    if not all_rows:
        print("No embeddings to insert")
        return

    conn = connect_using_env("controlcore", "CONTROLCORE_USER", "CONTROLCORE_PW")
    register_vector(conn)

    insert_sql = (
        "INSERT INTO schema_embeddings"
        " (table_name, column_name, content, embedding, source_file, entry_type)"
        " VALUES %s"
        " ON CONFLICT (table_name, column_name, content, entry_type)"
        " DO UPDATE SET embedding = EXCLUDED.embedding, source_file = EXCLUDED.source_file"
    )

    with conn:
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, all_rows)

    print(f"Inserted {len(all_rows)} embeddings")


if __name__ == "__main__":
    main()
