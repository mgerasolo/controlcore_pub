# Schema Introspection

The API needs a concise description of all database tables so Gandalf can craft valid SQL queries.
`collect_table_schema` queries each configured database and builds a markdown listing of tables and columns.

1. `list_public_tables` connects to a database using credentials from environment variables and reads
   `information_schema.tables` for the `public` schema. This returns every base table name.
2. For the tables returned, `fetch_schema` pulls column names and data types from
   `information_schema.columns`.
3. The results are formatted into a single markdown string used by the LLM.

This dynamic approach ensures the schema information always matches the actual databases without
manual updates.

When Gandalf is asked to generate SQL, the schema is supplied in a JSON block grouped by database
name. Each database is independent; table names should be referenced directly without including the
database prefix. The prompt explicitly mentions that the databases use PostgreSQL so the language
model emits that dialect. The example query in the prompt shows this style (`SELECT * FROM table LIMIT 5;`).

In addition to the live introspection, richer descriptions, common aliases and
example queries live in JSON files under `database_schemas/vector_embeddings`.
Run `python scripts/load_schema_vectors.py` to encode these definitions and
populate the `schema_embeddings` table (requires the `pgvector` extension and
database credentials via `CONTROLCORE_USER`/`CONTROLCORE_PW`). The `/chat`
endpoint searches this table for snippets most similar to the user's question
and sends those hints to Gandalf with the introspected schema.
