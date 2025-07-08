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
