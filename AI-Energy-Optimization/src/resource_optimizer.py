from pathlib import Path

import pandas as pd
from xgboost import XGBRegressor

from src.optimization import (
    generate_cpu_candidates,
    select_best_allocation
)


def load_energy_model(model_path):

    model = XGBRegressor()

    model.load_model(
        model_path
    )

    return model


def load_workload_predictions(
    prediction_path
):

    df = pd.read_csv(
        prediction_path
    )

    required_columns = [
        "actual_cpu_util_percent",
        "predicted_cpu_util_percent"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing workload prediction columns:\n"
            + "\n".join(missing)
        )

    return df


def load_energy_features(
    energy_prediction_path
):

    df = pd.read_csv(
        energy_prediction_path
    )

    return df


def optimize_resources(
    energy_model_path,
    workload_predictions_path,
    energy_predictions_path,
    output_path
):

    print("\n===================================")
    print("RESOURCE OPTIMIZATION ENGINE")
    print("===================================")

    # ------------------------------------------------
    # LOAD MODELS / DATA
    # ------------------------------------------------

    print("\nLoading energy model...")

    energy_model = load_energy_model(
        energy_model_path
    )

    print("Energy model loaded.")

    print("\nLoading workload predictions...")

    workload_df = load_workload_predictions(
        workload_predictions_path
    )

    print(
        f"Workload predictions loaded: "
        f"{len(workload_df)} rows"
    )

    print("\nLoading energy prediction data...")

    energy_df = load_energy_features(
        energy_predictions_path
    )

    print(
        f"Energy data loaded: "
        f"{len(energy_df)} rows"
    )

    # ------------------------------------------------
    # USE A SAMPLE OF TEST CASES
    # ------------------------------------------------

    number_of_cases = min(
        100,
        len(workload_df),
        len(energy_df)
    )

    workload_df = workload_df.iloc[
        :number_of_cases
    ].reset_index(drop=True)

    energy_df = energy_df.iloc[
        :number_of_cases
    ].reset_index(drop=True)

    results = []

    # ------------------------------------------------
    # OPTIMIZATION LOOP
    # ------------------------------------------------

    for i in range(number_of_cases):

        predicted_workload = float(
            workload_df.loc[
                i,
                "predicted_cpu_util_percent"
            ]
        )

        # Use actual CPU as current allocation
        current_cpu = float(
            workload_df.loc[
                i,
                "actual_cpu_util_percent"
            ]
        )

        # ------------------------------------------------
        # ENERGY MODEL BASE FEATURES
        # ------------------------------------------------

        energy_row = energy_df.iloc[i]

        base_features = {

            "cpu_mean":
                current_cpu,

            "cpu_max":
                current_cpu,

            "cpu_min":
                current_cpu,

            "cpu_std":
                0.0,

            "cpu_median":
                current_cpu,

            "cpu_frequency_ghz":
                float(
                    energy_row[
                        "cpu_frequency_ghz"
                    ]
                ),

            "memory_util_gb":
                float(
                    energy_row[
                        "memory_util_gb"
                    ]
                ),

            "sda_write_count_during_interval":
                float(
                    energy_row[
                        "sda_write_count_during_interval"
                    ]
                ),

            "sda_read_count_during_interval":
                float(
                    energy_row[
                        "sda_read_count_during_interval"
                    ]
                )
        }

        # ------------------------------------------------
        # GENERATE CANDIDATES
        # ------------------------------------------------

        candidates = generate_cpu_candidates(
            current_cpu,
            predicted_workload
        )

        # ------------------------------------------------
        # SELECT BEST
        # ------------------------------------------------

        candidate_results, best = (
            select_best_allocation(
                candidates,
                predicted_workload,
                energy_model,
                base_features
            )
        )

        current_energy = float(
            energy_model.predict(
                pd.DataFrame(
                    [[
                        current_cpu,
                        current_cpu,
                        current_cpu,
                        0.0,
                        current_cpu,
                        base_features[
                            "cpu_frequency_ghz"
                        ],
                        base_features[
                            "memory_util_gb"
                        ],
                        base_features[
                            "sda_write_count_during_interval"
                        ],
                        base_features[
                            "sda_read_count_during_interval"
                        ]
                    ]],
                    columns=[
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
                )
            )[0]
        )

        optimized_energy = float(
            best["predicted_energy"]
        )

        energy_saving = (
            current_energy
            - optimized_energy
        )

        if current_energy != 0:

            energy_saving_percent = (
                energy_saving
                / current_energy
            ) * 100

        else:

            energy_saving_percent = 0

        results.append({

            "case":
                i + 1,

            "current_cpu":
                current_cpu,

            "predicted_workload":
                predicted_workload,

            "recommended_cpu":
                float(
                    best["cpu_allocation"]
                ),

            "current_predicted_energy":
                current_energy,

            "optimized_predicted_energy":
                optimized_energy,

            "estimated_energy_saving":
                energy_saving,

            "estimated_energy_saving_percent":
                energy_saving_percent,

            "optimization_score":
                float(
                    best["optimization_score"]
                )
        })

    result_df = pd.DataFrame(
        results
    )

    result_df.to_csv(
        output_path,
        index=False
    )

    print("\n===================================")
    print("OPTIMIZATION COMPLETE")
    print("===================================")

    print(
        f"\nCases optimized: "
        f"{len(result_df)}"
    )

    print(
        f"\nAverage current energy: "
        f"{result_df['current_predicted_energy'].mean():.4f} J"
    )

    print(
        f"Average optimized energy: "
        f"{result_df['optimized_predicted_energy'].mean():.4f} J"
    )

    print(
        f"Average estimated saving: "
        f"{result_df['estimated_energy_saving'].mean():.4f} J"
    )

    print(
        f"Average estimated saving percentage: "
        f"{result_df['estimated_energy_saving_percent'].mean():.2f}%"
    )

    print(
        f"\nResults saved to:\n"
        f"{output_path}"
    )

    return result_df