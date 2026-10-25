import { Explained, HelpText } from "../../components/help/Help";
import { useEffect, useState } from "react";
import { useRemote } from "../../hooks/useRemote";
import { request } from "../../services/client";
import type { SimulationState } from "../../types/simulation";
import type { Observation, Forecasts } from "../../types/optimization";
import { Title, Notice, ErrorBox } from "../../components/ResearchUI";
const columns = [
  "cpu_util_percent",
  "mem_util_percent",
  "net_in",
  "net_out",
  "disk_io_percent",
] as const;
const example = (): Observation[] =>
  Array.from({ length: 4 }, (_, i) => ({
    cpu_util_percent: 40 + i * 5,
    mem_util_percent: 50 + i * 2,
    net_in: 100 + i * 10,
    net_out: 80 + i * 5,
    disk_io_percent: 20 + i * 2,
  }));
export default function WorkloadIntelligence() {
  const { data: state, error: stateError } =
    useRemote<SimulationState>("/simulation/state");
  const [histories, setHistories] = useState<Record<string, Observation[]>>({});
  const [sources, setSources] = useState<Record<string, string>>({});
  const [selected, setSelected] = useState("");
  const [draft, setDraft] = useState<Observation[]>([]);
  const [source, setSource] = useState("user-entered");
  const [result, setResult] = useState<Forecasts | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [savedMessage, setSavedMessage] = useState("");
  useEffect(() => {
    request<{
      histories: Record<string, Observation[]>;
      sources: Record<string, string>;
    }>("/intelligence/histories")
      .then((d) => {
        setHistories(d.histories);
        setSources(d.sources);
      })
      .catch((e) => setError(String(e)));
  }, []);
  function choose(id: string) {
    setDirty(false);
    setSavedMessage("");
    setSelected(id);
    setDraft(histories[id]?.slice(-4) || []);
    setSource(sources[id] || "user-entered");
    setResult(null);
  }
  async function forecast(all = false) {
    setBusy(true);
    setResult(null);
    setSavedMessage("");
    setError("");
    try {
      if (!all) {
        const next = { ...histories, [selected]: draft };
        const r = await request<Forecasts>("/intelligence/forecast", {
          histories: { [selected]: draft },
          source,
        });
        setHistories(next);
        setSources({ ...sources, [selected]: source });
        setResult(r);
        setDirty(false);
        setSavedMessage(
          `Saved your ${source} readings for ${selected}. Forecasts now use these values. Preview placement again to use the updated demand.`,
        );
      } else setResult(await request<Forecasts>("/intelligence/forecasts"));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Title
        title="Workload Intelligence"
        description="Save ordered CPU, RAM, network and disk observations per VM; forecast the next interval and aggregate server demand."
      />
      <Notice>
        Training uses an aggregated trace without timestamps or VM IDs. VM-level
        predictions are experimental transfers. No histories are invented unless
        you choose Load synthetic example.
      </Notice>
      <ErrorBox message={error || stateError} />
      {dirty && (
        <p className="data-feedback unsaved" role="status">
          Unsaved readings or source changes. Save & forecast VM to update
          predictions and optimization inputs.
        </p>
      )}
      {savedMessage && (
        <p className="data-feedback" role="status">
          {savedMessage}
        </p>
      )}
      <fieldset className="workload-editor" disabled={busy}>
        <div className="panel">
          <div className="actions">
            <Explained title="VM">
              <label>
                VM
                <select
                  aria-label="VM"
                  value={selected}
                  onChange={(e) => choose(e.target.value)}
                >
                  <option value="">Select a VM</option>
                  {state?.vms.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.id} — {v.name}
                    </option>
                  ))}
                </select>
              </label>
            </Explained>
            <Explained title="Observation source">
              <label>
                Observation source
                <select
                  aria-label="Observation source"
                  value={source}
                  onChange={(e) => {
                    setDirty(true);
                    setSavedMessage("");
                    setSource(e.target.value);
                    setResult(null);
                  }}
                >
                  {["user-entered", "measured", "synthetic"].map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </select>
              </label>
            </Explained>
            <Explained action title="Load synthetic example">
              <button
                disabled={!selected || busy}
                onClick={() => {
                  setDirty(true);
                  setSavedMessage("");
                  setDraft(example());
                  setSource("synthetic");
                  setResult(null);
                }}
              >
                Load synthetic example
              </button>
            </Explained>
            <Explained action title="Enter four readings">
              <button
                disabled={!selected || busy}
                onClick={() => {
                  setDirty(true);
                  setSavedMessage("");
                  setDraft(
                    Array.from({ length: 4 }, () => ({
                      cpu_util_percent: 0,
                      mem_util_percent: 0,
                      net_in: 0,
                      net_out: 0,
                      disk_io_percent: 0,
                    })),
                  );
                  setSource("user-entered");
                  setResult(null);
                }}
              >
                Enter four readings
              </button>
            </Explained>
          </div>
          {draft.length > 0 && (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Oldest → newest</th>
                    {columns.map((c) => (
                      <th key={c}>
                        <HelpText title={String(c)}>{c}</HelpText>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {draft.map((row, i) => (
                    <tr key={i}>
                      <td>T-{3 - i}</td>
                      {columns.map((c) => (
                        <td key={c}>
                          <input
                            aria-label={`${c} interval ${i + 1}`}
                            type="number"
                            min={0}
                            max={c.includes("percent") ? 100 : undefined}
                            value={row[c]}
                            onChange={(e) => {
                              setDirty(true);
                              setSavedMessage("");
                              if (source === "synthetic")
                                setSource("user-entered");
                              setDraft(
                                draft.map((r, j) =>
                                  i === j
                                    ? { ...r, [c]: Number(e.target.value) }
                                    : r,
                                ),
                              );
                              setResult(null);
                            }}
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div className="actions">
            <Explained action title="Save & forecast VM">
              <button
                disabled={!selected || draft.length < 4 || busy}
                onClick={() => void forecast()}
              >
                Save & forecast VM
              </button>
            </Explained>
            <Explained action title="Forecast all saved histories">
              <button
                disabled={busy || dirty}
                onClick={() => void forecast(true)}
              >
                Forecast all saved histories
              </button>
            </Explained>
          </div>
        </div>
      </fieldset>
      {result && (
        <>
          <div className="server-grid">
            {result.vm_forecasts.map((f) => (
              <article className="panel" key={f.vm_id}>
                <h3>{f.vm_name}</h3>
                <p>
                  CPU: {f.predicted_cpu_percent.toFixed(1)}% ·{" "}
                  {f.estimated_cpu_demand_vcpu.toFixed(2)} vCPU
                </p>
                <p>
                  RAM: {f.predicted_memory_percent.toFixed(1)}% ·{" "}
                  {f.estimated_memory_demand_gb.toFixed(2)} GB
                </p>
                <p>{f.resource_risk}</p>
                <small>
                  {result.sources[f.vm_id]} / CPU {f.cpu_strategy} / RAM{" "}
                  {f.memory_strategy}
                </small>
              </article>
            ))}
          </div>
          <div className="panel">
            <h3>Server forecasts</h3>
            {result.server_forecasts.map((s) => (
              <p key={s.server_id}>
                {s.server_name}:{" "}
                {s.complete
                  ? `CPU ${s.predicted_cpu_percent.toFixed(1)}% / RAM ${s.predicted_memory_percent.toFixed(1)}%`
                  : "Incomplete histories"}
              </p>
            ))}
            <p>
              Missing histories: {result.missing_vm_ids.join(", ") || "None"}
            </p>
          </div>
        </>
      )}
    </>
  );
}
