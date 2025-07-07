#!/bin/bash
cd "$(dirname "$0")"
PYTHONPATH=. uvicorn sauron_api.main:app --host 0.0.0.0 --port 8000
