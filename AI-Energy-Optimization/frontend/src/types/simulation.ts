export interface VirtualMachine {
  id: string;
  name: string;
  cpu: number;
  memory: number;
  server_id: string | null;
}

export interface PhysicalServer {
  id: string;
  name: string;
  cpu_capacity: number;
  memory_capacity: number;
  cpu_used: number;
  memory_used: number;
  cpu_available: number;
  memory_available: number;
  cpu_percent: number;
  memory_percent: number;
  status: "normal" | "high";
  vms: VirtualMachine[];
}

export interface SimulationMetrics {
  total_servers: number;
  total_vms: number;
  assigned_vms: number;
  unassigned_vms: number;
  total_cpu: number;
  used_cpu: number;
  total_memory: number;
  used_memory: number;
  cpu_utilization_percent: number;
  memory_utilization_percent: number;
  high_utilization_servers: number;
}

export interface SimulationState {
  servers: PhysicalServer[];
  vms: VirtualMachine[];
  metrics: SimulationMetrics;
}

export interface ServerCreate {
  id: string;
  name: string;
  cpu_capacity: number;
  memory_capacity: number;
}

export interface VMCreate {
  id: string;
  name: string;
  cpu: number;
  memory: number;
}

export interface PlacementRequest {
  vm_id: string;
  server_id: string;
}
