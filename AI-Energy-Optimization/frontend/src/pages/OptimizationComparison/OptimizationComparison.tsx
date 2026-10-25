import { Explained, HelpText } from "../../components/help/Help";
import { useState } from "react";
import { request } from "../../services/client";
import { defaultOptions } from "../../types/optimization";
import type { Comparison } from "../../types/optimization";
import { Title, Notice, ErrorBox } from "../../components/ResearchUI";
export default function OptimizationComparison() {
  const [data, setData] = useState<Comparison | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function run() {
    setBusy(true);
    setError("");
    try {
      setData(
        await request<Comparison>("/optimization/compare", defaultOptions),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Title
        title="Algorithm Comparison"
        description="Compare static, first fit, best fit and forecast-informed search on identical served workloads."
      />
      <Notice>
        These are conventional baselines, not a reproduction of a specific base
        paper. SLA pressure is a resource proxy, not measured application
        latency or SLA violations.
      </Notice>
      <ErrorBox message={error} />
      <Explained action title="Run controlled comparison">
        <button disabled={busy} onClick={() => void run()}>
          {busy ? "Evaluating…" : "Run controlled comparison"}
        </button>
      </Explained>
      {data && (
        <div className="panel">
          <p>{data.methodology}</p>
          <p>
            Missing histories (100% demand fallback):{" "}
            {data.missing_histories.join(", ") || "None"}
          </p>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>
                    <HelpText title="Strategy">Strategy</HelpText>
                  </th>
                  <th>
                    <HelpText title="Total Wh">Total Wh</HelpText>
                  </th>
                  <th>
                    <HelpText title="Saving %">Saving %</HelpText>
                  </th>
                  <th>
                    <HelpText title="Active">Active</HelpText>
                  </th>
                  <th>
                    <HelpText title="Moves">Moves</HelpText>
                  </th>
                  <th>
                    <HelpText title="Migration Wh">Migration Wh</HelpText>
                  </th>
                  <th>
                    <HelpText title="Pressure">Pressure</HelpText>
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.rows.map((r) => (
                  <tr key={r.strategy}>
                    <td>{r.strategy}</td>
                    {r.metrics ? (
                      <>
                        <td>{r.metrics.total_energy_wh.toFixed(3)}</td>
                        <td>{r.energy_saving_percent?.toFixed(2)}</td>
                        <td>{r.metrics.active_servers}</td>
                        <td>{r.metrics.migrations}</td>
                        <td>{r.metrics.migration_energy_wh.toFixed(3)}</td>
                        <td>{r.metrics.sla_pressure_proxy.toFixed(4)}</td>
                      </>
                    ) : (
                      <td colSpan={6}>{r.reason}</td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h3>Estimated interval energy including migrations</h3>
          {data.rows
            .filter((r) => r.metrics)
            .map((r) => (
              <div className="comparison-row" key={r.strategy}>
                <span>{r.strategy}</span>
                <progress
                  value={r.metrics!.total_energy_wh}
                  max={Math.max(
                    ...data.rows.map((x) => x.metrics?.total_energy_wh || 0),
                  )}
                />
                <strong>{r.metrics!.total_energy_wh.toFixed(2)} Wh</strong>
              </div>
            ))}
        </div>
      )}
    </>
  );
}
