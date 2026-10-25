import { useState } from "react";
import {
  Zap,
  Activity,
  Brain,
  Cpu,
  Gauge,
  Network,
  Layers,
  BarChart3,
  History,
  FileText,
  RefreshCw,
  Menu,
} from "lucide-react";
import { LegacyContext, useLegacyController } from "./hooks/useLegacy";
import Dashboard from "./pages/Dashboard/Dashboard";
import ResourceMonitor from "./pages/ResourceMonitor/ResourceMonitor";
import AIOptimization from "./pages/AIOptimization/AIOptimization";
import DataCenterSimulator from "./pages/DataCenterSimulator/DataCenterSimulator";
import WorkloadIntelligence from "./pages/WorkloadIntelligence/WorkloadIntelligence";
import VMPlacement from "./pages/VMPlacement/VMPlacement";
import VMConsolidation from "./pages/VMConsolidation/VMConsolidation";
import EnergyAnalytics from "./pages/EnergyAnalytics/EnergyAnalytics";
import OptimizationComparison from "./pages/OptimizationComparison/OptimizationComparison";
import AdaptiveOptimization from "./pages/AdaptiveOptimization/AdaptiveOptimization";
import SimulationHistory from "./pages/SimulationHistory/SimulationHistory";
import Reports from "./pages/Reports/Reports";
import { Notice, ErrorBox } from "./components/ResearchUI";
import { PageHelp } from "./components/help/Help";

const pages = [
  { name: "Dashboard", icon: Gauge, component: Dashboard },
  { name: "Resource Monitor", icon: Activity, component: ResourceMonitor },
  { name: "AI Optimization", icon: Brain, component: AIOptimization },
  {
    name: "Data Center Simulator",
    icon: Network,
    component: DataCenterSimulator,
  },
  { name: "Workload Intelligence", icon: Cpu, component: WorkloadIntelligence },
  { name: "VM Placement", icon: Layers, component: VMPlacement },
  { name: "VM Consolidation", icon: Layers, component: VMConsolidation },
  { name: "Energy Analytics", icon: Zap, component: EnergyAnalytics },
  {
    name: "Optimization Comparison",
    icon: BarChart3,
    component: OptimizationComparison,
  },
  {
    name: "Adaptive Optimization",
    icon: RefreshCw,
    component: AdaptiveOptimization,
  },
  { name: "Simulation History", icon: History, component: SimulationHistory },
  { name: "Reports", icon: FileText, component: Reports },
];
export default function App() {
  const legacy = useLegacyController();
  const [active, setActive] = useState(0);
  const [open, setOpen] = useState(false);
  const Page = pages[active].component;
  return (
    <LegacyContext.Provider value={legacy}>
      <div className="app">
        <aside className={`sidebar ${open ? "mobile-open" : ""}`}>
          <div className="brand">
            <div className="brand-icon">
              <Zap />
            </div>
            <div>
              <h2>GridOpt AI</h2>
              <span>Energy Intelligence</span>
            </div>
          </div>
          <nav>
            {pages.map(({ name, icon: Icon }, i) => (
              <button
                key={name}
                className={`nav-item ${active === i ? "active" : ""}`}
                onClick={() => {
                  setActive(i);
                  setOpen(false);
                }}
              >
                <Icon size={18} />
                {name}
              </button>
            ))}
          </nav>
          <div className="sidebar-footer">
            <div className="mode-label">
              <span className="status-dot" />
              Research simulation
            </div>
            <p>Forecast → place → consolidate → evaluate → adapt</p>
          </div>
        </aside>
        <main className="main">
          <header className="topbar">
            <div>
              <h1>AI Energy Optimization</h1>
              <p>Cloud Data Center Resource Management</p>
            </div>
            <button
              className="mobile-menu"
              aria-label="Toggle navigation"
              onClick={() => setOpen(!open)}
            >
              <Menu />
            </button>
          </header>
          <ErrorBox message={legacy.error} />
          {active === 1 && (
            <Notice>
              Original single-host prediction lab. The prefilled values are
              synthetic examples. Use Workload Intelligence to save per-VM
              histories for the integrated simulator.
            </Notice>
          )}
          <PageHelp page={pages[active].name} key={`help-${active}`} />
          <Page key={active} />
          <footer>
            <span>GridOpt AI · Integrated research prototype</span>
            <span>
              Simulated allocation · Explicit assumptions · Reproducible
              evidence
            </span>
          </footer>
        </main>
      </div>
    </LegacyContext.Provider>
  );
}
