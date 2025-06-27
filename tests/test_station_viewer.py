import sys
sys.path.append('.')

from datetime import datetime
from station_viewer.python.src.services.cc_data_manager import resolve_timestamp


def test_resolve_timestamp_valid():
    ts = 1700000000
    expected = datetime.utcfromtimestamp(ts)
    assert resolve_timestamp(ts) == expected


def test_resolve_timestamp_invalid():
    result = resolve_timestamp("notatime")
    assert isinstance(result, datetime)


