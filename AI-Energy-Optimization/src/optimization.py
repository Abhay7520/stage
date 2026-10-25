import numpy as np
import pandas as pd


def calculate_optimization_score(
    predicted_energy,
    cpu_allocation,
    predicted_workload
):
    """
    Calculates a score for a resource allocation.

    Lower score is better.

    Energy is the primary objective.
    A penalty is added when CPU allocation
    is below predicted workload.
    """

    workload_gap = max(
        0,
        predicted_workload - cpu_allocation
    )

    performance_penalty = (
        workload_gap * 10
    )

    score = (
        predicted_energy
        + performance_penalty
    )

    return score


def generate_cpu_candidates(
    current_cpu,
    predicted_workload
):
    """
    Generates possible CPU allocations.

    The optimizer considers allocations around
    the predicted workload.
    """

    candidates = set()

    # Around current allocation
    for change in [-20, -15, -10, -5, 0, 5, 10, 15, 20]:
        value = current_cpu + change

        if 0 <= value <= 100:
            candidates.add(round(value, 2))

    # Around predicted workload
    for margin in [-10, -5, 0, 5, 10, 15, 20]:
        value = predicted_workload + margin

        if 0 <= value <= 100:
            candidates.add(round(value, 2))

    return sorted(candidates)


def select_best_allocation(
    candidates,
    predicted_workload,
    energy_model,
    base_features
):
    """
    Evaluates all candidate CPU allocations and
    selects the lowest-scoring feasible option.
    """

    results = []

    for cpu_allocation in candidates:

        features = base_features.copy()

        features["cpu_mean"] = cpu_allocation

        features["cpu_max"] = cpu_allocation

        features["cpu_min"] = cpu_allocation

        features["cpu_median"] = cpu_allocation

        features["cpu_std"] = 0.0

        feature_order = [
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

        X = pd.DataFrame(
            [[features[column] for column in feature_order]],
            columns=feature_order
        )

        predicted_energy = float(
            energy_model.predict(X)[0]
        )

        score = calculate_optimization_score(
            predicted_energy,
            cpu_allocation,
            predicted_workload
        )

        feasible = (
            cpu_allocation >= predicted_workload
        )

        results.append({
            "cpu_allocation": cpu_allocation,
            "predicted_energy": predicted_energy,
            "optimization_score": score,
            "feasible": feasible
        })

    result_df = pd.DataFrame(results)

    feasible_df = result_df[
        result_df["feasible"] == True
    ]

    if feasible_df.empty:

        # If no feasible allocation exists,
        # select the highest available allocation.
        best_row = result_df.loc[
            result_df["cpu_allocation"].idxmax()
        ]

    else:

        best_row = feasible_df.loc[
            feasible_df["optimization_score"].idxmin()
        ]

    return result_df, best_row