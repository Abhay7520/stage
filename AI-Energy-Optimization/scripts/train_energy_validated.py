"""Deterministic file-group holdout; never joins energy and workload records."""

import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from src.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN

ROOT = Path(__file__).resolve().parents[1]


def main():
    files = sorted((ROOT / "data/energy").rglob("*.csv"))
    frames = []
    for p in files:
        df = pd.read_csv(p)
        df["source_file"] = str(p.relative_to(ROOT))
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    numeric = (
        df[FEATURE_COLUMNS + [TARGET_COLUMN]]
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    good = numeric.notna().all(axis=1) & (numeric >= 0).all(axis=1)
    numeric = numeric.loc[good]
    groups = df.loc[good, "source_file"]
    train, test = next(
        GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42).split(
            numeric, groups=groups
        )
    )
    X = numeric[FEATURE_COLUMNS]
    y = numeric[TARGET_COLUMN]
    model = XGBRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        n_jobs=2,
        random_state=42,
        subsample=0.9,
    )
    model.fit(X.iloc[train], y.iloc[train])
    pred = np.maximum(0, model.predict(X.iloc[test]))
    actual = y.iloc[test]
    mean = np.full(len(test), y.iloc[train].mean())

    def score(p):
        return {
            "mae_j": float(mean_absolute_error(actual, p)),
            "rmse_j": float(np.sqrt(mean_squared_error(actual, p))),
            "r2": float(r2_score(actual, p)),
        }

    result = {
        "dataset": "SWEAT supplied CSV collection",
        "files": len(files),
        "raw_rows": len(df),
        "valid_rows": len(numeric),
        "invalid_rows": int((~good).sum()),
        "training_rows": len(train),
        "test_rows": len(test),
        "train_files": sorted(set(groups.iloc[train])),
        "test_files": sorted(set(groups.iloc[test])),
        "split": "80/20 disjoint file groups, random_state=42; files sorted; test not used in fit or model choice",
        "xgboost": score(pred),
        "training_mean_baseline": score(mean),
        "limitations": [
            "File-level separation does not ensure unseen hardware separation",
            "Measurement interval duration/source provenance not supplied",
            "Do not map independent workload values to SWEAT rows",
            "CPU-input counterfactuals do not validate a resource-control model",
        ],
    }
    assert not set(result["train_files"]) & set(result["test_files"])
    model.save_model(ROOT / "models/energy_model.json")
    (ROOT / "models/energy_evaluation.json").write_text(json.dumps(result, indent=2))
    pd.DataFrame(
        {"actual_j": actual.values, "predicted_j": pred, "mean_baseline_j": mean}
    ).to_csv(ROOT / "outputs/energy_holdout.csv", index=False)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in ["train_files", "test_files"]},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
