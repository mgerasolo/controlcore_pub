#!/bin/bash
cd "$(dirname "$0")"
PYTHONPATH=. python scripts/load_schema_vectors.py
