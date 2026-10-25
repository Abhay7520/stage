from pathlib import Path

from src.resource_optimizer import (
    optimize_resources
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent


ENERGY_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "energy_model.json"
)


WORKLOAD_PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "workload_predictions.csv"
)


ENERGY_PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "energy_predictions.csv"
)


OUTPUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "optimization_results.csv"
)


# ============================================================
# RUN OPTIMIZATION
# ============================================================

print("\n===================================")
print("PHASE 3 - RESOURCE OPTIMIZATION")
print("===================================")


optimize_resources(

    energy_model_path=
        ENERGY_MODEL_PATH,

    workload_predictions_path=
        WORKLOAD_PREDICTIONS_PATH,

    energy_predictions_path=
        ENERGY_PREDICTIONS_PATH,

    output_path=
        OUTPUT_PATH
)


print("\n===================================")
print("PHASE 3 FINISHED!")
print("===================================")