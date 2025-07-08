from pathlib import Path

def _read(path: str) -> str:
    return Path(path).read_text()


def test_station_viewer_uses_specific_env_vars():
    cc_manager = _read('station_viewer/python/src/services/cc_data_manager.py')
    cleanup = _read('station_viewer/python/src/services/data_cleanup.py')
    for content in (cc_manager, cleanup):
        assert 'CONTROLCORE_USER' in content
        assert 'CONTROLCORE_PW' in content
        assert 'PG_USER' not in content
        assert 'PG_PASSWORD' not in content


def test_openweather_config_uses_specific_env_vars():
    content = _read('openweather/src/config/config.py')
    assert 'OPENHIST_USER' in content and 'OPENHIST_PW' in content
    assert 'OPENFORE_USER' in content and 'OPENFORE_PW' in content
    assert 'PG_USER' not in content and 'PG_PASSWORD' not in content
