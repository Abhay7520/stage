from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Load all CSV files from a folder recursively
# ---------------------------------------------------------
def load_energy_files(base_folder):
    """
    Reads all CSV files inside the SWEAT preprocessed folder.

    Returns:
        combined_df: all valid rows
        file_count: number of files successfully loaded
    """

    base_path = Path(base_folder)

    if not base_path.exists():
        raise FileNotFoundError(
            f"Energy dataset folder not found: {base_folder}"
        )

    csv_files = list(base_path.rglob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found inside: {base_folder}"
        )

    dataframes = []

    print(f"\nFound {len(csv_files)} CSV files.\n")

    for file_path in csv_files:

        try:
            df = pd.read_csv(file_path)

            if df.empty:
                print(f"Skipping empty file: {file_path}")
                continue

            # Add the source filename.
            # This is important because we don't want to randomly
            # split rows from the same experimental run.
            df["source_file"] = str(file_path)

            dataframes.append(df)

            print(
                f"Loaded: {file_path} | "
                f"Rows: {len(df)}"
            )

        except Exception as e:

            print(
                f"Could not read {file_path}: {e}"
            )

    if not dataframes:
        raise ValueError("No usable CSV files were loaded.")

    combined_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    print("\n-----------------------------------")
    print("DATA LOADING COMPLETE")
    print("-----------------------------------")
    print(f"Total rows: {len(combined_df)}")
    print(f"Total columns: {len(combined_df.columns)}")

    return combined_df, len(dataframes)