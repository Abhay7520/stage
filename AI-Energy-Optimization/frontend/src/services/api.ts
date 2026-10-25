import { request } from "./client";
import type {
  ResourceData,
  EnergyInput,
  OptimizationInput,
  WorkloadResponse,
  EnergyResponse,
  OptimizationResponse,
} from "../types/legacy";
export const predictWorkload = (history: ResourceData[]) =>
  request<WorkloadResponse>("/predict/workload", { history });
export const predictEnergy = (data: EnergyInput) =>
  request<EnergyResponse>("/predict/energy", data);
export const optimizeResources = (data: OptimizationInput) =>
  request<OptimizationResponse>("/optimize", data);
export async function checkBackend(): Promise<boolean> {
  try {
    await request("/health");
    return true;
  } catch {
    return false;
  }
}
