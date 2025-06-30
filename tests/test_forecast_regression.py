import sys
sys.path.append('.')
import math
from datetime import datetime, timezone
import pandas as pd
import pytest
from controlcore_ai.core.forecast_regression import (
    calculate_error_metrics,
    calculate_error_by_lead,
    run_forecast_regression,
)


def test_calculate_error_metrics():
    df = pd.DataFrame({'forecast_temp': [10, 12, 14], 'actual_temp': [9, 13, 15]})
    metrics = calculate_error_metrics(df)
    assert metrics['mae'] == pytest.approx((1 + 1 + 1) / 3)
    expected_rmse = math.sqrt(((10-9)**2 + (12-13)**2 + (14-15)**2) / 3)
    assert metrics['rmse'] == pytest.approx(expected_rmse)


def test_calculate_error_metrics_ignore_nan():
    df = pd.DataFrame({'forecast_temp': [10, 12], 'actual_temp': [10, None]})
    metrics = calculate_error_metrics(df)
    assert metrics['mae'] == 0
    assert metrics['rmse'] == 0


def test_timezone_merge_and_lead_metrics():
    forecast_df = pd.DataFrame({
        'forecast_time': [pd.Timestamp('2024-01-01T00:00Z')],
        'snapshot_time': [pd.Timestamp('2023-12-31T18:00Z')],
        'lat': [1.0],
        'lon': [2.0],
        'forecast_temp': [10],
        'actual_temp': [12],
        'lead_hours': [6],
    })

    hist_df = pd.DataFrame({
        'ts': [pd.Timestamp('2024-01-01T00:00')],
        'lat': [1.0],
        'lon': [2.0],
        'actual_temp': [12],
    })
    hist_df['ts'] = pd.to_datetime(hist_df['ts'], utc=True)

    merged = pd.merge(
        forecast_df,
        hist_df,
        left_on=['lat', 'lon', 'forecast_time'],
        right_on=['lat', 'lon', 'ts'],
        how='left',
    )

    assert merged['actual_temp_y'].iloc[0] == 12

    grouped = calculate_error_by_lead(forecast_df)
    assert 'mae' in grouped.columns and 'rmse' in grouped.columns

def test_run_forecast_regression_filters_future(monkeypatch):
    now = pd.Timestamp(datetime.now(timezone.utc))
    future = now + pd.Timedelta(hours=1)
    past = now - pd.Timedelta(hours=1)
    df = pd.DataFrame({
        'forecast_time': [future, past],
        'snapshot_time': [past - pd.Timedelta(hours=5), past - pd.Timedelta(hours=5)],
        'lat': [1.0, 1.0],
        'lon': [2.0, 2.0],
        'forecast_temp': [10, 11],
        'actual_temp': [12, 11],
        'lead_hours': [7, 6],
    })

    monkeypatch.setattr('controlcore_ai.core.forecast_regression._fetch_data', lambda d: df)
    result_df = run_forecast_regression(store=False)

    assert len(result_df) == 1
    assert result_df['forecast_time'].max() <= now

