# Experimental comparison results

Actual results produced in this environment by `python -m scripts.run_experiments`; raw paired records are in `experiments/paired_results.csv`. See `experiments/summary.json` for full precision.

Ten paired seeds each generate four servers and eight hypothetical VMs with different reservations, initially distributed over four servers. Eight five-minute intervals replay separate segments from the untouched aggregate workload test block. Every method receives the same reservations, topology and next-row CPU/RAM demand for a seed/interval. Predictions guide allocation; the analytical power estimate is then calculated using the next observation as simulated realized demand. Migration energy is included, and all VMs remain served. Failed reoptimizations retain the previous valid allocation and are counted. No physical power or SLA measurements are claimed.

| Method | Mean total Wh over 8 intervals | Mean saving vs static % | Mean migrations | Mean pressure proxy | Failed reoptimizations / 80 |
|---|---:|---:|---:|---:|---:|
| static | 352.323 | 0.00 | 0.00 | 0.000802 | 0 |
| first_fit | 210.991 | 40.12 | 5.20 | 0.002241 | 0 |
| best_fit | 300.135 | 14.88 | 4.80 | 0.002186 | 24 |
| predictive | 245.505 | 30.47 | 3.00 | 0.000377 | 0 |
| predictive_no_forecast | 235.674 | 33.19 | 3.20 | 0.000000 | 0 |

The predictive method reduces estimated energy versus static and has fewer migrations and less pressure than first fit, but first fit uses less energy. The no-forecast ablation also uses less energy and has lower pressure in this setup. Therefore these experiments **do not establish that prediction improves placement performance**. They demonstrate an integrated experimental pipeline and a trade-off selected by configured weights. Best fit encounters migration-order/cooldown infeasibility in some intervals; the recorded failures retain service instead of dropping workloads.

The “predictive_no_forecast” ablation uses the same search/constraints with conservative 100% CPU/RAM demand rather than model predictions. It helps isolate predictive inputs, but it is not a reproduction of any specific paper.

Limits: small synthetic topology, only ten paired seeds, correlated aggregate observations assigned to hypothetical VMs, unknown timestamp/entity provenance, assumed power profiles and migration costs. No statistical-significance, generalization or base-paper-superiority claim follows. Static/adaptive energy differences are conditional estimates under this model, not expected real-cloud savings.

The interactive comparison page is a separate one-interval analysis of the current saved state; its values will differ from these multi-interval results.
