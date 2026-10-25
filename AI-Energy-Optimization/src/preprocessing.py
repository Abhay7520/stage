import pandas as pd


# ---------------------------------------------------------
# Columns required by our energy model
# ---------------------------------------------------------

FEATURE_COLUMNS = [
    "cpu_mean",
    "cpu_max",
    "cpu_min",
    "cpu_std",
    "cpu_median",
    "cpu_frequency_ghz",
    "memory_util_gb",
    "sda_write_count_during_interval",
    "sda_read_count_during_interval"
]

TARGET_COLUMN = "energy_util_during_interval_j"


# ---------------------------------------------------------
# Prepare dataset
# ---------------------------------------------------------

def prepare_energy_data(df):

    print("\nChecking dataset columns...")

    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "\nMissing columns:\n"
            + "\n".join(missing_columns)
            + "\n\nAvailable columns:\n"
            + "\n".join(df.columns)
        )

    # Keep only columns needed for training + source file
    columns_to_keep = required_columns + ["source_file"]

    df = df[columns_to_keep].copy()

    # Convert everything except source_file to numeric
    for column in required_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Replace infinity with NaN
    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    print("\nMissing values before cleaning:")

    print(
        df[required_columns]
        .isnull()
        .sum()
    )

    # Remove rows where any required value is missing
    df = df.dropna(
        subset=required_columns
    )

    # Energy cannot be negative
    df = df[
        df[TARGET_COLUMN] >= 0
    ]

    # CPU and memory shouldn't be negative
    df = df[
        df["cpu_mean"] >= 0
    ]

    df = df[
        df["memory_util_gb"] >= 0
    ]

    df = df.reset_index(drop=True)

    print("\n-----------------------------------")
    print("PREPROCESSING COMPLETE")
    print("-----------------------------------")

    print(f"Rows after cleaning: {len(df)}")

    return df