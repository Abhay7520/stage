import pandas as pd


RESOURCE_COLUMNS = [
    "cpu_util_percent",
    "mem_util_percent",
    "net_in",
    "net_out",
    "disk_io_percent"
]

TARGET_COLUMN = "next_cpu_util_percent"


def prepare_workload_data(df):

    print("\nChecking workload dataset columns...")

    missing_columns = [
        column
        for column in RESOURCE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "\nMissing columns:\n"
            + "\n".join(missing_columns)
            + "\n\nAvailable columns:\n"
            + "\n".join(df.columns)
        )

    # Keep only required resource columns
    df = df[RESOURCE_COLUMNS].copy()

    # Convert everything to numeric
    for column in RESOURCE_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Replace infinite values
    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    print("\nMissing values before cleaning:")
    print(df.isnull().sum())

    # Remove rows with missing values
    df = df.dropna(
        subset=RESOURCE_COLUMNS
    )

    # Remove obviously invalid values
    df = df[
        df["cpu_util_percent"] >= 0
    ]

    df = df[
        df["mem_util_percent"] >= 0
    ]

    df = df[
        df["net_in"] >= 0
    ]

    df = df[
        df["net_out"] >= 0
    ]

    # Disk data can contain -1 / 101 as documented
    # Remove those abnormal values
    df = df[
        (df["disk_io_percent"] >= 0)
        & (df["disk_io_percent"] <= 100)
    ]

    df = df.reset_index(drop=True)

    print("\nRows after basic cleaning:")
    print(len(df))

    # ------------------------------------------------
    # CREATE HISTORICAL FEATURES
    # ------------------------------------------------

    lag_features = []

    for column in RESOURCE_COLUMNS:

        for lag in [1, 2, 3]:

            feature_name = f"{column}_lag_{lag}"

            df[feature_name] = df[column].shift(lag)

            lag_features.append(feature_name)

    # ------------------------------------------------
    # CREATE TARGET
    # ------------------------------------------------

    # Next time-step CPU utilization
    df[TARGET_COLUMN] = (
        df["cpu_util_percent"].shift(-1)
    )

    # Remove rows created by lag/target shifting
    df = df.dropna()

    df = df.reset_index(drop=True)

    print("\n-----------------------------------")
    print("WORKLOAD PREPROCESSING COMPLETE")
    print("-----------------------------------")

    print(f"Rows after lag creation: {len(df)}")

    print("\nTarget:")
    print(f" - {TARGET_COLUMN}")

    print("\nLag features created:")
    for feature in lag_features:
        print(f" - {feature}")

    return df, lag_features