import sys
sys.path.append('.')

from controlcore_ai.core import master


def run_main(monkeypatch, mode):
    calls = []
    def fake_run(cmd, check=True):
        calls.append(cmd)
    monkeypatch.setattr(master, 'get_last_run', lambda name: None)
    monkeypatch.setattr(master.subprocess, 'run', fake_run)
    master.main(advisor_interval=0, forecast_interval=0, mode=mode)
    return [c[2] for c in calls]


def test_heavy_runs_all(monkeypatch):
    modules = run_main(monkeypatch, 'heavy')
    assert modules == ['controlcore_ai.core.runner', 'controlcore_ai.core.advisor', 'controlcore_ai.core.forecast_regression']


def test_light_skips_forecast(monkeypatch):
    modules = run_main(monkeypatch, 'light')
    assert modules == ['controlcore_ai.core.runner', 'controlcore_ai.core.advisor']
