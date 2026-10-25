import { useEffect, useState, useRef, createContext, useContext } from "react";
import {
  optimizeResources,
  predictEnergy,
  predictWorkload,
  checkBackend,
} from "../services/api";
import type {
  EnergyInput,
  OptimizationResult,
  ResourceData,
} from "../types/legacy";
const initialHistory: ResourceData[] = [
  {
    cpu_util_percent: 40,
    mem_util_percent: 50,
    net_in: 100,
    net_out: 80,
    disk_io_percent: 20,
  },

  {
    cpu_util_percent: 45,
    mem_util_percent: 52,
    net_in: 110,
    net_out: 85,
    disk_io_percent: 22,
  },

  {
    cpu_util_percent: 50,
    mem_util_percent: 55,
    net_in: 120,
    net_out: 90,
    disk_io_percent: 25,
  },

  {
    cpu_util_percent: 55,
    mem_util_percent: 58,
    net_in: 130,
    net_out: 95,
    disk_io_percent: 28,
  },
];

const initialEnergy: EnergyInput = {
  cpu_mean: 55,
  cpu_max: 60,
  cpu_min: 50,
  cpu_std: 4,
  cpu_median: 55,

  cpu_frequency_ghz: 2.5,

  memory_util_gb: 8,

  sda_write_count_during_interval: 100,

  sda_read_count_during_interval: 150,
};

export function useLegacyController() {
  const inputVersion = useRef(0);
  const latestRun = useRef(0);
  const [history, setHistory] = useState<ResourceData[]>(initialHistory);

  const [energyInput, setEnergyInputRaw] = useState<EnergyInput>(initialEnergy);

  const [predictedWorkload, setPredictedWorkload] = useState<number | null>(
    null,
  );

  const [predictedEnergy, setPredictedEnergy] = useState<number | null>(null);

  const [optimization, setOptimization] = useState<OptimizationResult | null>(
    null,
  );

  const [backendOnline, setBackendOnline] = useState(false);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    checkBackend().then(setBackendOnline);
  }, []);

  function updateHistory(
    index: number,
    field: keyof ResourceData,
    value: number,
  ) {
    inputVersion.current += 1;
    const updated = [...history];

    updated[index] = {
      ...updated[index],
      [field]: value,
    };

    setHistory(updated);
    setPredictedWorkload(null);
    setOptimization(null);
  }

  function setEnergyInput(value: EnergyInput) {
    inputVersion.current += 1;
    setEnergyInputRaw(value);
    setPredictedEnergy(null);
    setOptimization(null);
  }

  async function runAnalysis() {
    const version = inputVersion.current;
    const run = ++latestRun.current;
    const isCurrent = () =>
      inputVersion.current === version && latestRun.current === run;
    setLoading(true);
    setPredictedWorkload(null);
    setPredictedEnergy(null);
    setOptimization(null);
    setError("");

    try {
      const workloadResult = await predictWorkload(history);

      if (!isCurrent()) return;
      const workload = workloadResult.predicted_cpu_utilization;

      setPredictedWorkload(workload);

      const energyResult = await predictEnergy(energyInput);

      if (!isCurrent()) return;
      setPredictedEnergy(energyResult.predicted_energy);

      const optimizationResult = await optimizeResources({
        current_cpu: history[3].cpu_util_percent,

        predicted_workload: workload,

        cpu_frequency_ghz: energyInput.cpu_frequency_ghz,

        memory_util_gb: energyInput.memory_util_gb,

        sda_write_count_during_interval:
          energyInput.sda_write_count_during_interval,

        sda_read_count_during_interval:
          energyInput.sda_read_count_during_interval,
      });

      if (!isCurrent()) return;
      setOptimization(optimizationResult.optimization);
    } catch (err) {
      if (isCurrent())
        setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      if (latestRun.current === run) setLoading(false);
    }
  }

  const currentCpu = history[3].cpu_util_percent;

  return {
    history,
    setHistory,
    energyInput,
    setEnergyInput,
    predictedWorkload,
    predictedEnergy,
    optimization,
    backendOnline,
    loading,
    error,
    updateHistory,
    runAnalysis,
    currentCpu,
  };
}
export const LegacyContext = createContext<ReturnType<
  typeof useLegacyController
> | null>(null);
export function useLegacy() {
  const c = useContext(LegacyContext);
  if (!c) throw new Error("Missing context");
  return c;
}
