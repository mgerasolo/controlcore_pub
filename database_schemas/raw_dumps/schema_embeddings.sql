CREATE TABLE schema_embeddings (
  id serial PRIMARY KEY,
  table_name text,
  column_name text,
  content text,
  embedding vector(768),
  source_file text,
  entry_type text  -- alias | column | example | description
);
