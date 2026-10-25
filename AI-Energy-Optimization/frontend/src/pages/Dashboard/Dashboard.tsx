import { HelpText } from "../../components/help/Help";
import { Explained } from "../../components/help/Help";
import { useState } from "react";
import { useRemote } from "../../hooks/useRemote";
import type { SimulationState } from "../../types/simulation";
import { Title, Notice, ErrorBox } from "../../components/ResearchUI";
import LegacyDashboard from "./LegacyDashboard";
export default function Dashboard() {
  const { data, error, reload } =
    useRemote<SimulationState>("/simulation/state");
  const [lab, setLab] = useState(false);
  return (
    <>
      <Title
        title="Data Center Overview"
        description="Shared server and VM reservations. Forecasting and optimization operate on this same persisted simulation."
      />
      <Notice>
        Decision-support simulator. Initial servers and VMs are demonstration
        configurations. Resource reservations are distinct from measured
        utilization.
      </Notice>
      <ErrorBox message={error} />
      <div className="stat-grid">
        {data &&
          [
            ["Servers", data.metrics.total_servers],
            ["VMs", data.metrics.total_vms],
            ["Assigned", data.metrics.assigned_vms],
            ["Unassigned", data.metrics.unassigned_vms],
          ].map(([k, v]) => (
            <div className="stat-card" key={k}>
              <div>
                <HelpText title={String(k)} />
                <strong>{v}</strong>
              </div>
            </div>
          ))}
      </div>
      <div className="server-grid">
        {data?.servers.map((s) => (
          <div className="panel" key={s.id}>
            <h3>{s.name}</h3>
            <p>
              <HelpText title="Reserved CPU" /> {s.cpu_used} / {s.cpu_capacity}{" "}
              vCPU
            </p>
            <progress value={s.cpu_percent} max={100} />
            <p>
              <HelpText title="Reserved RAM" /> {s.memory_used} /{" "}
              {s.memory_capacity} GB
            </p>
            <progress value={s.memory_percent} max={100} />
            <p>
              {s.vms.map((v) => v.id).join(", ") ||
                "Empty / eligible for simulated sleep"}
            </p>
          </div>
        ))}
      </div>
      <div className="actions">
        <Explained action title="Refresh state">
          <button onClick={() => void reload()}>Refresh state</button>
        </Explained>
        <Explained action title="original model analysis">
          <button onClick={() => setLab(!lab)}>
            {lab ? "Hide" : "Open"} original model analysis
          </button>
        </Explained>
      </div>
      {lab && (
        <>
          <Notice>
            Original model lab with synthetic form defaults. Energy and workload
            estimates come from separate datasets; its CPU-input scenarios are
            exploratory, not validated control savings.
          </Notice>
          <LegacyDashboard />
        </>
      )}
    </>
  );
}
