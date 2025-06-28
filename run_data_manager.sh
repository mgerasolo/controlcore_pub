#!/bin/bash
cd "$(dirname "$0")"
PYTHONPATH=. python station_viewer/python/src/services/cc_data_manager.py
