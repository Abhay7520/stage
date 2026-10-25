import OptimizationWorkbench from "../../components/OptimizationWorkbench";
import { Title, Notice } from "../../components/ResearchUI";
export default function VMConsolidation() {
  return (
    <>
      <Title
        title="VM Consolidation"
        description="Favor energy reduction while accounting for migration energy, pressure and full resource reservations."
      />
      <Notice>
        Empty servers enter a simulated sleep state. A lower server count is
        recommended only when the complete placement remains feasible. Existing
        VMs are never silently dropped.
      </Notice>
      <OptimizationWorkbench consolidation />
    </>
  );
}
