from pathlib import Path
import json

from src.vm_loader import load_vm_data
from src.vm_preprocessing import prepare_vm_data


PROJECT_ROOT = Path(__file__).resolve().parent

VM_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "resource"
    / "vm_cpu_readings_month_aggregated_cpu_mem_no_timestamp.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "vm_resource_analysis.csv"
)

INFO_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "vm_resource_analysis_info.json"
)


(PROJECT_ROOT / "outputs").mkdir(
    exist_ok=True
)


print("\n===================================")
print("PHASE 2C - VM RESOURCE ANALYSIS")
print("===================================")


df = load_vm_data(
    VM_DATA_PATH
)


df = prepare_vm_data(
    df
)


# ------------------------------------------------
# RESOURCE SUMMARY
# ------------------------------------------------

summary = {

    "dataset":
        "vm_cpu_readings_month_aggregated_cpu_mem_no_timestamp.csv",

    "total_rows":
        len(df),

    "cpu_usage_mean":
        float(df["cpu_usage"].mean()),

    "cpu_usage_max":
        float(df["cpu_usage"].max()),

    "assigned_mem_mean":
        float(df["assigned_mem"].mean()),

    "assigned_mem_max":
        float(df["assigned_mem"].max()),

    "cpu_memory_ratio_mean":
        float(
            df["cpu_memory_ratio"].mean()
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
print("VM ANALYSIS COMPLETE")
print("===================================")

print(f"\nRows analyzed: {len(df)}")

print("\nVM resource summary:")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nOutput:")
print(OUTPUT_PATH)

print("\nInformation:")
print(INFO_PATH)