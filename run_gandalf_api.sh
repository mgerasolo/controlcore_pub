#!/bin/bash
cd "$(dirname "$0")"
PYTHONPATH=. uvicorn gandalf_api.sql_query_handler:app --host 0.0.0.0 --port 9001

