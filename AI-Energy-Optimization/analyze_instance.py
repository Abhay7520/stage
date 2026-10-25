from pathlib import Path
import json

from src.instance_loader import load_instance_data
from src.instance_preprocessing import prepare_instance_data


PROJECT_ROOT = Path(__file__).resolve().parent

INSTANCE_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "resource"
    / "instance_usage_grouped_300_seconds_month.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "instance_resource_analysis.csv"
)

INFO_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "instance_resource_analysis_info.json"
)


(PROJECT_ROOT / "outputs").mkdir(
    exist_ok=True
)


print("\n===================================")
print("PHASE 2B - INSTANCE USAGE ANALYSIS")
print("===================================")


df = load_instance_data(
    INSTANCE_DATA_PATH
)


df = prepare_instance_data(
    df
)


# ------------------------------------------------
# RESOURCE SUMMARY
# ------------------------------------------------

summary = {

    "dataset":
        "instance_usage_grouped_300_seconds_month.csv",

    "total_rows":
        len(df),

    "avg_cpu_mean":
        float(df["avg_cpu"].mean()),

    "avg_cpu_max":
        float(df["avg_cpu"].max()),

    "avg_mem_mean":
        float(df["avg_mem"].mean()),

    "avg_assigned_mem_mean":
        float(df["avg_assigned_mem"].mean()),

    "avg_cycles_per_instruction_mean":
        float(
            df["avg_cycles_per_instruction"].mean()
        ),

    "memory_usage_ratio_mean":
        float(
            df["memory_usage_ratio"].mean()
        )
}


# ------------------------------------------------
# SAVE DATA
# ------------------------------------------------

df.to_csv(
    OUTPUT_PATH,
    index=False
)


with open(
    INFO_PATH,
    "w"
) as file:

    json.dump(
        summary,
        file,
        indent=4
    )


print("\n===================================")
print("INSTANCE ANALYSIS COMPLETE")
print("===================================")

print(f"\nRows analyzed: {len(df)}")

print("\nResource summary:")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nOutput:")
print(OUTPUT_PATH)

print("\nInformation:")
print(INFO_PATH)