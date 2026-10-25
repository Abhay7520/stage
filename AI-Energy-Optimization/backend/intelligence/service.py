"""Shared feature contract for CPU and RAM models. No implicit example histories."""

import json
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from backend.config import MODELS_DIR

RESOURCE_COLUMNS = [
    "cpu_util_percent",
    "mem_util_percent",
    "net_in",
    "net_out",
    "disk_io_percent",
]
FEATURE_COLUMNS = RESOURCE_COLUMNS + [
    f"{c}_lag_{lag}" for c in RESOURCE_COLUMNS for lag in (1, 2, 3)
]


def build_features(history):
    if len(history) < 4:
        raise ValueError("At least four ordered observations are required.")
    rows = [
        (
            r.model_dump()
            if hasattr(r, "model_dump")
            else (r if isinstance(r, dict) else vars(r))
        )
        for r in history[-4:]
    ]
    x = [rows[-1][c] for c in RESOURCE_COLUMNS] + [
        rows[-1 - lag][c] for c in RESOURCE_COLUMNS for lag in (1, 2, 3)
    ]
    if not np.isfinite(x).all():
        raise ValueError("Resource values must be finite.")
    return pd.DataFrame([x], columns=FEATURE_COLUMNS)


class IntelligenceService:
    def __init__(self, cpu_model=None, memory_model=None, strategy=None):
        self.models = {}
        self.strategies = {}
        for key, supplied in [("cpu", cpu_model), ("memory", memory_model)]:
            path = MODELS_DIR / f"{key}_forecast.json"
            info_path = MODELS_DIR / "forecast_evaluation.json"
            info = json.loads(info_path.read_text()) if info_path.exists() else {}
            choice = strategy or info.get(key, {}).get("selected", "persistence")
            self.strategies[key] = choice
            if supplied is not None:
                self.models[key] = supplied
            elif choice == "xgboost" and path.exists():
                model = XGBRegressor(n_jobs=1)
                model.load_model(path)
                self.models[key] = model
            else:
                self.strategies[key] = "persistence"
                self.models[key] = None

    def forecast_vm(self, vm, history):
        X = build_features(history)
        values = {}
        for key, col in [("cpu", "cpu_util_percent"), ("memory", "mem_util_percent")]:
            model = self.models[key]
            pred = (
                model.predict(X)[0]
                if model is not None and self.strategies[key] != "persistence"
                else X[col].iloc[0]
            )
            values[key] = float(np.clip(pred, 0, 100))
        risks = [f"{key.upper()} high" for key in values if values[key] >= 85]
        return {
            "vm_id": vm["id"],
            "vm_name": vm["name"],
            "server_id": vm["server_id"],
            "predicted_cpu_percent": values["cpu"],
            "predicted_memory_percent": values["memory"],
            "estimated_cpu_demand_vcpu": vm["cpu"] * values["cpu"] / 100,
            "estimated_memory_demand_gb": vm["memory"] * values["memory"] / 100,
            "allocated_vcpu": vm["cpu"],
            "allocated_memory_gb": vm["memory"],
            "resource_risk": ", ".join(risks) or "Normal",
            "cpu_strategy": self.strategies["cpu"],
            "memory_strategy": self.strategies["memory"],
        }

    def server_summaries(self, state, forecasts):
        by_id = {f["vm_id"]: f for f in forecasts}
        rows = []
        for s in state["servers"]:
            vms = s["vms"]
            complete = all(v["id"] in by_id for v in vms)
            cpu = sum(
                by_id[v["id"]]["estimated_cpu_demand_vcpu"]
                for v in vms
                if v["id"] in by_id
            )
            mem = sum(
                by_id[v["id"]]["estimated_memory_demand_gb"]
                for v in vms
                if v["id"] in by_id
            )
            rows.append(
                {
                    "server_id": s["id"],
                    "server_name": s["name"],
                    "complete": complete,
                    "predicted_cpu_demand_vcpu": cpu,
                    "predicted_memory_demand_gb": mem,
                    "predicted_cpu_percent": cpu / s["cpu_capacity"] * 100,
                    "predicted_memory_percent": mem / s["memory_capacity"] * 100,
                }
            )
        return rows


service = IntelligenceService()
