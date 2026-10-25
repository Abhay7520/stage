# Verification record

Executed on 25 October 2026 in the available Linux environment with Python 3.12.14, Node 24.22.1 and Chromium 134 via Playwright 1.51.0. Windows installation and external cloud deployment were not executed.

| Check | Result | Evidence |
|---|---|---|
| Python unit/API/inference/constraint suite | 50 passed | `experiments/pytest.txt` |
| Original Phase 6 regressions | 8 passed, included in the 50 above | `tests/test_phase6_regression.py` |
| New integrated tests | 42 passed, included above | `tests/test_integrated.py` |
| Frontend TypeScript + production build | Passed | `experiments/frontend-build.txt` |
| Frontend ESLint | Passed | `experiments/frontend-lint.txt` |
| Chromium UI/API integration | Passed, 12 sidebar pages | `experiments/browser-smoke.json`, `browser-run.txt` |
| Mobile layout and navigation | Passed at 390 × 844; screenshot visually reviewed | Internal visual inspection; browser assertions in `experiments/browser-smoke.json` |
| CPU/RAM training/evaluation | Completed, validation selection and test/persistence comparisons saved | `models/forecast_evaluation.json` |
| Energy training/evaluation | Completed, 1,050 files, disjoint file-group split | `models/energy_evaluation.json`, `experiments/energy_training.txt` |
| Paired replay comparison + no-forecast ablation | Completed, 10 seeds × 8 intervals × 5 methods | `experiments/paired_results.csv`, `summary.json` |
| Python dependency consistency | `pip check`: no broken requirements | Runtime check |
| Supplied dataset preservation | Byte-for-byte verification against uploaded archive | `experiments/source-audit.json` |

## What the tests check

Feature order and lags; short/nonfinite history rejection; forecast clipping and vCPU/GB conversion; persistence fallback; incomplete aggregation; CPU and RAM constraints; invalid/duplicate/unknown resources; allocation and migration atomicity; complete VM coverage; stale-preview rejection; infeasible search behavior; migration energy; sequential migration capacity including swap rejection; cooldown; server sleep/Wh units; persisted restart and reset; concurrent mutations; CORS; malformed NaN input returning 422; adaptive rollback of histories/tick; report generation; original model inference and original Phase 6 behavior.

Browser flow checks per-VM synthetic history save, forecast output, preview/apply, equal-workload comparison, adaptive interval, history, JSON/CSV downloads, legacy inference, invalidation after editing, browser reload, mobile menu, hidden sidebar position and horizontal overflow. The browser script runs isolated test servers and temporary state, not the normal user's runtime data. Desktop dashboard/placement and mobile analytics were visually inspected during verification. Browser images are not part of the deliverable.

One harmless dependency deprecation warning is emitted by the FastAPI/Starlette `httpx` test-client combination. Tests and all assertions pass; the warning is retained in the log.

## Reproduce

From the project root with dependencies installed:

```text
python -m pytest -q
python -m scripts.verify_browser
python train_memory.py
python -m scripts.train_energy_validated
python -m scripts.run_experiments
```

From `frontend`:

```text
npm ci
npm run build
npm run lint
```

Browser tests additionally require `requirements-dev.txt` and `python -m playwright install chromium`. Test servers use ports 8011 and 5178. See SETUP.md for Windows commands.

## Limits of verification

Local Chromium and simulated APIs were checked, not every browser/device combination, Windows-specific dependency installation, real hypervisor/cloud migration, physical energy, application latency, SLA compliance, multi-process durability, sudden power-loss durability, very large topologies or independent real VM datasets. Bounded search may report infeasibility even when another search could find a solution. Experiments record heuristic failures rather than suppressing them. Research novelty/base-paper superiority and forecast benefit are not established by these tests. Full metric limitations are in MODEL_EVALUATION.md and EXPERIMENT_RESULTS.md.

## Guided UI and custom-data update

The browser flow now also checks page-guide popups on all twelve pages, the Dashboard’s seven-step full workflow, field/action explanations, Escape and backdrop dismissal, keyboard focus trapping/restoration, and mobile dialog sizing. Opening an action’s help must not change the simulation revision or apply the action.

Custom data is exercised through the UI: changing CPU/RAM readings and saving them must persist the entered values, change the actual model forecasts and record user-entered provenance. Unsaved changes clear old results and block batch forecasting. An invalid 101% CPU value must produce a validation error without replacing the last accepted history. The original laboratory also ignores stale in-flight results after its inputs change. All of these checks use temporary test state.
