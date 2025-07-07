#!/bin/bash
export PYTHONPATH=/home/sauron/projects/codex_controlcore_agg
/home/sauron/environments/cc_data_manager/bin/python /home/sauron/projects/codex_controlcore_agg/openweather/scripts/openweather_overview_fill.py >> /home/sauron/projects/codex_controlcore_agg/openweather/data/logs/daily_script.log 2>&1
