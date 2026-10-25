from pathlib import Path
import pandas as pd


def load_workload_data(file_path):
    """
    Loads the resource/workload dataset.

    Returns:
        DataFrame containing workload data.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Workload dataset not found: {file_path}"
        )

    print("\nLoading workload dataset...")
    print(f"File: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(
            "The workload dataset is empty."
        )

    print("\n-----------------------------------")
    print("WORKLOAD DATA LOADED")
    print("-----------------------------------")

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    print("\nAvailable columns:")
    for column in df.columns:
        print(f" - {column}")

    return df