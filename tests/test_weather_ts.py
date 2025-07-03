import sys
sys.path.append('.')
from pathlib import Path
import re


def test_fetch_daily_summary_defined():
    content = Path('controlcore_main_site/lib/weather.ts').read_text()
    assert 'export async function fetchDailySummary' in content
    assert 'daily_summary_data' in content
    match = re.search(r'fetchDailySummary\(limit = (\d+)\)', content)
    assert match and int(match.group(1)) > 0


def test_daily_summary_route_uses_function():
    route_path = Path('controlcore_main_site/app/api/weather/daily-summary/route.ts')
    assert route_path.exists()
    route_content = route_path.read_text()
    assert 'fetchDailySummary' in route_content

