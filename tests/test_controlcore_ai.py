import os
import sys
import pathlib
import importlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

sys.path.append(str(ROOT))
sys.path.append(str(ROOT / 'controlcore_ai' / 'core'))

_cwd = os.getcwd()
os.chdir(ROOT / 'controlcore_ai' / 'core')
advisor = importlib.import_module('advisor')
os.chdir(_cwd)
advise_watering = advisor.advise_watering


def test_advise_skip_due_to_recent_rain():
    decision, reasons = advise_watering({}, {"recent_rain_mm_last_3_days": 12})
    assert decision == "skip"
    assert "last 3 days" in reasons[0]


def test_advise_skip_due_to_forecast():
    weather = {"hourly_pop_windows": {"a": 0.9, "b": 0.95, "c": 0.94, "d": 0.93}}
    decision, reasons = advise_watering({}, weather)
    assert decision == "skip"
    assert "High-confidence forecast" in reasons[0]

