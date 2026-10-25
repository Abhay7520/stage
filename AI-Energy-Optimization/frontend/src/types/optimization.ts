export interface Observation {
  cpu_util_percent: number;
  mem_util_percent: number;
  net_in: number;
  net_out: number;
  disk_io_percent: number;
}
export interface Forecast {
  vm_id: string;
  vm_name: string;
  predicted_cpu_percent: number;
  predicted_memory_percent: number;
  estimated_cpu_demand_vcpu: number;
  estimated_memory_demand_gb: number;
  resource_risk: string;
  cpu_strategy: string;
  memory_strategy: string;
}
export interface ServerForecast {
  server_id: string;
  server_name: string;
  complete: boolean;
  predicted_cpu_percent: number;
  predicted_memory_percent: number;
}
export interface Forecasts {
  vm_forecasts: Forecast[];
  server_forecasts: ServerForecast[];
  missing_vm_ids: string[];
  sources: Record<string, string>;
}
export interface Options {
  strategy: string;
  interval_minutes: number;
  energy_weight: number;
  risk_weight: number;
  balance_weight: number;
  migration_weight: number;
  headroom: number;
  cooldown_intervals: number;
  minimum_improvement: number;
  idle_watts: number;
  peak_watts: number;
  sleep_watts: number;
  migration_wh_per_gb: number;
  beam_width: number;
}
export interface ServerMetric {
  server_id: string;
  state: string;
  power_w: number;
  cpu_pressure_percent: number;
  memory_pressure_percent: number;
  reserved_cpu: number;
  reserved_memory: number;
}
export interface Metrics {
  power_w: number;
  energy_wh: number;
  total_energy_wh: number;
  migration_energy_wh: number;
  sla_pressure_proxy: number;
  imbalance: number;
  migrations: number;
  migration_gb: number;
  migration_seconds_proxy: number;
  active_servers: number;
  mean_active_pressure_percent: number;
  scheduled_vms: number;
  unassigned_vms: number;
  score: number;
  servers: ServerMetric[];
}
export interface Action {
  vm_id: string;
  from_server: string | null;
  to_server: string;
  kind: string;
}
export interface Plan {
  revision: number;
  tick: number;
  strategy: string;
  allocation: Record<string, string>;
  before: Metrics;
  after: Metrics;
  actions: Action[];
  estimated_energy_saving_wh: number;
  comparable_workload: boolean;
  missing_histories: string[];
  explanation: string;
  assumptions: Options;
}
export interface Comparison {
  rows: {
    strategy: string;
    status: string;
    metrics?: Metrics;
    energy_saving_percent?: number;
    reason?: string;
  }[];
  methodology: string;
  missing_histories: string[];
}
export interface Event {
  revision?: number;
  tick: number;
  action: string;
  strategy?: string;
  source?: string;
  before?: Metrics;
  after?: Metrics;
  moves?: Action[];
}
export interface History {
  events: Event[];
  revision: number;
  tick: number;
}
export const defaultOptions: Options = {
  strategy: "predictive",
  interval_minutes: 5,
  energy_weight: 1,
  risk_weight: 2,
  balance_weight: 0.15,
  migration_weight: 0.4,
  headroom: 0.1,
  cooldown_intervals: 2,
  minimum_improvement: 0.002,
  idle_watts: 100,
  peak_watts: 250,
  sleep_watts: 5,
  migration_wh_per_gb: 0.05,
  beam_width: 32,
};
