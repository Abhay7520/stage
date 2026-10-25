import OptimizationWorkbench from "../../components/OptimizationWorkbench";
import { Title } from "../../components/ResearchUI";
export default function VMPlacement() {
  return (
    <>
      <Title
        title="VM Placement"
        description="Preview a complete allocation, inspect resource constraints and migration order, then apply it to the simulator."
      />
      <OptimizationWorkbench />
    </>
  );
}
