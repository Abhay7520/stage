# GridOpt AI — integrated energy-aware cloud simulation

**AI-Based Energy Optimization for Cloud Data Center Resource Management Using Workload Prediction and Intelligent Resource Allocation**

An upgrade of the supplied Phase 6 project, preserving its simulator, original model APIs, training utilities, datasets, and dark visual design. The completed research prototype integrates CPU/RAM forecasts, constrained VM placement, consolidation, configurable multi-objective search, adaptive intervals, persistent history, controlled comparisons and downloadable reports.

Start with [SETUP.md](SETUP.md), then [DEMO_GUIDE.md](DEMO_GUIDE.md). Read [USER_GUIDANCE.md](USER_GUIDANCE.md) for the in-app ⓘ guides and custom-data workflow. No model retraining is required to start: trained artifacts are included.

## Capabilities

- Page-level ⓘ popups on all 12 pages, including the full project workflow in Dashboard; contextual help for inputs, actions, columns and metrics.
- Custom VM observations are saved and forecast using their actual values; unsaved edits clear old results and must be saved before batch forecasting.

- Create physical servers and VMs; allocate/migrate with independent CPU and RAM reservation checks.
- Save VM histories with `measured`, `user-entered` or `synthetic` provenance. Forecast VM demand and aggregate it per server.
- Preview complete placements using forecast-informed beam search, first fit or best fit. Inspect before/after metrics and ordered actions before applying.
- Consolidate onto fewer servers when the objective and constraints justify it; estimate empty-server sleep power.
- Tune energy, resource-pressure, balance and migration objectives. Reject stale previews and unsafe migrations.
- Advance simulation intervals, optionally generating reproducible synthetic workload fluctuations. Apply cooldown and minimum-improvement thresholds.
- Compare four strategies on equal served workloads, export JSON/CSV, and inspect recorded history.
- Retain the original single-host workload/energy model laboratory, clearly labeled as exploratory scenarios.

## Architecture and folder map

```text
AI-Energy-Optimization/
  backend/
    main.py                     # composition, CORS, API entrypoint
    config.py                   # paths
    schemas.py                  # original resource and energy contracts
    simulation/
      engine.py                 # preserved Phase 6 capacity engine
      store.py                  # shared state, persistence, rollback, revision
      routes.py, schemas.py     # server/VM APIs and state responses
    intelligence/
      service.py, routes.py     # shared features, CPU/RAM inference, histories
      legacy_models.py          # original workload/energy regressors
      legacy_routes.py          # original API endpoints
    optimization/
      engine.py                 # baselines, beam search, objectives, migrations
      routes.py, schemas.py     # previews, apply, comparison, adaptive intervals
    reporting/routes.py         # evaluation, JSON report, CSV export
  frontend/src/
    pages/
      Dashboard/                # shared simulation overview + original lab
      ResourceMonitor/          # original single-host input forms
      AIOptimization/           # multi-objective workbench + original scenarios
      DataCenterSimulator/      # preserved create/allocate/migrate UI
        components/             # page-specific controls
      WorkloadIntelligence/     # per-VM history editing and forecasts
      VMPlacement/              # full constrained placement
      VMConsolidation/          # consolidation objective preset
      EnergyAnalytics/          # analytical power and energy estimates
      OptimizationComparison/   # controlled comparison
      AdaptiveOptimization/     # successive simulation intervals
      SimulationHistory/        # decision history
      Reports/                  # exports and model evidence
    components/                 # shared controls, workbench, metrics and charts
    hooks/                      # data loading and original form state
    services/                   # HTTP clients; no API requests in rendering code
    types/                      # simulation, forecast and optimization contracts
    utils/                      # reserved for shared non-UI helpers
  src/                          # retained loaders, preprocessing, original optimizers
  scripts/                      # validated training, experiments, browser verification
  tests/                        # new tests and original Phase 6 regressions
  models/                       # CPU, RAM, energy artifacts and evaluations
    inherited/                  # same folder; unused duplicate model removed
  data/                         # all supplied datasets, unchanged
  outputs/                      # holdouts and optimizer inputs retained; redundant exports removed
  experiments/                  # actual runs, paired results, logs
  runtime/                      # generated persistent state; not shipped
```

Small compatibility modules preserve old `src.datacenter_simulator`, `backend.model_service`, `backend.simulation_routes` and intelligence import paths. Each sidebar heading has its own page folder. Visual styles shared by pages remain in `styles.css` and `research.css`; simulator-specific styles stay with its page.

## Algorithms and evidence

CPU and RAM use separate XGBoost regressors with a common 20-feature observation/lag contract. Persistence is evaluated and serves as an explicit fallback. The intelligent allocation algorithm is **bounded constrained beam search**, not renamed Q-learning or a trained RL policy. It uses forecast pressure in its objective and full reservations for feasibility.

See [MODEL_EVALUATION.md](MODEL_EVALUATION.md), [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md), [RESEARCH_GAP_MAPPING.md](RESEARCH_GAP_MAPPING.md), [TESTING.md](TESTING.md), [API_DOCUMENTATION.md](API_DOCUMENTATION.md) and [PHASE_IMPLEMENTATION.md](PHASE_IMPLEMENTATION.md).

## Dataset boundaries

- Machine workload: 2,243 rows of CPU/RAM/network/disk aggregates. No timestamp or entity identifier. File-order forecasting is an assumption, and transfer to individual VMs is experimental.
- SWEAT energy: 1,050 CSV files, 338,850 observations. The energy regressor is validated using disjoint file groups and is kept separate from workload optimization's analytical power model.
- VM and instance aggregates: preserved for the original analysis scripts. Unknown raw units and missing entity/time metadata prevent defensible per-VM demand forecasting from these files.

The project never joins independent workload and energy rows by index.

## Practical limits

This is a local, single-user **simulation research prototype**, not a real cloud orchestrator. Run one backend worker. JSON persistence is serialized in one process, not a multi-process database. Interactive search is bounded to 80 VMs/40 servers, can miss a feasible/better solution, and does not prove a global optimum. All server power, migration-energy/duration and SLA-pressure estimates are assumptions/proxies. No actual latency, application throughput, carbon, GPU scheduling or DVFS control is implemented.

The exact base-paper implementation and protocol were not supplied. Integrated features and conventional-baseline experiments demonstrate implementation coverage; they do not establish publication novelty or superiority over that paper. Predictive search does not win every metric; the included results show this openly.
