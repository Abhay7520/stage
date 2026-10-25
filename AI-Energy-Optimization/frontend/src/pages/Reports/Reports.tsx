import { Explained } from "../../components/help/Help";
import { useState } from "react";
import { downloadReport } from "../../services/client";
import { useRemote } from "../../hooks/useRemote";
import { Title, Notice, ErrorBox } from "../../components/ResearchUI";
export default function Reports() {
  const { data, error } = useRemote<Record<string, unknown>>(
    "/reports/evaluation",
  );
  const [downloadError, setDownloadError] = useState("");
  async function save(path: string, name: string) {
    try {
      setDownloadError("");
      await downloadReport(path, name);
    } catch (e) {
      setDownloadError(e instanceof Error ? e.message : String(e));
    }
  }
  return (
    <>
      <Title
        title="Reports & Evidence"
        description="Export current simulation state, controlled comparisons, decision history and model evaluation."
      />
      <Notice>
        Exports contain simulation estimates and provenance. Evidence for
        research novelty against a selected paper still requires its exact
        method and experiment protocol.
      </Notice>
      <ErrorBox message={error || downloadError} />
      <div className="actions">
        <Explained action title="Download JSON report">
          <button
            onClick={() =>
              void save("/reports/snapshot", "simulation-report.json")
            }
          >
            Download JSON report
          </button>
        </Explained>
        <Explained action title="Download comparison CSV">
          <button
            onClick={() =>
              void save("/reports/comparison.csv", "algorithm-comparison.csv")
            }
          >
            Download comparison CSV
          </button>
        </Explained>
      </div>
      <div className="panel">
        <h3>Reproducible forecast evaluation</h3>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </>
  );
}
