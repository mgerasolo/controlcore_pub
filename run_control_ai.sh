#!/bin/bash
cd "$(dirname "$0")"
PYTHONPATH=. python controlcore_ai/core/master.py
