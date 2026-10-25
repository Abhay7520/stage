export interface ResourceData {
  cpu_util_percent: number;
  mem_util_percent: number;
  net_in: number;
  net_out: number;
  disk_io_percent: number;
}

export interface EnergyInput {
  cpu_mean: number;
  cpu_max: number;
  cpu_min: number;
  cpu_std: number;
  cpu_median: number;
  cpu_frequency_ghz: number;
  memory_util_gb: number;
  sda_write_count_during_interval: number;
  sda_read_count_during_interval: number;
}

export interface OptimizationInput {
  current_cpu: number;
  predicted_workload: number;
  cpu_frequency_ghz: number;
  memory_util_gb: number;
  sda_write_count_during_interval: number;
  sda_read_count_during_interval: number;
}

export interface WorkloadResponse {
  success: boolean;
  predicted_cpu_utilization: number;
  unit: string;
}

export interface EnergyResponse {
  success: boolean;
  predicted_energy: number;
  unit: string;
}

export interface CandidateAllocation {
  cpu_allocation: number;
  predicted_energy: number;
  optimization_score: number;
  feasible: boolean;
}

export interface OptimizationResult {
  current_cpu: number;
  predicted_workload: number;
  recommended_cpu: number;
  current_predicted_energy: number;
  optimized_predicted_energy: number;
  estimated_energy_saving: number;
  estimated_energy_saving_percent: number;
  optimization_score: number;
  candidate_allocations: CandidateAllocation[];
}

export interface OptimizationResponse {
  success: boolean;
  optimization: OptimizationResult;
}
