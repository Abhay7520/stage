# API documentation

Base URL: `http://127.0.0.1:8000`. Interactive schemas and requests: <http://127.0.0.1:8000/docs>. OpenAPI JSON is also included at `experiments/openapi.json`.

## Existing compatible endpoints

| Method | Path | Behavior |
|---|---|---|
| GET | `/` | Service status |
| GET | `/health` | Loaded original model status and selected CPU/RAM forecast strategies |
| POST | `/predict/workload` | Original CPU regressor; body `{"history": [ResourceData, ...]}` with 4–64 observations |
| POST | `/predict/energy` | SWEAT-based energy regressor, joules per source measurement interval |
| POST | `/optimize` | Original single-host CPU-input scenario search; exploratory, not validated CPU control |
| GET | `/simulation/state` | Servers, VMs, reservations, metrics, revision and tick |
| GET | `/simulation/metrics` | Reservation metrics |
| POST | `/simulation/reset` | Reset demonstration topology and clear saved workload/history |
| POST | `/simulation/servers` | Create server; `id`, `name`, `cpu_capacity`, `memory_capacity` |
| POST | `/simulation/vms` | Create pending VM; `id`, `name`, `cpu`, `memory` |
| POST | `/simulation/allocate` | Allocate pending VM; `vm_id`, `server_id` |
| POST | `/simulation/migrate` | Migrate assigned VM; same request fields |

Identifiers for creation use letters, digits, `_` or `-`. Capacities and reservations must be positive finite numbers. Memory and vCPU reservations are independent hard constraints. Manual migrations update the optimizer cooldown history.

## Integrated endpoints

| Method | Path | Behavior |
|---|---|---|
| GET | `/intelligence/histories` | Saved readings and their provenance |
| POST | `/intelligence/forecast` | Validate/save histories and forecast all saved VMs |
| GET | `/intelligence/forecasts` | Forecast saved histories without mutation; missing VMs explicit |
| POST | `/optimization/preview` | Read-only full plan, revision, actions, before/after estimates and assumptions |
| POST | `/optimization/apply` | Apply a complete, feasible, revision-matched plan in one persistent transaction |
| POST | `/optimization/compare` | Static, first fit, best fit and predictive results for equal served workload |
| POST | `/optimization/step` | Advance interval, optionally append synthetic readings, plan/apply, record decision |
| GET | `/optimization/history` | Saved operations, before/after metrics and moves |
| GET | `/reports/evaluation` | CPU/RAM and energy evaluation artifacts |
| GET | `/reports/snapshot` | JSON state, history, model evidence, current comparison and limits |
| GET | `/reports/comparison.csv` | Download equal-workload comparison CSV |

## Examples

Create a server:

```json
{"id":"S4","name":"Research Server","cpu_capacity":16,"memory_capacity":32}
```

Save VM history (oldest first; raw network-unit meaning must match the source trace):

```json
{
  "source":"synthetic",
  "histories":{
    "VM1":[
      {"cpu_util_percent":40,"mem_util_percent":50,"net_in":100,"net_out":80,"disk_io_percent":20},
      {"cpu_util_percent":45,"mem_util_percent":52,"net_in":110,"net_out":85,"disk_io_percent":22},
      {"cpu_util_percent":50,"mem_util_percent":55,"net_in":120,"net_out":90,"disk_io_percent":25},
      {"cpu_util_percent":55,"mem_util_percent":58,"net_in":130,"net_out":95,"disk_io_percent":28}
    ]
  }
}
```

CPU/RAM/disk inputs must be finite 0–100; network inputs finite and nonnegative. At least four observations are required. Up to the last 64 observations are retained per VM; inference consumes the last four. `source` is `measured`, `user-entered` or `synthetic`; this label is user-supplied provenance, not independently verified measurement.

Preview options (all fields optional, defaults shown):

```json
{
  "strategy":"predictive",
  "interval_minutes":5,
  "energy_weight":1,
  "risk_weight":2,
  "balance_weight":0.15,
  "migration_weight":0.4,
  "headroom":0.1,
  "cooldown_intervals":2,
  "minimum_improvement":0.002,
  "idle_watts":100,
  "peak_watts":250,
  "sleep_watts":5,
  "migration_wh_per_gb":0.05,
  "beam_width":32
}
```

Strategy can be `predictive`, `first_fit`, `best_fit` or `static`. Static preserves allocation and may leave pending VMs unassigned. The preview returns an `allocation` mapping for the complete non-static plan, its source `revision`, planned actions and metrics. Apply by copying **the actual returned allocation and revision** into a request with the same options. Do not hardcode an allocation from documentation. Editing topology or histories changes the revision and invalidates older previews.

The comparison endpoint first places pending VMs into available reservations without moving running VMs, then evaluates all methods from that identical complete state. It is read-only. A method may report `infeasible`; comparison never drops VMs to manufacture savings. This is a one-interval comparison. Multi-interval paired results are produced by `python -m scripts.run_experiments`.

Adaptive example:

```json
{"source":"synthetic","seed":42,"strategy":"predictive","cooldown_intervals":2}
```

`source="unchanged"` reuses saved readings and never claims to sample live data. A failed step rolls back histories, tick, allocation and event changes.

## Errors and concurrency

- `404`: unknown VM/server.
- `409`: duplicate ID, insufficient capacity, stale preview, cooldown, incomplete plan or no sequentially feasible migration order.
- `422`: invalid fields, nonfinite values, history length, strategy or inconsistent power-profile ordering.
- Planner limits: 80 VMs, 40 servers, beam width 1–128. Exceeding the interactive planner limit is a validation error; bounded search may fail even if a different algorithm could find a plan.

State-changing operations serialize within the single backend process and persist with atomic file replacement. Applied batches are simulated transactions; the ordered actions validate destination capacity while source allocations still exist. The simulator does not execute real live migrations or model simultaneous migration bandwidth contention.
