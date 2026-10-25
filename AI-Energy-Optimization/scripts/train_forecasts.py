"""Blocked, purged evaluation. File order is an assumption, not proven chronology."""

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from backend.intelligence.service import RESOURCE_COLUMNS, FEATURE_COLUMNS

ROOT = Path(__file__).resolve().parents[1]


def metrics(y, p):
    return {
        "mae": float(mean_absolute_error(y, p)),
        "rmse": float(np.sqrt(mean_squared_error(y, p))),
        "r2": float(r2_score(y, p)),
    }


def main():
    path = ROOT / "data/resource/machine_usage_days_1_to_8_grouped_300_seconds.csv"
    raw = pd.read_csv(path)
    df = (
        raw[RESOURCE_COLUMNS]
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    valid = df.notna().all(axis=1) & (df >= 0).all(axis=1)
    for c in ("cpu_util_percent", "mem_util_percent", "disk_io_percent"):
        valid &= df[c] <= 100
    df.loc[~valid, :] = (
        np.nan
    )  # preserve gaps rather than stitching unrelated observations
    features = df.copy()
    for c in RESOURCE_COLUMNS:
        for lag in (1, 2, 3):
            features[f"{c}_lag_{lag}"] = df[c].shift(lag)
    for key, c in [("cpu", "cpu_util_percent"), ("memory", "mem_util_percent")]:
        features[key + "_target"] = df[c].shift(-1)
    clean = features.dropna()
    n = len(df)
    train = clean.loc[clean.index < int(n * 0.6) - 4]
    val = clean.loc[
        (clean.index >= int(n * 0.6) + 4) & (clean.index < int(n * 0.8) - 4)
    ]
    test = clean.loc[clean.index >= int(n * 0.8) + 4]
    result = {
        "dataset": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "raw_rows": n,
        "invalid_rows": int((~valid).sum()),
        "split": "60/20/20 file-order blocks with four-row purges; timestamps/entity IDs absent",
        "training_rows": len(train),
        "validation_rows": len(val),
        "test_rows": len(test),
        "features": FEATURE_COLUMNS,
        "limitation": "Aggregated trace, no timestamp or entity IDs. Not validated per-VM or chronological forecasting.",
    }
    predictions = {}
    for key, col in [("cpu", "cpu_util_percent"), ("memory", "mem_util_percent")]:
        model = XGBRegressor(
            n_estimators=180,
            max_depth=3,
            learning_rate=0.04,
            subsample=0.9,
            colsample_bytree=0.9,
            n_jobs=2,
            random_state=42,
        )
        model.fit(train[FEATURE_COLUMNS], train[key + "_target"])
        vp = np.clip(model.predict(val[FEATURE_COLUMNS]), 0, 100)
        selected = (
            "xgboost"
            if mean_absolute_error(val[key + "_target"], vp)
            < mean_absolute_error(val[key + "_target"], val[col])
            else "persistence"
        )
        tp = np.clip(model.predict(test[FEATURE_COLUMNS]), 0, 100)
        result[key] = {
            "selected": selected,
            "validation_xgboost": metrics(val[key + "_target"], vp),
            "validation_persistence": metrics(val[key + "_target"], val[col]),
            "test_xgboost": metrics(test[key + "_target"], tp),
            "test_persistence": metrics(test[key + "_target"], test[col]),
        }
        model.save_model(ROOT / f"models/{key}_forecast.json")
        predictions[key + "_actual"] = test[key + "_target"].values
        predictions[key + "_xgboost"] = tp
        predictions[key + "_persistence"] = test[col].values
    (ROOT / "models/forecast_evaluation.json").write_text(json.dumps(result, indent=2))
    pd.DataFrame(predictions).to_csv(ROOT / "outputs/forecast_holdout.csv", index=False)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
