from pathlib import Path
import json

import pandas as pd
import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor

from src.workload_loader import load_workload_data
from src.workload_preprocessing import (
    prepare_workload_data
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

RESOURCE_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "resource"
    / "machine_usage_days_1_to_8_grouped_300_seconds.csv"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "workload_model.json"
)

PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "workload_predictions.csv"
)

MODEL_INFO_PATH = (
    PROJECT_ROOT
    / "models"
    / "workload_model_info.json"
)


# ============================================================
# CREATE REQUIRED FOLDERS
# ============================================================

(PROJECT_ROOT / "models").mkdir(
    exist_ok=True
)

(PROJECT_ROOT / "outputs").mkdir(
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("\n===================================")
print("PHASE 2 - WORKLOAD PREDICTION")
print("===================================")

df = load_workload_data(
    RESOURCE_DATA_PATH
)


# ============================================================
# PREPROCESS DATA
# ============================================================

df, lag_features = prepare_workload_data(
    df
)


# ============================================================
# DEFINE FEATURES
# ============================================================

TARGET_COLUMN = "next_cpu_util_percent"


CURRENT_FEATURES = [
    "cpu_util_percent",
    "mem_util_percent",
    "net_in",
    "net_out",
    "disk_io_percent"
]

FEATURE_COLUMNS = (
    CURRENT_FEATURES
    + lag_features
)


X = df[FEATURE_COLUMNS]

y = df[TARGET_COLUMN]


print("\nFeatures used by model:")

for feature in FEATURE_COLUMNS:
    print(f" - {feature}")

print("\nTarget:")
print(f" - {TARGET_COLUMN}")


# ============================================================
# CHRONOLOGICAL TRAIN / TEST SPLIT
# ============================================================

split_index = int(
    len(df) * 0.80
)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


print("\n===================================")
print("DATA SPLIT")
print("===================================")

print(f"Training rows: {len(X_train)}")
print(f"Testing rows : {len(X_test)}")


# ============================================================
# CREATE XGBOOST MODEL
# ============================================================

print("\n===================================")
print("CREATING XGBOOST WORKLOAD MODEL")
print("===================================")

model = XGBRegressor(

    objective="reg:squarederror",

    n_estimators=500,

    learning_rate=0.05,

    max_depth=6,

    min_child_weight=3,

    subsample=0.8,

    colsample_bytree=0.8,

    reg_alpha=0.1,

    reg_lambda=1.0,

    random_state=42,

    n_jobs=-1
)


# ============================================================
# TRAIN MODEL
# ============================================================

print("\nTraining started...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# ============================================================
# GENERATE PREDICTIONS
# ============================================================

print("\nGenerating workload predictions...")

predictions = model.predict(
    X_test
)


# ============================================================
# EVALUATION
# ============================================================

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)


print("\n===================================")
print("WORKLOAD MODEL RESULTS")
print("===================================")

print(f"MAE  : {mae:.4f} %")
print(f"RMSE : {rmse:.4f} %")
print(f"R²   : {r2:.4f}")


# ============================================================
# SAVE PREDICTIONS
# ============================================================

prediction_df = pd.DataFrame({

    "actual_cpu_util_percent":
        y_test.values,

    "predicted_cpu_util_percent":
        predictions

})

prediction_df.to_csv(
    PREDICTIONS_PATH,
    index=False
)


# ============================================================
# SAVE MODEL
# ============================================================

model.save_model(
    MODEL_PATH
)


# ============================================================
# SAVE MODEL INFORMATION
# ============================================================

model_info = {

    "model_type":
        "XGBoost Regressor",

    "purpose":
        "Next-step CPU workload prediction",

    "dataset":
        "machine_usage_days_1_to_8_grouped_300_seconds.csv",

    "target":
        TARGET_COLUMN,

    "features":
        FEATURE_COLUMNS,

    "training_rows":
        len(X_train),

    "testing_rows":
        len(X_test),

    "mae":
        float(mae),

    "rmse":
        float(rmse),

    "r2":
        float(r2)

}


with open(
    MODEL_INFO_PATH,
    "w"
) as file:

    json.dump(
        model_info,
        file,
        indent=4
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n===================================")
print("FILES CREATED")
print("===================================")

print(f"Model:")
print(MODEL_PATH)

print("\nPredictions:")
print(PREDICTIONS_PATH)

print("\nModel information:")
print(MODEL_INFO_PATH)

print("\n===================================")
print("WORKLOAD MODEL TRAINING FINISHED!")
print("===================================")