"""Forecast-informed constrained beam search, with conventional baselines.
No policy is claimed to be reinforcement learning. Power/SLA/cost are proxies.
"""

import math
from backend.simulation.engine import SimulationError
from backend.intelligence.service import service


def predictions(store):
    result = {}
    for vid, vm in store.vms.items():
        if vid in store.histories:
            f = service.forecast_vm(vm, store.histories[vid])
            result[vid] = (
                f["predicted_cpu_percent"] / 100,
                f["predicted_memory_percent"] / 100,
            )
        else:
            result[vid] = (1.0, 1.0)  # conservative, disclosed fallback
    return result


def valid(allocation, store, complete=True):
    if complete and set(allocation) != set(store.vms):
        return False
    if set(allocation) - set(store.vms):
        return False
    for sid in allocation.values():
        if sid not in store.servers:
            return False
    for sid, s in store.servers.items():
        group = [store.vms[vid] for vid, target in allocation.items() if target == sid]
        if (
            sum(v["cpu"] for v in group) > s["cpu_capacity"] + 1e-9
            or sum(v["memory"] for v in group) > s["memory_capacity"] + 1e-9
        ):
            return False
    return True


def migration_schedule(allocation, store):
    """Reject cycles without spare capacity; every move fits while source is running."""
    current = {vid: v["server_id"] for vid, v in store.vms.items() if v["server_id"]}
    todo = [vid for vid in allocation if current.get(vid) != allocation[vid]]
    actions = []
    while todo:
        for vid in todo:
            trial = {**current, vid: allocation[vid]}
            if valid(trial, store, complete=False):
                actions.append(
                    {
                        "vm_id": vid,
                        "from_server": current.get(vid),
                        "to_server": allocation[vid],
                        "kind": "migration" if current.get(vid) else "placement",
                    }
                )
                current = trial
                todo.remove(vid)
                break
        else:
            raise SimulationError(
                "Plan requires temporary capacity or a disruptive swap.", 409
            )
    return actions


def evaluate(allocation, store, demand, opt):
    rows = []
    pressure = []
    risk = 0.0
    for sid, s in store.servers.items():
        group = [store.vms[v] for v, target in allocation.items() if target == sid]
        cpu = sum(v["cpu"] * demand[v["id"]][0] for v in group)
        mem = sum(v["memory"] * demand[v["id"]][1] for v in group)
        cu, mu = cpu / s["cpu_capacity"], mem / s["memory_capacity"]
        # RAM pressure contributes to dynamic power; identical profiles are a documented assumption.
        watts = (
            opt.sleep_watts
            if not group
            else opt.idle_watts
            + (opt.peak_watts - opt.idle_watts) * min(1, 0.8 * cu + 0.2 * mu)
        )
        p = max(cu, mu)
        if group:
            pressure.append(p)
            risk += max(0, p + opt.headroom - 0.85) ** 2
        rows.append(
            {
                "server_id": sid,
                "power_w": watts,
                "state": "active" if group else "sleep",
                "cpu_demand": cpu,
                "memory_demand": mem,
                "cpu_pressure_percent": cu * 100,
                "memory_pressure_percent": mu * 100,
                "reserved_cpu": sum(v["cpu"] for v in group),
                "reserved_memory": sum(v["memory"] for v in group),
            }
        )
    moved = [
        v
        for v, sid in allocation.items()
        if store.vms[v]["server_id"] is not None and store.vms[v]["server_id"] != sid
    ]
    migration_gb = sum(store.vms[v]["memory"] for v in moved)
    migration_wh = migration_gb * opt.migration_wh_per_gb
    power = sum(s["power_w"] for s in rows)
    energy = power * opt.interval_minutes / 60
    mean = sum(pressure) / len(pressure) if pressure else 0
    imbalance = sum((p - mean) ** 2 for p in pressure) / max(1, len(pressure))
    missing = len(store.vms) - len(allocation)
    norm = max(1, len(store.servers) * opt.peak_watts * opt.interval_minutes / 60)
    score = (
        opt.energy_weight * (energy + migration_wh) / norm
        + opt.risk_weight * risk / max(1, len(store.servers))
        + opt.balance_weight * imbalance
        + opt.migration_weight
        * migration_gb
        / max(1, sum(v["memory"] for v in store.vms.values()))
        + missing * 100
    )
    return {
        "power_w": power,
        "energy_wh": energy,
        "migration_energy_wh": migration_wh,
        "total_energy_wh": energy + migration_wh,
        "sla_pressure_proxy": risk / max(1, len(store.servers)),
        "imbalance": imbalance,
        "migrations": len(moved),
        "migration_gb": migration_gb,
        "migration_seconds_proxy": migration_gb / 0.125,
        "active_servers": sum(s["state"] == "active" for s in rows),
        "scheduled_vms": len(allocation),
        "unassigned_vms": missing,
        "mean_active_pressure_percent": mean * 100,
        "score": score,
        "servers": rows,
    }


def plan(store, opt, use_forecasts=True):
    if opt.peak_watts < opt.idle_watts or opt.sleep_watts > opt.idle_watts:
        raise SimulationError("Require sleep watts <= idle watts <= peak watts.", 422)
    if len(store.vms) > 80 or len(store.servers) > 40:
        raise SimulationError(
            "Interactive planner supports up to 80 VMs and 40 servers.", 422
        )
    demand = predictions(store) if use_forecasts else {v: (1.0, 1.0) for v in store.vms}
    current = {vid: v["server_id"] for vid, v in store.vms.items() if v["server_id"]}
    before = evaluate(current, store, demand, opt)
    if opt.strategy == "static":
        return result(
            current,
            current,
            store,
            demand,
            opt,
            before,
            "Static allocation; pending VMs remain unassigned.",
        )
    if opt.strategy in ("first_fit", "best_fit"):
        # Repack in insertion order, independent of the predictive scheduler's ranking.
        allocation = {
            vid: sid
            for vid, sid in current.items()
            if store.tick - store.last_migration.get(vid, -10000)
            < opt.cooldown_intervals
        }
        for vid, vm in store.vms.items():
            if vid in allocation:
                continue
            fits = [
                sid
                for sid in store.servers
                if valid({**allocation, vid: sid}, store, False)
            ]
            if not fits:
                raise SimulationError("No full placement found by this heuristic.", 409)
            if opt.strategy == "best_fit":
                fits.sort(
                    key=lambda sid: store.servers[sid]["cpu_capacity"]
                    - sum(
                        store.vms[v]["cpu"] for v, t in allocation.items() if t == sid
                    )
                    - vm["cpu"]
                )
            allocation[vid] = fits[0]
        migration_schedule(allocation, store)
    else:
        fixed = {
            vid: sid
            for vid, sid in current.items()
            if store.tick - store.last_migration.get(vid, -10000)
            < opt.cooldown_intervals
        }
        todo = sorted(
            (vid for vid in store.vms if vid not in fixed),
            key=lambda v: (
                -max(
                    store.vms[v]["cpu"] * demand[v][0],
                    store.vms[v]["memory"] * demand[v][1],
                ),
                v,
            ),
        )
        beams = [fixed]
        for vid in todo:
            expanded = [
                {**a, vid: sid}
                for a in beams
                for sid in store.servers
                if valid({**a, vid: sid}, store, False)
            ]
            if not expanded:
                raise SimulationError(
                    "No feasible full placement found within bounded search/cooldown constraints.",
                    409,
                )
            expanded.sort(
                key=lambda a: (
                    evaluate(a, store, demand, opt)["score"],
                    tuple(sorted(a.items())),
                )
            )
            beams = expanded[: opt.beam_width]
        # Preserve current complete plan if bounded search misses it.
        if valid(current, store):
            beams.append(current)
        feasible = []
        for a in beams:
            try:
                migration_schedule(a, store)
                feasible.append(a)
            except SimulationError:
                pass
        if not feasible:
            raise SimulationError(
                "No sequentially feasible migration schedule found.", 409
            )
        allocation = min(
            feasible, key=lambda a: evaluate(a, store, demand, opt)["score"]
        )
        if (
            valid(current, store)
            and before["score"] - evaluate(allocation, store, demand, opt)["score"]
            < opt.minimum_improvement
        ):
            allocation = current
    return result(
        allocation,
        current,
        store,
        demand,
        opt,
        before,
        "CPU/RAM reservations remain hard constraints; search minimizes forecast-informed normalized objectives.",
    )


def result(allocation, current, store, demand, opt, before, reason):
    after = evaluate(allocation, store, demand, opt)
    return {
        "revision": store.revision,
        "tick": store.tick,
        "strategy": opt.strategy,
        "allocation": allocation,
        "before": before,
        "after": after,
        "actions": migration_schedule(allocation, store),
        "estimated_energy_saving_wh": before["total_energy_wh"]
        - after["total_energy_wh"],
        "comparable_workload": set(current) == set(allocation),
        "missing_histories": [v for v in store.vms if v not in store.histories],
        "explanation": reason,
        "data_source": "simulation",
        "assumptions": opt.model_dump(),
    }


def apply(store, allocation, revision, opt):
    if revision != store.revision:
        raise SimulationError("State changed. Preview again before applying.", 409)
    if not valid(allocation, store):
        raise SimulationError(
            "Full VM coverage and CPU/RAM capacity constraints are required.", 409
        )
    for vid, sid in allocation.items():
        old = store.vms[vid]["server_id"]
        if (
            old
            and old != sid
            and store.tick - store.last_migration.get(vid, -10000)
            < opt.cooldown_intervals
        ):
            raise SimulationError("Migration cooldown is active.", 409)
    actions = migration_schedule(allocation, store)
    for action in actions:
        vid = action["vm_id"]
        if action["kind"] == "migration":
            store.last_migration[vid] = store.tick
        store.vms[vid]["server_id"] = action["to_server"]
    return actions
