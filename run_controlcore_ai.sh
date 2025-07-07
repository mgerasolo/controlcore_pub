#!/bin/bash

# Set the working directory to where the project lives
cd /home/sauron/projects/codex_controlcore_agg

# Set the PYTHONPATH so relative imports work
export PYTHONPATH=/home/sauron/projects/codex_controlcore_agg

# Activate the correct environment and run the master script
/home/sauron/environments/cc_data_manager/bin/python controlcore_ai/core/master.py \
  >> /home/sauron/projects/codex_controlcore_agg/controlcore_ai/logs/master_cron.log 2>&1
