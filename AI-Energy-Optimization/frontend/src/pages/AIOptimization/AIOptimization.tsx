import { Explained } from "../../components/help/Help";
import { useState } from "react";
import OptimizationWorkbench from "../../components/OptimizationWorkbench";
import LegacyOptimization from "./LegacyOptimization";
import { Title, Notice } from "../../components/ResearchUI";
export default function AIOptimization() {
  const [lab, setLab] = useState(false);
  return (
    <>
      <Title
        title="Multi-Objective Optimization"
        description="Explore energy, forecast pressure, workload balance and migration trade-offs in one pipeline."
      />
      <OptimizationWorkbench />
      <Explained action title="original single-host energy experiment">
        <button onClick={() => setLab(!lab)}>
          {lab ? "Hide" : "Open"} original single-host energy experiment
        </button>
      </Explained>
      {lab && (
        <>
          <Notice>
            Legacy model scenario: changes to CPU utilization are hypothetical
            input changes, not a physical CPU-cap control model. Estimated
            savings do not prove real allocation savings. The workload and
            energy datasets are independent.
          </Notice>
          <LegacyOptimization />
        </>
      )}
    </>
  );
}
