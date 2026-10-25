import pandas as pd


INSTANCE_COLUMNS = [
    "avg_cpu",
    "avg_mem",
    "avg_assigned_mem",
    "avg_cycles_per_instruction"
]


def prepare_instance_data(df):

    print("\nChecking instance dataset columns...")

    missing_columns = [
        column
        for column in INSTANCE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "\nMissing columns:\n"
            + "\n".join(missing_columns)
            + "\n\nAvailable columns:\n"
            + "\n".join(df.columns)
        )

    df = df[INSTANCE_COLUMNS].copy()

    # Convert to numeric
    for column in INSTANCE_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Replace infinity
    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    print("\nMissing values before cleaning:")
    print(df.isnull().sum())

    # Remove missing values
    df = df.dropna(
        subset=INSTANCE_COLUMNS
    )

    # Remove invalid negative values
    df = df[
        df["avg_cpu"] >= 0
    ]

    df = df[
        df["avg_mem"] >= 0
    ]

    df = df[
        df["avg_assigned_mem"] >= 0
    ]

    df = df[
        df["avg_cycles_per_instruction"] >= 0
    ]

    df = df.reset_index(drop=True)

    # ------------------------------------------------
    # CREATE RESOURCE PRESSURE INDICATORS
    # ------------------------------------------------

    # Memory utilization relative to assigned memory
    df["memory_usage_ratio"] = (
        df["avg_mem"]
        /
        df["avg_assigned_mem"].replace(0, pd.NA)
    )

    # CPU / memory relationship
    df["cpu_memory_ratio"] = (
        df["avg_cpu"]
        /
        df["avg_mem"].replace(0, pd.NA)
    )

    # Remove invalid generated values
    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    df = df.dropna()

    df = df.reset_index(drop=True)

    print("\n-----------------------------------")
    print("INSTANCE PREPROCESSING COMPLETE")
    print("-----------------------------------")

    print(f"Rows after cleaning: {len(df)}")

    print("\nGenerated resource indicators:")
    print(" - memory_usage_ratio")
    print(" - cpu_memory_ratio")

    return df