"""Paired hypothetical-VM trace replay. No real VM/energy trace correspondence claimed."""

import copy
import csv
import json
import random
from pathlib import Path
import numpy as np
import pandas as pd
from backend.simulation.store import SimulationStore
from backend.optimization.engine import plan, apply, evaluate, valid
from backend.optimization.schemas import Options
from backend.simulation.engine import SimulationError

ROOT = Path(__file__).resolve().parents[1]


def scenario(seed):
    rng = random.Random(seed)
    s = SimulationStore()
    s.servers = {}
    for i, cap in enumerate([16, 16, 8, 16]):
        sid = f"S{i+1}"
        s.servers[sid] = {
            "id": sid,
            "name": sid,
            "cpu_capacity": cap,
            "memory_capacity": cap * 2,
        }
    s.vms = {}
    for i in range(8):
        vid = f"V{i}"
        s.vms[vid] = {
            "id": vid,
            "name": vid,
            "cpu": rng.choice([2.0, 3.0, 4.0]),
            "memory": rng.choice([4.0, 6.0, 8.0]),
            "server_id": f"S{i%4+1}",
        }
    s.validate()
    return s


def main():
    trace = pd.read_csv(
        ROOT / "data/resource/machine_usage_days_1_to_8_grouped_300_seconds.csv"
    )
    rows = []
    for seed in range(10):
        base = scenario(seed)
        for strategy in [
            "static",
            "first_fit",
            "best_fit",
            "predictive",
            "predictive_no_forecast",
        ]:
            s = SimulationStore()
            s._restore(base._document())
            total = 0.0
            migration = 0
            pressure = 0.0
            moves = 0
            failures = 0
            for t in range(8):
                s.tick = t
                actual = {}
                for i, vid in enumerate(s.vms):
                    # All segments are from the untouched file-order test block.
                    index = 1810 + seed * 7 + i * 13 + t
                    readings = trace.iloc[index - 3 : index + 1].to_dict("records")
                    s.histories[vid] = readings
                    s.provenance[vid] = "aggregate-trace-derived hypothetical VM"
                    nxt = trace.iloc[index + 1]
                    actual[vid] = (
                        float(nxt["cpu_util_percent"]) / 100,
                        float(nxt["mem_util_percent"]) / 100,
                    )
                opt = Options(
                    strategy=(
                        "predictive"
                        if strategy == "predictive_no_forecast"
                        else strategy
                    )
                )
                try:
                    p = plan(s, opt, use_forecasts=strategy != "predictive_no_forecast")
                    allocation = p["allocation"]
                    assert valid(allocation, s)
                    measured_proxy = evaluate(allocation, s, actual, opt)
                    total += measured_proxy["total_energy_wh"]
                    migration += measured_proxy["migration_energy_wh"]
                    pressure += measured_proxy["sla_pressure_proxy"]
                    moves += measured_proxy["migrations"]
                    if strategy != "static":
                        apply(s, allocation, s.revision, opt)
                except SimulationError:
                    failures += 1
                    allocation = {v: vm["server_id"] for v, vm in s.vms.items()}
                    measured_proxy = evaluate(allocation, s, actual, opt)
                    total += measured_proxy["total_energy_wh"]
                    pressure += measured_proxy["sla_pressure_proxy"]
            rows.append(
                {
                    "seed": seed,
                    "strategy": strategy,
                    "intervals": 8,
                    "total_energy_wh": total,
                    "migration_energy_wh": migration,
                    "migrations": moves,
                    "mean_pressure_proxy": pressure / 8,
                    "failed_reoptimizations": failures,
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "experiments/paired_results.csv", index=False)
    summary = {}
    static = df[df.strategy == "static"].set_index("seed").total_energy_wh
    for strategy, g in df.groupby("strategy"):
        savings = (static - g.set_index("seed").total_energy_wh) / static * 100
        summary[strategy] = {
            "mean_total_energy_wh": float(g.total_energy_wh.mean()),
            "mean_energy_saving_percent_vs_static": float(savings.mean()),
            "saving_stddev_percent": float(savings.std()),
            "mean_migrations": float(g.migrations.mean()),
            "mean_pressure_proxy": float(g.mean_pressure_proxy.mean()),
            "failed_reoptimizations": int(g.failed_reoptimizations.sum()),
        }
    result = {
        "method": "10 paired seeds, 4 servers, 8 hypothetical VMs, 8 five-minute intervals per seed. Held-out aggregate segments mapped to hypothetical VMs. Evaluate next-row demand with analytical power; migration energy included.",
        "limitations": [
            "No actual per-VM timestamps/identity",
            "Power and SLA are proxies",
            "Small synthetic topology",
            "No base-paper reproduction",
            "No confidence claim from correlated aggregate segments",
        ],
        "summary": summary,
    }
    (ROOT / "experiments/summary.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
