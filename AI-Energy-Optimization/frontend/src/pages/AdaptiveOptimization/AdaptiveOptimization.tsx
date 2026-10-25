import { Explained } from "../../components/help/Help";
import { useState } from "react";
import { request } from "../../services/client";
import { defaultOptions } from "../../types/optimization";
import type { Plan } from "../../types/optimization";
import { Title, Notice, ErrorBox, PlanView } from "../../components/ResearchUI";
export default function AdaptiveOptimization() {
  const [source, setSource] = useState("unchanged");
  const [strategy, setStrategy] = useState("predictive");
  const [seed, setSeed] = useState(42);
  const [tick, setTick] = useState<number | null>(null);
  const [data, setData] = useState<Plan | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function step() {
    setBusy(true);
    setError("");
    try {
      const r = await request<{ plan: Plan; state: { tick: number } }>(
        "/optimization/step",
        { ...defaultOptions, source, strategy, seed },
      );
      setData(r.plan);
      setTick(r.state.tick);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Title
        title="Adaptive Optimization"
        description="Advance a simulation interval, update demand, reoptimize and save the allocation decision."
      />
      <Notice>
        Two-interval migration cooldown and minimum objective improvement reduce
        churn. Synthetic mode appends generated readings and marks them
        synthetic. Unchanged mode reuses saved observations; it does not collect
        live telemetry.
      </Notice>
      <ErrorBox message={error} />
      <div className="panel">
        <div className="control-grid">
          <Explained title="Workload source">
            <label>
              Workload source
              <select
                aria-label="Workload source"
                value={source}
                onChange={(e) => {
                  setSource(e.target.value);
                  setData(null);
                }}
              >
                <option value="unchanged">Saved observations unchanged</option>
                <option value="synthetic">Seeded synthetic fluctuations</option>
              </select>
            </label>
          </Explained>
          <Explained title="Allocation">
            <label>
              Allocation
              <select
                aria-label="Allocation"
                value={strategy}
                onChange={(e) => {
                  setStrategy(e.target.value);
                  setData(null);
                }}
              >
                <option value="predictive">Adaptive predictive search</option>
                <option value="static">Static allocation</option>
              </select>
            </label>
          </Explained>
          <Explained title="Seed">
            <label>
              Seed
              <input
                type="number"
                min={0}
                aria-label="Seed"
                value={seed}
                onChange={(e) => {
                  setSeed(Number(e.target.value));
                  setData(null);
                }}
              />
            </label>
          </Explained>
        </div>
        <Explained action title="Advance one interval & apply">
          <button disabled={busy} onClick={() => void step()}>
            {busy ? "Advancing…" : "Advance one interval & apply"}
          </button>
        </Explained>
        {tick !== null && <p>Saved interval: {tick}</p>}
      </div>
      {data && <PlanView plan={data} />}
    </>
  );
}
