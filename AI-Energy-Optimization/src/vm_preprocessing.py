import pandas as pd


VM_COLUMNS = [
    "cpu_usage",
    "assigned_mem"
]


def prepare_vm_data(df):

    print("\nChecking VM dataset columns...")

    missing_columns = [
        column
        for column in VM_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "\nMissing columns:\n"
            + "\n".join(missing_columns)
            + "\n\nAvailable columns:\n"
            + "\n".join(df.columns)
        )

    df = df[VM_COLUMNS].copy()

    # Convert to numeric
    for column in VM_COLUMNS:
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
        subset=VM_COLUMNS
    )

    # Remove invalid values
    df = df[
        df["cpu_usage"] >= 0
    ]

    df = df[
        df["assigned_mem"] >= 0
    ]

    df = df.reset_index(drop=True)

    # ------------------------------------------------
    # CREATE RESOURCE INDICATORS
    # ------------------------------------------------

    # CPU demand per unit of assigned memory
    df["cpu_memory_ratio"] = (
        df["cpu_usage"]
        /
        df["assigned_mem"].replace(
            0,
            pd.NA
        )
    )

    # Handle invalid ratios
    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    df = df.dropna()

    df = df.reset_index(drop=True)

    print("\n-----------------------------------")
    print("VM PREPROCESSING COMPLETE")
    print("-----------------------------------")

    print(f"Rows after cleaning: {len(df)}")

    print("\nGenerated resource indicator:")
    print(" - cpu_memory_ratio")

    return df