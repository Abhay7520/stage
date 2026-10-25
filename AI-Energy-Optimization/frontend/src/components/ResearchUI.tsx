import { HelpText } from "./help/Help";
import type { ReactNode } from "react";
import type { Metrics, Plan } from "../types/optimization";
export function Notice({ children }: { children: ReactNode }) {
  return <div className="research-notice">{children}</div>;
}
export function ErrorBox({ message }: { message: string }) {
  return message ? (
    <div className="error-box" role="alert">
      {message}
    </div>
  ) : null;
}
export function Title({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="page-title">
      <span className="eyebrow">CLOUD RESOURCE RESEARCH LAB</span>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}
export function MetricsCards({ metrics }: { metrics: Metrics }) {
  return (
    <div className="stat-grid">
      {[
        ["Estimated energy", `${metrics.total_energy_wh.toFixed(2)} Wh`],
        ["Active servers", metrics.active_servers],
        ["Pressure proxy", metrics.sla_pressure_proxy.toFixed(4)],
        ["Migrations", metrics.migrations],
      ].map(([label, value]) => (
        <div className="stat-card" key={label}>
          <div>
            <HelpText title={String(label)} />
            <strong>{value}</strong>
          </div>
        </div>
      ))}
    </div>
  );
}
export function ServerBars({ metrics }: { metrics: Metrics }) {
  return (
    <div className="server-grid">
      {metrics.servers.map((s) => (
        <article className="panel" key={s.server_id}>
          <h3>
            {s.server_id} <small>{s.state}</small>
          </h3>
          <p>{s.power_w.toFixed(1)} estimated W</p>
          {[
            ["CPU", s.cpu_pressure_percent],
            ["RAM", s.memory_pressure_percent],
          ].map(([l, n]) => (
            <div key={l}>
              <span>
                <HelpText title={String(l)}>{l}</HelpText>:{" "}
                {Number(n).toFixed(1)}% predicted demand
              </span>
              <progress max={100} value={Number(n)} />
            </div>
          ))}
          <small>
            Reserved: {s.reserved_cpu} vCPU / {s.reserved_memory} GB
          </small>
        </article>
      ))}
    </div>
  );
}
export function PlanView({ plan }: { plan: Plan }) {
  return (
    <>
      <Notice>
        {plan.explanation}{" "}
        {plan.missing_histories.length > 0 &&
          `Missing histories (${plan.missing_histories.join(", ")}): 100% demand assumed.`}
      </Notice>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Metric</th>
              <th>Before</th>
              <th>After</th>
            </tr>
          </thead>
          <tbody>
            {(
              [
                "total_energy_wh",
                "scheduled_vms",
                "active_servers",
                "sla_pressure_proxy",
                "imbalance",
                "migrations",
                "migration_gb",
                "score",
              ] as const
            ).map((k) => (
              <tr key={k}>
                <td>
                  <HelpText title={k}>{k.replaceAll("_", " ")}</HelpText>
                </td>
                <td>{plan.before[k].toFixed(3)}</td>
                <td>{plan.after[k].toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!plan.comparable_workload && (
        <Notice>
          Served VM counts differ. This energy difference is not a like-for-like
          saving. Use Algorithm Comparison for equal workloads.
        </Notice>
      )}
      <h3>Planned actions</h3>
      {plan.actions.length ? (
        <table>
          <thead>
            <tr>
              <th>VM</th>
              <th>Source</th>
              <th>Destination</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {plan.actions.map((a) => (
              <tr key={a.vm_id}>
                <td>{a.vm_id}</td>
                <td>{a.from_server || "Unassigned"}</td>
                <td>{a.to_server}</td>
                <td>{a.kind}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No moves recommended under the current objectives and cooldown.</p>
      )}
      <ServerBars metrics={plan.after} />
    </>
  );
}
