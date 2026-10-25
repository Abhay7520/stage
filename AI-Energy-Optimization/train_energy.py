from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor

from src.data_loader import load_energy_files
from src.preprocessing import (
    prepare_energy_data,
    FEATURE_COLUMNS,
    TARGET_COLUMN
)


# =========================================================
# 1. PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

ENERGY_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "energy"
    / "SWEAT"
    / "preprocessed_data"
    / "Infra-A"
)

MODEL_FOLDER = PROJECT_ROOT / "models"
OUTPUT_FOLDER = PROJECT_ROOT / "outputs"

MODEL_FOLDER.mkdir(
    exist_ok=True
)

OUTPUT_FOLDER.mkdir(
    exist_ok=True
)


# =========================================================
# 2. LOAD DATA
# =========================================================

print("\n==========================================")
print("AI ENERGY OPTIMIZATION PROJECT")
print("ENERGY PREDICTION MODEL")
print("==========================================")

print("\nDataset location:")
print(ENERGY_DATA_PATH)


df, file_count = load_energy_files(
    ENERGY_DATA_PATH
)


# =========================================================
# 3. PREPROCESS
# =========================================================

df = prepare_energy_data(df)


# =========================================================
# 4. DEFINE FEATURES AND TARGET
# =========================================================

X = df[FEATURE_COLUMNS]

y = df[TARGET_COLUMN]

groups = df["source_file"]


print("\nFeatures used by model:")

for feature in FEATURE_COLUMNS:
    print(" -", feature)

print("\nTarget:")
print(" -", TARGET_COLUMN)


# =========================================================
# 5. TRAIN / TEST SPLIT
# =========================================================
#
# IMPORTANT:
# We split by source file rather than randomly splitting
# individual rows.
#
# This prevents rows from the same experimental run
# appearing in both training and testing data.
# =========================================================

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_indices, test_indices = next(
    splitter.split(
        X,
        y,
        groups=groups
    )
)

X_train = X.iloc[train_indices]
X_test = X.iloc[test_indices]

y_train = y.iloc[train_indices]
y_test = y.iloc[test_indices]


print("\n==========================================")
print("DATA SPLIT")
print("==========================================")

print(f"Training rows: {len(X_train)}")
print(f"Testing rows : {len(X_test)}")

print(
    f"Training files: "
    f"{groups.iloc[train_indices].nunique()}"
)

print(
    f"Testing files : "
    f"{groups.iloc[test_indices].nunique()}"
)


# =========================================================
# 6. CREATE XGBOOST MODEL
# =========================================================

print("\n==========================================")
print("CREATING XGBOOST MODEL")
print("==========================================")

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


# =========================================================
# 7. TRAIN MODEL
# =========================================================

print("\nTraining started...")

model.fit(
    X_train,
    y_train,
    eval_set=[
        (X_test, y_test)
    ],
    verbose=False
)

print("Training completed.")


# =========================================================
# 8. MAKE PREDICTIONS
# =========================================================

print("\nGenerating predictions...")

predictions = model.predict(
    X_test
)


# =========================================================
# 9. EVALUATION
# =========================================================

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = mean_squared_error(
    y_test,
    predictions
) ** 0.5

r2 = r2_score(
    y_test,
    predictions
)


print("\n==========================================")
print("MODEL RESULTS")
print("==========================================")

print(f"MAE  : {mae:.4f} J")
print(f"RMSE : {rmse:.4f} J")
print(f"R²   : {r2:.4f}")


# =========================================================
# 10. SAVE PREDICTIONS
# =========================================================

results = X_test.copy()

results["actual_energy_j"] = y_test.values

results["predicted_energy_j"] = predictions

results["absolute_error_j"] = (
    abs(
        results["actual_energy_j"]
        -
        results["predicted_energy_j"]
    )
)

prediction_file = (
    OUTPUT_FOLDER
    / "energy_predictions.csv"
)

results.to_csv(
    prediction_file,
    index=False
)


# =========================================================
# 11. SAVE MODEL
# =========================================================

model_file = (
    MODEL_FOLDER
    / "energy_model.json"
)

model.save_model(
    model_file
)


# =========================================================
# 12. SAVE FEATURE INFORMATION
# =========================================================

feature_info = {

    "features": FEATURE_COLUMNS,

    "target": TARGET_COLUMN,

    "training_rows": int(
        len(X_train)
    ),

    "testing_rows": int(
        len(X_test)
    ),

    "training_files": int(
        groups.iloc[train_indices]
        .nunique()
    ),

    "testing_files": int(
        groups.iloc[test_indices]
        .nunique()
    ),

    "MAE_J": float(mae),

    "RMSE_J": float(rmse),

    "R2": float(r2)
}


feature_file = (
    MODEL_FOLDER
    / "energy_model_info.json"
)

with open(
    feature_file,
    "w"
) as file:

    json.dump(
        feature_info,
        file,
        indent=4
    )


# =========================================================
# 13. FINISHED
# =========================================================

print("\n==========================================")
print("FILES CREATED")
print("==========================================")

print(
    f"Model:\n{model_file}"
)

print(
    f"\nPredictions:\n{prediction_file}"
)

print(
    f"\nModel information:\n{feature_file}"
)

print("\nENERGY MODEL TRAINING FINISHED!")