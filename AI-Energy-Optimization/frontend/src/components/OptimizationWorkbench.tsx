import { Explained } from "./help/Help";
import { useState } from "react";
import { request } from "../services/client";
import { defaultOptions } from "../types/optimization";
import type { Plan, Options } from "../types/optimization";
import { ErrorBox, Notice, PlanView } from "./ResearchUI";
export default function OptimizationWorkbench({
  consolidation = false,
}: {
  consolidation?: boolean;
}) {
  const [options, setOptions] = useState<Options>({
    ...defaultOptions,
    ...(consolidation ? { energy_weight: 2, migration_weight: 0.1 } : {}),
  });
  const [plan, setPlan] = useState<Plan | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  function change(key: keyof Options, value: number | string) {
    setOptions({ ...options, [key]: value });
    setPlan(null);
    setMessage("");
  }
  async function run(apply = false) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      if (apply && plan) {
        await request("/optimization/apply", {
          ...options,
          allocation: plan.allocation,
          revision: plan.revision,
        });
        setPlan(null);
        setMessage("Plan applied to the shared simulation.");
      } else setPlan(await request<Plan>("/optimization/preview", options));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="panel">
      <Notice>
        Forecast-informed beam search is a constrained optimization algorithm,
        not reinforcement learning. Reservations never exceed capacity. All
        power and performance values are simulation estimates.
      </Notice>
      <ErrorBox message={error} />
      <fieldset className="workload-editor" disabled={busy}>
        <div className="control-grid">
          <Explained title="Strategy">
            <label>
              Strategy
              <select
                aria-label="Strategy"
                value={options.strategy}
                onChange={(e) => change("strategy", e.target.value)}
              >
                {["predictive", "first_fit", "best_fit"].map((x) => (
                  <option key={x}>{x}</option>
                ))}
              </select>
            </label>
          </Explained>
          {(
            [
              ["interval_minutes", "Interval (minutes)"],
              ["energy_weight", "Energy weight"],
              ["risk_weight", "Pressure weight"],
              ["migration_weight", "Migration weight"],
              ["balance_weight", "Balance weight"],
              ["headroom", "Forecast headroom"],
              ["idle_watts", "Server idle W"],
              ["peak_watts", "Server peak W"],
              ["sleep_watts", "Server sleep W"],
              ["migration_wh_per_gb", "Migration Wh / GB"],
            ] as const
          ).map(([k, label]) => (
            <Explained key={k} title={String(label)}>
              <label>
                {label}
                <input
                  type="number"
                  min={0}
                  step="any"
                  aria-label={label}
                  value={options[k]}
                  onChange={(e) => change(k, Number(e.target.value))}
                />
              </label>
            </Explained>
          ))}
        </div>
        <div className="actions">
          <Explained action title="Preview">
            <button disabled={busy} onClick={() => void run()}>
              Preview {consolidation ? "consolidation" : "placement"}
            </button>
          </Explained>
          <Explained action title="Apply preview">
            <button disabled={busy || !plan} onClick={() => void run(true)}>
              Apply preview
            </button>
          </Explained>
        </div>
      </fieldset>
      {message && <p role="status">{message}</p>}
      {plan && <PlanView plan={plan} />}
    </div>
  );
}
