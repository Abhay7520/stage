# Research gap mapping and boundaries

The proposed contribution is an integrated, reproducible **prototype pipeline**. No assertion is made that these individual techniques or their combination are unprecedented. The selected paper's full algorithm, code and protocol were not present in the ZIP; first/best fit are conventional comparators, not a claimed reproduction of its Q-learning method.

| Identified gap | Implementation | Evidence | Remaining limit |
|---|---|---|---|
| CPU-only workload awareness | Separate CPU and RAM XGBoost regressors; shared lag contract; persistence baselines | `scripts/train_forecasts.py`, `models/forecast_evaluation.json`, `outputs/forecast_holdout.csv` | RAM test MAE is worse than persistence; aggregated file has no entity/time metadata |
| Forecasts disconnected from allocation | Forecast fractions drive candidate power/pressure scores | `backend/optimization/engine.py: predictions, plan, evaluate` | VM transfer is experimental; missing histories use conservative 100% |
| Single-resource placement | Full CPU and RAM reservations constrain every candidate and applied state | `valid`, `store.validate`, resource tests | No network/storage/NUMA constraints or overcommit |
| Standalone static VM placement | Bounded beam search, selectable conventional baselines, revision-safe apply | `plan`, preview/apply APIs, browser smoke | Approximate search; no global optimality guarantee; not RL |
| Missing consolidation/idle model | Full repacking candidates and empty-server sleep state; consolidation UI preset | `evaluate`, `VMConsolidation`, paired experiments | No actual hypervisor/server shutdown; no wake latency/power transition model |
| Ignored migration overhead | RAM-proportional migration Wh and duration proxy, feasible sequential move ordering | `migration_schedule`, `evaluate`, cyclic/atomicity tests | Assumed 1 Gbps throughput; dirty-page transfer, contention and wake energy omitted |
| Single-objective decisions | Normalized energy, pressure, balance and migration components with configurable weights | `Options`, `evaluate`, before/after UI | Pressure proxies replace actual application performance/SLA measurements |
| No continuous adaptation | Successive intervals, synthetic or unchanged history source, cooldown and minimum improvement | `/optimization/step`, history, replay experiment | No background telemetry agent or real-time orchestration |
| No end-to-end state | Single shared persistent store and serialized rollback-safe mutations | persistence, concurrency and stale-preview tests | One process/worker only; JSON persistence is not a distributed database |
| Weak evaluation | Equal-workload four-strategy comparison; paired static/adaptive replay; no-forecast ablation | `experiments/paired_results.csv`, `summary.json` | Small hypothetical topology; correlated aggregate traces; no paper-specific comparison |
| Limited interactive evidence | Twelve page folders, forecasts, reservation bars, previews, exports | browser integration script/results, frontend build/lint | Local Chromium checked; Windows/deployment not executed |

## What the experiment supports

The ten paired scenarios show predictive search reduces analytical energy relative to static allocation and uses fewer migrations than first fit, with a lower resource-pressure proxy. First fit achieves lower energy, while the no-forecast ablation also has lower energy in this experiment. This is **not evidence that forecasting universally improves placement**. The simulation demonstrates integration and trade-offs; the mixed results identify limitations rather than being hidden.

## What is still required for a paper-level claim

A timestamped per-VM trace with documented units, an application performance model or measurements, calibrated server/migration power measurements, the exact base-paper protocol, topology-scale sensitivity experiments and independent workloads/hardware holdouts. These are validation/data requirements, not missing claims to fill with invented numbers.
