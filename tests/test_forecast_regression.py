import math
import pandas as pd
import pytest
from controlcore_ai.core.forecast_regression import calculate_error_metrics


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
