import copy
import random
from fastapi import APIRouter, HTTPException
from backend.optimization.schemas import (
    Options,
    ApplyRequest,
    StepRequest,
    PlanResponse,
)
from backend.optimization.engine import plan, apply, evaluate, predictions, valid
from backend.simulation.engine import SimulationError
from backend.simulation.store import store, SimulationStore

router = APIRouter(prefix="/optimization", tags=["Integrated optimization"])


def guarded(fn):
    try:
        with store.lock:
            return fn()
    except SimulationError as exc:
        raise HTTPException(exc.status_code, str(exc)) from exc


@router.post("/preview", response_model=PlanResponse)
def preview(data: Options):
    return guarded(lambda: plan(store, data))


@router.post("/apply")
def apply_plan(data: ApplyRequest):
    def run():
        def commit():
            before = evaluate(
                {v: x["server_id"] for v, x in store.vms.items() if x["server_id"]},
                store,
                predictions(store),
                data,
            )
            actions = apply(store, data.allocation, data.revision, data)
            after = evaluate(data.allocation, store, predictions(store), data)
            store.events.append(
                {
                    "tick": store.tick,
                    "action": "optimization_result",
                    "strategy": data.strategy,
                    "before": before,
                    "after": after,
                    "moves": actions,
                }
            )
            return actions

        actions = store.mutate("apply_plan", commit)
        return {"state": store.get_state(), "actions": actions}

    return guarded(run)


def comparison(target, options):
    # Fill pending VMs without moving running VMs, ensuring equal served workloads.
    clone = SimulationStore()
    clone._restore(target._document())
    for vid, vm in clone.vms.items():
        if vm["server_id"] is None:
            allocation = {
                v: x["server_id"] for v, x in clone.vms.items() if x["server_id"]
            }
            fits = [
                sid
                for sid in clone.servers
                if valid({**allocation, vid: sid}, clone, False)
            ]
            if not fits:
                raise SimulationError(
                    "Cannot compare identical workloads: pending VM does not fit.", 409
                )
            vm["server_id"] = fits[0]
    rows = []
    for strategy in ("static", "first_fit", "best_fit", "predictive"):
        opt = options.model_copy(update={"strategy": strategy})
        try:
            p = plan(clone, opt)
            rows.append(
                {
                    "strategy": strategy,
                    "status": "ok",
                    "metrics": p["after"],
                    "allocation": p["allocation"],
                }
            )
        except SimulationError as exc:
            rows.append(
                {"strategy": strategy, "status": "infeasible", "reason": str(exc)}
            )
    baseline = rows[0]["metrics"]["total_energy_wh"]
    for row in rows:
        if row["status"] == "ok":
            row["energy_saving_percent"] = (
                100 * (baseline - row["metrics"]["total_energy_wh"]) / baseline
                if baseline
                else 0
            )
    return {
        "rows": rows,
        "interval_minutes": options.interval_minutes,
        "data_source": "simulation",
        "methodology": "Same VM set, demand, server profiles, interval and initial allocation; pending VMs first fitted before all strategies. Migration energy included.",
        "sources": clone.provenance,
        "missing_histories": [v for v in clone.vms if v not in clone.histories],
    }


@router.post("/compare")
def compare(data: Options):
    return guarded(lambda: comparison(store, data))


@router.post("/step")
def step(data: StepRequest):
    def run():
        def advance():
            store.tick += 1
            if data.source == "synthetic":
                rng = random.Random(data.seed + store.tick)
                for vid in store.vms:
                    history = copy.deepcopy(store.histories.get(vid, []))
                    if not history:
                        history = [
                            {
                                "cpu_util_percent": rng.uniform(20, 80),
                                "mem_util_percent": rng.uniform(30, 85),
                                "net_in": 50.0,
                                "net_out": 40.0,
                                "disk_io_percent": 15.0,
                            }
                            for _ in range(4)
                        ]
                    last = dict(history[-1])
                    for col in ("cpu_util_percent", "mem_util_percent"):
                        last[col] = max(
                            0.0, min(100.0, last[col] + rng.uniform(-18, 18))
                        )
                    store.histories[vid] = (history + [last])[-64:]
                    store.provenance[vid] = "synthetic"
            p = plan(store, data)
            actions = (
                apply(store, p["allocation"], store.revision, data)
                if data.strategy != "static"
                else []
            )
            store.events.append(
                {
                    "tick": store.tick,
                    "action": "adaptive_result",
                    "strategy": data.strategy,
                    "source": data.source,
                    "before": p["before"],
                    "after": p["after"],
                    "moves": actions,
                }
            )
            return p

        p = store.mutate("advance_interval", advance)
        return {"state": store.get_state(), "plan": p}

    return guarded(run)


@router.get("/history")
def history():
    with store.lock:
        return {
            "events": copy.deepcopy(store.events),
            "revision": store.revision,
            "tick": store.tick,
        }
