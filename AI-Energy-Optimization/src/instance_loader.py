from pathlib import Path
import pandas as pd


def load_instance_data(file_path):
    """
    Loads the instance usage dataset.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Instance dataset not found: {file_path}"
        )

    print("\nLoading instance usage dataset...")
    print(f"File: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(
            "The instance dataset is empty."
        )

    print("\n-----------------------------------")
    print("INSTANCE DATA LOADED")
    print("-----------------------------------")

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    print("\nAvailable columns:")

    for column in df.columns:
        print(f" - {column}")

    return df