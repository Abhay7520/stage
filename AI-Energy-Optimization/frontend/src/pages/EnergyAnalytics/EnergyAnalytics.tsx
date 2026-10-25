import { useEffect, useState } from "react";
import { request } from "../../services/client";
import { defaultOptions } from "../../types/optimization";
import type { Plan } from "../../types/optimization";
import {
  Title,
  Notice,
  ErrorBox,
  MetricsCards,
  ServerBars,
} from "../../components/ResearchUI";
export default function EnergyAnalytics() {
  const [data, setData] = useState<Plan | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    request<Plan>("/optimization/preview", {
      ...defaultOptions,
      strategy: "static",
    })
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);
  return (
    <>
      <Title
        title="Energy Analytics"
        description="Analytical power estimates from saved forecast demand and allocation, with explicit server sleep states."
      />
      <Notice>
        Default profile per server: 100 W idle, 250 W peak, 5 W empty sleep.
        Active W = 100 + 150 × (0.8 × CPU fraction + 0.2 × RAM fraction). Wh = W
        × interval minutes / 60. These profiles are assumptions and are
        configurable in optimization previews.
      </Notice>
      <ErrorBox message={error} />
      {data && (
        <>
          <MetricsCards metrics={data.before} />
          <ServerBars metrics={data.before} />
          <div className="panel">
            <p>
              Scheduled VMs: {data.before.scheduled_vms}; unassigned:{" "}
              {data.before.unassigned_vms}.
            </p>
            <p>
              Missing histories (100% assumed demand):{" "}
              {data.missing_histories.join(", ") || "None"}.
            </p>
            <p>
              The SWEAT energy regressor is retained separately in the original
              model lab. Its independent measurements are never paired with
              workload rows by index.
            </p>
          </div>
        </>
      )}
    </>
  );
}
