import pandas as pd
from xgboost import XGBRegressor

from backend.config import ENERGY_MODEL_PATH, WORKLOAD_MODEL_PATH

from src.optimization import generate_cpu_candidates, select_best_allocation


class ModelService:

    def __init__(self):

        print("\nLoading AI models...")

        self.energy_model = XGBRegressor()

        self.energy_model.load_model(ENERGY_MODEL_PATH)

        print("Energy model loaded.")

        self.workload_model = XGBRegressor()

        self.workload_model.load_model(WORKLOAD_MODEL_PATH)

        print("Workload model loaded.")

        print("All AI models loaded successfully.")

    # -----------------------------------------
    # WORKLOAD PREDICTION
    # -----------------------------------------

    def predict_workload(self, history):

        if len(history) < 4:

            raise ValueError("At least 4 resource records are required.")

        rows = []

        for item in history:

            rows.append(
                {
                    "cpu_util_percent": item.cpu_util_percent,
                    "mem_util_percent": item.mem_util_percent,
                    "net_in": item.net_in,
                    "net_out": item.net_out,
                    "disk_io_percent": item.disk_io_percent,
                }
            )

        df = pd.DataFrame(rows)

        resource_columns = [
            "cpu_util_percent",
            "mem_util_percent",
            "net_in",
            "net_out",
            "disk_io_percent",
        ]

        features = {}

        # Current values
        current_row = df.iloc[-1]

        for column in resource_columns:

            features[column] = current_row[column]

        # Lag values
        for column in resource_columns:

            for lag in [1, 2, 3]:

                features[f"{column}_lag_{lag}"] = df.iloc[-(lag + 1)][column]

        feature_order = resource_columns + [
            f"{column}_lag_{lag}" for column in resource_columns for lag in [1, 2, 3]
        ]

        X = pd.DataFrame(
            [[features[column] for column in feature_order]], columns=feature_order
        )

        prediction = float(self.workload_model.predict(X)[0])

        prediction = max(0, min(100, prediction))

        return prediction

    # -----------------------------------------
    # ENERGY PREDICTION
    # -----------------------------------------

    def predict_energy(self, data):

        feature_order = [
            "cpu_mean",
            "cpu_max",
            "cpu_min",
            "cpu_std",
            "cpu_median",
            "cpu_frequency_ghz",
            "memory_util_gb",
            "sda_write_count_during_interval",
            "sda_read_count_during_interval",
        ]

        X = pd.DataFrame(
            [
                [
                    data.cpu_mean,
                    data.cpu_max,
                    data.cpu_min,
                    data.cpu_std,
                    data.cpu_median,
                    data.cpu_frequency_ghz,
                    data.memory_util_gb,
                    data.sda_write_count_during_interval,
                    data.sda_read_count_during_interval,
                ]
            ],
            columns=feature_order,
        )

        prediction = float(self.energy_model.predict(X)[0])

        return max(0, prediction)

    # -----------------------------------------
    # RESOURCE OPTIMIZATION
    # -----------------------------------------

    def optimize_resources(self, data):

        current_cpu = data.current_cpu

        predicted_workload = data.predicted_workload

        base_features = {
            "cpu_mean": current_cpu,
            "cpu_max": current_cpu,
            "cpu_min": current_cpu,
            "cpu_std": 0.0,
            "cpu_median": current_cpu,
            "cpu_frequency_ghz": data.cpu_frequency_ghz,
            "memory_util_gb": data.memory_util_gb,
            "sda_write_count_during_interval": data.sda_write_count_during_interval,
            "sda_read_count_during_interval": data.sda_read_count_during_interval,
        }

        candidates = generate_cpu_candidates(current_cpu, predicted_workload)

        candidate_results, best = select_best_allocation(
            candidates, predicted_workload, self.energy_model, base_features
        )

        # Current energy
        current_energy = self.predict_energy_from_values(current_cpu, base_features)

        optimized_energy = float(best["predicted_energy"])

        energy_saving = current_energy - optimized_energy

        if current_energy != 0:

            energy_saving_percent = (energy_saving / current_energy) * 100

        else:

            energy_saving_percent = 0

        return {
            "current_cpu": current_cpu,
            "predicted_workload": predicted_workload,
            "recommended_cpu": float(best["cpu_allocation"]),
            "current_predicted_energy": current_energy,
            "optimized_predicted_energy": optimized_energy,
            "estimated_energy_saving": energy_saving,
            "estimated_energy_saving_percent": energy_saving_percent,
            "optimization_score": float(best["optimization_score"]),
            "candidate_allocations": candidate_results.to_dict(orient="records"),
        }

    def predict_energy_from_values(self, cpu_value, base_features):

        feature_order = [
            "cpu_mean",
            "cpu_max",
            "cpu_min",
            "cpu_std",
            "cpu_median",
            "cpu_frequency_ghz",
            "memory_util_gb",
            "sda_write_count_during_interval",
            "sda_read_count_during_interval",
        ]

        X = pd.DataFrame(
            [
                [
                    cpu_value,
                    cpu_value,
                    cpu_value,
                    0.0,
                    cpu_value,
                    base_features["cpu_frequency_ghz"],
                    base_features["memory_util_gb"],
                    base_features["sda_write_count_during_interval"],
                    base_features["sda_read_count_during_interval"],
                ]
            ],
            columns=feature_order,
        )

        prediction = float(self.energy_model.predict(X)[0])

        return max(0, prediction)
