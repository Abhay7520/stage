# Model evaluation

## Shared CPU/RAM forecasting protocol

The supplied machine workload CSV contains 2,243 rows and five numeric features: CPU utilization %, memory utilization %, network in, network out and disk I/O %. No timestamp, entity identifier or network units are supplied. All rows pass finite/nonnegative and percentage-range checks. The new trainer preserves invalid-row gaps rather than stitching observations after dropping them.

Four observations form 20 features: the five most recent resource values plus lags 1, 2 and 3 for each resource. Targets are next-observation CPU and memory utilization percentages. We use 60/20/20 **file-order** blocks with four-row purges around split boundaries: 1,338 train, 441 validation and 444 test samples. This prevents overlapping observation windows across partitions. It does not establish real temporal ordering, which cannot be verified from the file.

Fixed XGBoost configuration: 180 estimators, depth 3, learning rate 0.04, random seed 42. The train block alone fits each model; validation chooses XGBoost versus persistence based on MAE. Both select XGBoost on validation. The untouched test block reports both methods; it is not used to reselect the deployed method after viewing results.

| Target | Selected method | Test MAE (percentage points) | Test RMSE | Test R² | Persistence test MAE |
|---|---|---:|---:|---:|---:|
| CPU | xgboost | 4.1091 | 5.3739 | 0.5494 | 4.3997 |
| MEMORY | xgboost | 1.3829 | 1.7352 | 0.4678 | 1.1700 |

Memory XGBoost is **worse than persistence on the test block**, despite a validation advantage. This is disclosed model-selection/generalization risk. The project makes no blanket claim that the AI models outperform simple forecasting. Model artifact or selection metadata absence causes an explicit persistence fallback. Forecast strategies are displayed with outputs. Predictions are clipped to 0–100; vCPU/GB demand is the allocated reservation multiplied by the predicted fraction.

Per-VM inference transfers an aggregate model to VM-level histories. It is experimental, not validated per-VM forecasting. Missing histories are not fabricated: forecast results mark them missing; the optimizer assumes 100% CPU/RAM demand conservatively.

Current artifacts: `models/cpu_forecast.json`, `memory_forecast.json`, `forecast_evaluation.json`, and `outputs/forecast_holdout.csv`. Reproduce with `python train_memory.py`. The original supplied workload model is retained for the original model lab, with inherited metadata in `workload_model_info.json`.

## Independently validated energy regressor

The supplied SWEAT collection has 1,050 CSV files and 338,850 valid rows. Features are CPU mean/max/min/std/median, CPU frequency GHz, memory GB and disk read/write counts. Target is `energy_util_during_interval_j` in joules. Source interval duration was not supplied; do not interpret an observation as five-minute server energy.

The validated trainer sorts file paths, uses an 80/20 group split with seed 42, and trains 200 depth-5 XGBoost trees on 271,080 rows. The disjoint 210-file test set contains 67,770 rows; no test data is passed into fitting or model selection. The training-target mean is the baseline. File lists are recorded in `models/energy_evaluation.json` so the split is auditable. Hardware groups may appear across both partitions: this is a file-run holdout, not an unseen-hardware benchmark.

| Method | Test MAE J | Test RMSE J | Test R² |
|---|---:|---:|---:|
| XGBoost | 4.2750 | 12.9937 | 0.6457 |
| Training mean | 12.6800 | 21.8366 | -0.0007 |

Reproduce with `python -m scripts.train_energy_validated`. The current model serves `/predict/energy`; the unused older duplicate energy model was removed from `models/inherited`; the folder layout and active model are unchanged. Existing supplied output CSVs are historical and must not be presented as rerun results. Current holdout predictions are in `outputs/energy_holdout.csv`.

## Other supplied datasets and units

- `vm_cpu_readings_month_aggregated_cpu_mem_no_timestamp.csv`: 8,640 rows, `cpu_usage` and `assigned_mem`. Raw magnitudes are not normalized percentages/GB; no conversion or timestamp correspondence can be justified from supplied metadata. Retained only for original descriptive analysis.
- `instance_usage_grouped_300_seconds_month.csv`: 8,064 rows, average CPU, memory, assigned memory and CPI. No entity/time columns; usage values are fractions by apparent range, not assumed percentages. Retained descriptive analysis, not used as supervised per-VM targets.
- No independent workload and energy datasets are paired by row or treated as synchronized observations.

## Optimization energy and performance estimates

The integrated placement engine deliberately uses a separate transparent analytical model instead of fabricating SWEAT features for each VM. Default per-server power: 100 W idle, 250 W peak, 5 W sleep. Active power is `idle + (peak-idle) * min(1, 0.8*CPU_demand/capacity + 0.2*RAM_demand/capacity)`. Empty servers sleep immediately. Energy Wh is power W times interval minutes / 60. Identical server watt profiles, even for different capacities, are an explicit simplification; users can change the uniform profile. Wake-up energy/latency and cooling/PUE are omitted.

Migration energy is `moved_reserved_RAM_GB * 0.05 Wh/GB` by default. Migration duration is `RAM_GB / 0.125 GB/s`, an assumed 1 Gbps link without dirty-page retransmission or contention. These are accounting proxies, not measured migration behavior.

Resource-pressure risk per active server is `max(0, max(CPU_fraction,RAM_fraction) + headroom - 0.85)^2`. Mean risk across all servers is the SLA-pressure proxy. Balance is variance of max-resource pressure across active servers. Full allocated CPU/RAM reservations remain the hard constraints; predictions do not enable overcommit.

Objective = weighted normalized total interval energy (including migrations) + weighted mean pressure proxy + weighted balance variance + weighted migrated RAM / total VM RAM. Energy is normalized by all-server peak interval Wh. Search includes current complete allocation and applies a minimum score-improvement threshold. It is approximate beam search and cannot guarantee a global optimum. No measured application latency, throughput, SLA violations or physical CPU-control savings are inferred from these proxies.
