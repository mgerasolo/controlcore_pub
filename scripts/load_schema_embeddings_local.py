#!/usr/bin/env python3
"""Load schema embeddings using local sentence-transformers (matches ControlCore)."""

import json
import os
from pathlib import Path
import psycopg2
from sentence_transformers import SentenceTransformer

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Use the same model as ControlCore
MODEL_NAME = "all-mpnet-base-v2"  # 768 dimensions
print(f"Loading embedding model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)

def get_embedding(text: str) -> list[float]:
    """Get embedding vector from local model."""
    return model.encode(text).tolist()

def connect_db():
    """Connect to PostgreSQL."""
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        dbname="forecaster"
    )

def build_rows(path: Path) -> list[tuple]:
    """Build embedding rows from schema JSON file."""
    data = json.loads(path.read_text())
    rows = []

    for table in data.get("tables", []):
        tname = table.get("table")
        desc = table.get("description")

        # Table description
        if desc:
            print(f"  Embedding: {tname} (description)")
            vec = get_embedding(desc)
            rows.append((tname, None, desc, vec, path.name, "description"))

        # Column descriptions
        for col, cdesc in (table.get("columns") or {}).items():
            print(f"  Embedding: {tname}.{col}")
            vec = get_embedding(cdesc)
            rows.append((tname, col, cdesc, vec, path.name, "column"))

        # Aliases
        for alias in table.get("aliases", []) or []:
            print(f"  Embedding: {tname} alias '{alias}'")
            vec = get_embedding(alias)
            rows.append((tname, None, alias, vec, path.name, "alias"))

        # Example prompts
        for prompt in table.get("example_prompts", []) or []:
            print(f"  Embedding: {tname} prompt '{prompt[:40]}...'")
            vec = get_embedding(prompt)
            rows.append((tname, None, prompt, vec, path.name, "prompt"))

    return rows

def main():
    base = Path(__file__).parent.parent / "database_schemas" / "vector_embeddings"
    all_rows = []

    print("\nLoading schema embeddings...")
    for json_file in sorted(base.glob("*.json")):
        print(f"\nProcessing: {json_file.name}")
        all_rows.extend(build_rows(json_file))

    if not all_rows:
        print("No embeddings to insert")
        return

    print(f"\nInserting {len(all_rows)} embeddings into database...")

    conn = connect_db()

    # Register pgvector
    from pgvector.psycopg2 import register_vector
    register_vector(conn)

    insert_sql = """
        INSERT INTO schema_embeddings
        (table_name, column_name, content, embedding, source_file, entry_type)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (table_name, column_name, content, entry_type)
        DO UPDATE SET embedding = EXCLUDED.embedding, source_file = EXCLUDED.source_file
    """

    with conn:
        with conn.cursor() as cur:
            for row in all_rows:
                cur.execute(insert_sql, row)

    conn.close()
    print(f"\nSuccessfully inserted {len(all_rows)} embeddings!")

if __name__ == "__main__":
    main()
