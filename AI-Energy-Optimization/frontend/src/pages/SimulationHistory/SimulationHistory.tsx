import { Explained, HelpText } from "../../components/help/Help";
import { useRemote } from "../../hooks/useRemote";
import type { History } from "../../types/optimization";
import { Title, ErrorBox } from "../../components/ResearchUI";
export default function SimulationHistory() {
  const { data, error, reload } = useRemote<History>("/optimization/history");
  return (
    <>
      <Title
        title="Simulation History"
        description="Persisted operations, interval decisions, migration actions and estimated outcomes."
      />
      <ErrorBox message={error} />
      <Explained action title="Refresh history">
        <button onClick={() => void reload()}>Refresh history</button>
      </Explained>
      <div className="panel">
        <p>
          Revision {data?.revision ?? "—"} · Interval {data?.tick ?? "—"}
        </p>
        {data?.events.length ? (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>
                    <HelpText title="Interval">Interval</HelpText>
                  </th>
                  <th>Action</th>
                  <th>
                    <HelpText title="Strategy">Strategy</HelpText>
                  </th>
                  <th>
                    <HelpText title="Moves">Moves</HelpText>
                  </th>
                  <th>
                    <HelpText title="After Wh">After Wh</HelpText>
                  </th>
                  <th>
                    <HelpText title="Source">Source</HelpText>
                  </th>
                </tr>
              </thead>
              <tbody>
                {[...data.events].reverse().map((e, i) => (
                  <tr key={i}>
                    <td>{e.tick}</td>
                    <td>{e.action}</td>
                    <td>{e.strategy || "—"}</td>
                    <td>
                      {e.moves
                        ?.map(
                          (a) =>
                            `${a.vm_id}: ${a.from_server || "pending"} → ${a.to_server}`,
                        )
                        .join("; ") || "—"}
                    </td>
                    <td>{e.after?.total_energy_wh.toFixed(3) || "—"}</td>
                    <td>{e.source || "simulation"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>
            No recorded actions. Create, allocate or optimize a VM to begin.
          </p>
        )}
      </div>
    </>
  );
}
