# Forecast Accuracy Workflow

The `openweather_forecast_detail` table stores a snapshot of the next 24 hours each time the forecast is fetched. Every hour therefore has multiple predictions. `forecast_regression.py` unpivots these rows so each record includes both the snapshot time and the forecasted hour.

The script then merges this data with historical observations from `hourly_data` and optional sensor readings. After merging, it computes the forecast error metrics.

Run the analysis with:

```bash
python -m controlcore_ai.core.forecast_regression --days 3 --store
```

Metrics are stored in `forecast_accuracy` and `forecast_accuracy_lead` when `--store` is supplied. Use these tables to chart how error changes as the lead time decreases.
