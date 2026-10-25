export interface HelpSection {
  heading: string;
  text?: string;
  steps?: string[];
}
export interface HelpContent {
  title: string;
  summary: string;
  sections: HelpSection[];
}
const section = (heading: string, text: string): HelpSection => ({
  heading,
  text,
});
const steps = (items: string[]): HelpSection => ({
  heading: "What to do",
  steps: items,
});
const simulated = section(
  "What is simulated?",
  "Servers, VM placements and migrations are virtual configurations in this application. Power, migration cost and resource-pressure risk are estimates. Nothing here starts, moves or switches off a real cloud server.",
);
const workflowSteps = [
  "Configure capacity in Data Center Simulator: create servers and VMs, then allocate VMs where both CPU and RAM reservations fit.",
  "Enter your own observations in Workload Intelligence: choose a VM, enter four readings from oldest to newest, then Save & forecast VM. Repeat for every VM you want to model.",
  "Predict demand: the saved readings feed CPU and RAM forecasting, then VM demand is aggregated by server. Missing histories are shown explicitly.",
  "Preview placement or consolidation: the optimizer evaluates capacity-safe allocations using demand, energy, pressure, balance and migration cost. Review the before/after values and actions.",
  "Apply the preview: the accepted plan updates the shared simulated allocation. Re-preview after changing readings or topology.",
  "Compare and adapt: compare static, first fit, best fit and predictive strategies; optionally advance intervals with saved data or explicitly selected synthetic fluctuations.",
  "Inspect evidence: Energy Analytics shows current estimates; Simulation History records decisions; Reports exports the state and comparative results.",
];
export const pageHelp: Record<string, HelpContent> = {
  Dashboard: {
    title: "Dashboard · overall project workflow",
    summary:
      "Start here to understand the complete path from your data to a simulated resource-allocation decision.",
    sections: [
      { heading: "Overall project workflow", steps: workflowSteps },
      section(
        "What the dashboard shows",
        "Server and VM counts, assigned versus pending VMs, and CPU/RAM reservations from the shared saved simulation. The bars show reserved resources, not live measurements.",
      ),
      section(
        "When you enter your own data",
        "Your saved VM readings are used for forecasts and the optimizer’s demand estimates. Creating a server or VM changes the available topology and capacity. Return here or refresh to see the saved changes.",
      ),
      simulated,
    ],
  },
  "Resource Monitor": {
    title: "Resource Monitor · original model laboratory",
    summary:
      "Try the original single-host CPU and energy models using editable input values.",
    sections: [
      steps([
        "Replace the four example workload observations with your readings.",
        "Enter the separate energy-model inputs with matching units.",
        "Click Run AI Analysis and inspect the results. Editing inputs clears affected recommendations.",
      ]),
      section(
        "How to interpret it",
        "This laboratory is separate from the per-VM simulation histories. Use Workload Intelligence to save readings that guide VM placement. Workload and energy datasets are independent; the single-host CPU-input scenario does not prove real CPU-control savings.",
      ),
      simulated,
    ],
  },
  "AI Optimization": {
    title: "AI Optimization · multiple objectives",
    summary:
      "Choose how much to prioritize energy, resource pressure, workload balance and migration cost.",
    sections: [
      steps([
        "Save VM histories in Workload Intelligence, or use the disclosed conservative fallback for missing histories.",
        "Select a strategy, interval, weights and power assumptions.",
        "Preview the plan. Compare before/after metrics and the ordered actions.",
        "Apply only the preview you reviewed. Changing options clears the preview.",
      ]),
      section(
        "How your data changes the result",
        "CPU/RAM predictions change estimated demand and candidate scores. Actual VM reservations and server capacities remain hard constraints. A different input can produce the same placement when constraints or trade-offs still favor it.",
      ),
      simulated,
    ],
  },
  "Data Center Simulator": {
    title: "Data Center Simulator · build your scenario",
    summary:
      "Create your own virtual servers and VMs, then allocate or migrate them safely.",
    sections: [
      steps([
        "Add a server with a unique ID and positive vCPU/RAM capacity.",
        "Create a VM with a unique ID and its full CPU/RAM reservation.",
        "Allocate a pending VM to a server, or migrate an assigned VM to another server.",
        "Use Workload Intelligence to enter that VM’s observed utilization.",
      ]),
      section(
        "What happens with your values",
        "Counts, remaining capacity and reservation bars recalculate after accepted operations. Insufficient CPU or RAM rejects the action and leaves the current placement unchanged. Reset deliberately restores the example topology and clears saved histories.",
      ),
      simulated,
    ],
  },
  "Workload Intelligence": {
    title: "Workload Intelligence · use your own readings",
    summary:
      "Enter a VM’s ordered resource observations to estimate demand for the next observation interval.",
    sections: [
      steps([
        "Select a VM. Choose Enter four readings for your own data, or explicitly load a synthetic example.",
        "Fill CPU %, RAM %, network in/out and disk I/O %, oldest first. Percentage values must be 0–100; network values must be nonnegative.",
        "Select the observation source honestly. Save & forecast VM sends your values to the backend.",
        "Repeat for other VMs, then forecast all saved histories. Preview placement after saving updated readings.",
      ]),
      section(
        "What the result means",
        "Predicted utilization × the VM’s reservation gives estimated demand in vCPU or GB. These are predictions, not new reservations. Some changed inputs may produce similar predictions because tree models respond in learned ranges.",
      ),
      section(
        "Data limits",
        "Models were trained on an aggregated trace, so transfer to individual VMs is experimental. Raw network units must match the training source; do not label arbitrary units as verified measurements. Missing VM histories remain incomplete and use 100% demand in optimization.",
      ),
      simulated,
    ],
  },
  "VM Placement": {
    title: "VM Placement · choose a destination",
    summary:
      "Find and review a complete capacity-safe allocation for the current VM set.",
    sections: [
      steps([
        "Save your VM histories and create any new capacity or pending VMs.",
        "Click Preview placement and inspect every proposed destination.",
        "Check before/after energy, pressure, served VM count and migration cost.",
        "Apply preview to change the shared simulation.",
      ]),
      section(
        "Why a move may be rejected",
        "CPU and RAM must both fit, existing VMs cannot be omitted, and migrations need room on their destinations. A stale preview, cooldown or bounded-search limit can also prevent an operation.",
      ),
      simulated,
    ],
  },
  "VM Consolidation": {
    title: "VM Consolidation · reduce idle capacity",
    summary:
      "Explore whether your VMs can run on fewer servers without violating reservations.",
    sections: [
      steps([
        "Enter your workload and inspect the current allocation.",
        "Preview consolidation using the energy-focused preset, or adjust its weights.",
        "Look for empty servers marked sleep and inspect the migration overhead.",
        "Apply if the proposed trade-off fits your scenario.",
      ]),
      section(
        "A valid no-change result",
        "The optimizer may retain the current allocation when migration costs, cooldown, pressure or capacity outweigh estimated savings. Consolidation does not guarantee fewer servers on every dataset.",
      ),
      simulated,
    ],
  },
  "Energy Analytics": {
    title: "Energy Analytics · read the estimates",
    summary:
      "Understand the analytical energy estimate for the current saved allocation and forecast demand.",
    sections: [
      steps([
        "Save your readings and apply any chosen allocation.",
        "Open this page to inspect estimated interval Wh, server W and demand bars.",
        "Compare active and sleeping servers. Read the declared power assumptions.",
      ]),
      section(
        "Units and assumptions",
        "W is estimated power at a point; Wh is energy over an interval. This page uses the documented default uniform power profile. Custom preview assumptions apply to that preview; they do not calibrate physical server power.",
      ),
      simulated,
    ],
  },
  "Optimization Comparison": {
    title: "Optimization Comparison · equal workloads",
    summary:
      "Compare alternative allocation strategies using the same topology, demand and served VM set.",
    sections: [
      steps([
        "Save your custom VM histories and topology.",
        "Run controlled comparison. The comparison does not apply any plan.",
        "Compare total Wh, active servers, migrations and pressure together; the lowest-energy strategy may have other costs.",
      ]),
      section(
        "Fairness and results",
        "Pending VMs are placed consistently before all methods are compared. Every method uses the same workload; infeasible methods show a reason. New inputs change the comparison when they change predictions, capacity or costs. A negative saving means higher estimated energy than static.",
      ),
      simulated,
    ],
  },
  "Adaptive Optimization": {
    title: "Adaptive Optimization · successive intervals",
    summary:
      "Advance the saved simulation and explore how allocations react to changing demand.",
    sections: [
      steps([
        "For your own readings, first save them in Workload Intelligence and select Saved observations unchanged here.",
        "Select adaptive predictive search or static allocation.",
        "Advance one interval. Review the applied allocation and look at Simulation History.",
        "To demonstrate fluctuations, deliberately select Seeded synthetic fluctuations.",
      ]),
      section(
        "Protect your data",
        "Saved-observation mode does not collect new measurements or alter the histories. Synthetic mode generates and saves new example readings, marks them synthetic and can replace the provenance of your saved histories. Use it only when that is intended.",
      ),
      section(
        "Why VMs may stay put",
        "A two-interval migration cooldown and minimum improvement threshold discourage repeated unnecessary moves. Static mode keeps the allocation unchanged.",
      ),
      simulated,
    ],
  },
  "Simulation History": {
    title: "Simulation History · trace decisions",
    summary:
      "Inspect saved operations, optimization decisions and before/after estimates.",
    sections: [
      steps([
        "Create, allocate, save workload data or advance an interval.",
        "Open or refresh this page to view the recorded events.",
        "Read the interval, strategy, migration actions, source and estimated outcome.",
      ]),
      section(
        "Persistence",
        "History survives normal backend restarts and browser reloads. Reset Simulation intentionally clears it. A recorded interval is a simulation step, not a live monitoring timestamp.",
      ),
      simulated,
    ],
  },
  Reports: {
    title: "Reports · export your scenario",
    summary:
      "Download the current saved scenario and inspect reproducible model evaluation evidence.",
    sections: [
      steps([
        "Save your readings and run the operations you want to document.",
        "Download JSON report for topology, provenance, comparison and history.",
        "Download comparison CSV for a spreadsheet-friendly summary.",
      ]),
      section(
        "Scenario results versus model evaluation",
        "Scenario exports react to your saved data. Training/evaluation metrics shown here come from the supplied fixed holdout experiments; entering new readings performs inference and does not retrain the models or change those benchmark scores.",
      ),
      simulated,
    ],
  },
};
const terms: Record<string, [string, string?]> = {
  cpu_util_percent: [
    "CPU utilization (%)",
    "Enter how busy the VM CPU was during each observation, from 0 to 100. This is a utilization fraction of its reserved vCPU, not a vCPU count.",
  ],
  mem_util_percent: [
    "RAM utilization (%)",
    "Enter used RAM as 0–100% of the VM’s reserved memory. For example, 50% of 8 GB estimates 4 GB of demand.",
  ],
  net_in: [
    "Network in",
    "Enter nonnegative incoming-network readings in the same raw units as the training trace. The supplied trace does not document a reliable conversion to Mbps.",
  ],
  net_out: [
    "Network out",
    "Enter nonnegative outgoing-network readings in the same raw units as the training trace.",
  ],
  disk_io_percent: [
    "Disk I/O (%)",
    "Enter observed disk I/O utilization from 0 to 100. It is an input to workload prediction, not a disk-capacity reservation.",
  ],
  strategy: [
    "Allocation strategy",
    "Predictive uses model-informed constrained beam search. First fit chooses the first feasible destination; best fit favors a tighter CPU fit. All must respect full CPU/RAM reservations.",
  ],
  interval_minutes: [
    "Interval (minutes)",
    "Choose the simulation duration used to turn W into Wh. For example, 120 W for 5 minutes is 10 Wh. Changing it changes energy accounting and cost trade-offs, not the measurement frequency of your data.",
  ],
  energy_weight: [
    "Energy weight",
    "A larger value gives estimated energy more influence in the objective. It does not guarantee a lower-energy plan because capacity, cooldown and other objectives still apply.",
  ],
  risk_weight: [
    "Pressure weight",
    "A larger value penalizes predicted CPU/RAM demand close to the pressure threshold. This is a resource-pressure proxy, not measured SLA violation probability.",
  ],
  balance_weight: [
    "Balance weight",
    "Increase this to penalize uneven predicted pressure among active servers. It can favor spreading workloads at the cost of extra active-server energy.",
  ],
  migration_weight: [
    "Migration weight",
    "Increase this to discourage moving existing VMs. It weights moved RAM relative to the total reserved VM RAM, in addition to estimated migration energy.",
  ],
  headroom: [
    "Forecast headroom",
    "A fraction added when assessing pressure risk. Enter 0.10 for a 10-percentage-point margin. It changes the risk score, not a server’s physical capacity.",
  ],
  idle_watts: [
    "Server idle W",
    "Assumed active-server base power when demand is near zero. It must be positive and no higher than peak power. It is not a sensor reading.",
  ],
  peak_watts: [
    "Server peak W",
    "Assumed maximum active power per server. Must be at least idle power. All simulated servers use this same profile in the current model.",
  ],
  sleep_watts: [
    "Server sleep W",
    "Assumed power for an empty sleeping server. Enter a nonnegative value no higher than idle power. Real wake-up energy and delay are not modeled.",
  ],
  migration_wh_per_gb: [
    "Migration Wh / GB",
    "Assumed migration energy for every GB of moved reserved RAM. Example: 8 GB × 0.05 Wh/GB = 0.4 Wh.",
  ],
  preview: [
    "Preview a plan",
    "Calculate destinations and before/after estimates without changing saved allocation. Review the actions, served VM count, costs and pressure before applying.",
  ],
  "apply preview": [
    "Apply the reviewed plan",
    "Save the previewed allocation into the shared simulation. A topology/history change can make its revision stale; generate a new preview in that case.",
  ],
  "reset simulation": [
    "Reset the scenario",
    "Restore the supplied demonstration servers and VMs, clearing saved workload readings, provenance and decision history. This deliberately discards your current simulated scenario.",
  ],
  "allocate vm": [
    "Allocate a pending VM",
    "Choose an unassigned VM and destination server. Both full CPU and RAM reservations must fit. An accepted allocation updates the shared state.",
  ],
  "migrate vm": [
    "Migrate an assigned VM",
    "Choose an already assigned VM and a different server. The destination must have spare CPU/RAM before the source placement is released. This is a simulated move.",
  ],
  "add server": [
    "Add a physical server",
    "Create a virtual capacity pool using a unique ID, name, positive vCPU capacity and positive RAM capacity in GB. It does not create real infrastructure.",
  ],
  "create vm": [
    "Create a virtual machine",
    "Create a pending VM with a unique ID and positive CPU/RAM reservations. Allocate it afterward, then save its observed utilization in Workload Intelligence.",
  ],
  "save & forecast vm": [
    "Save your data and forecast",
    "Validate and save the selected VM’s last four readings, then run the trained CPU/RAM predictors. Saved values feed later placement and comparison requests. This does not retrain the models.",
  ],
  "forecast all saved histories": [
    "Forecast all saved VMs",
    "Read each VM’s saved history and aggregate forecasts by current server assignment. Unsaved edits are not part of this request; save them first.",
  ],
  "load synthetic example": [
    "Load an example",
    "Fill the editor with illustrative values. They are explicitly synthetic and must not be presented as real VM measurements. Nothing is saved until you choose Save & forecast VM.",
  ],
  "enter four readings": [
    "Enter your own observations",
    "Open four editable rows, oldest first. Replace the starting zero values with your observations, check units and save to generate predictions.",
  ],
  "observation source": [
    "Observation source",
    "Choose user-entered for manual input, measured only for your actual observations, or synthetic for examples. This is your provenance label; the app cannot independently verify it.",
  ],
  "workload source": [
    "Adaptive workload source",
    "Saved observations unchanged uses your saved readings as-is. Synthetic fluctuations generate and save new example values, replacing provenance with synthetic.",
  ],
  seed: [
    "Synthetic random seed",
    "An integer controlling reproducible synthetic fluctuations. It affects generated examples only; saved-observation mode does not use it to change your data.",
  ],
  allocation: [
    "Adaptive or static allocation",
    "Adaptive predictive search can move VMs when its trade-offs improve. Static keeps placement unchanged, making it a useful reference.",
  ],
  advance: [
    "Advance one interval",
    "Advance the simulation tick and apply the selected method. Saved-observation mode keeps your readings; synthetic mode changes and saves generated readings. Cooldown may prevent immediate repeat migrations.",
  ],
  "run controlled comparison": [
    "Compare strategies",
    "Evaluate all strategies from one shared complete workload. This request reads your saved state and does not apply any alternative allocation.",
  ],
  "refresh state": [
    "Refresh saved state",
    "Reload server/VM configuration and reservation totals from the backend. It does not reset the scenario.",
  ],
  "refresh history": [
    "Refresh recorded decisions",
    "Reload operations and interval decisions from persistent state.",
  ],
  "download json report": [
    "Export the current scenario",
    "Download saved topology, data provenance, comparisons and decisions as JSON. Unsaved form edits are excluded.",
  ],
  "download comparison csv": [
    "Export comparison data",
    "Download the current equal-workload strategy comparison as a CSV file for Excel or another analysis tool.",
  ],
  "run ai analysis": [
    "Run the original model laboratory",
    "Run CPU prediction, separate SWEAT energy inference and the original exploratory CPU-input scenario using the form values. This lab does not save per-VM histories into the simulator.",
  ],
  "estimated energy": [
    "Estimated energy",
    "Energy in Wh over the selected interval, including migration energy when the result represents a proposed plan. It is analytical, not measured electricity use.",
  ],
  total_energy_wh: [
    "Total energy (Wh)",
    "Analytical interval energy plus migration-energy estimate. Only interpret a before/after saving when both serve the same VM workload.",
  ],
  energy_wh: [
    "Server energy (Wh)",
    "Analytical server power multiplied by interval hours; excludes migration energy.",
  ],
  migration_energy_wh: [
    "Migration energy (Wh)",
    "Extra estimated energy from moved RAM × the configured Wh/GB assumption.",
  ],
  active_servers: [
    "Active servers",
    "Servers with at least one assigned VM. Empty servers are counted as simulated sleep.",
  ],
  sla_pressure_proxy: [
    "Pressure proxy",
    "A penalty for predicted CPU/RAM pressure near the configured threshold, including headroom. Lower means less modeled pressure. It is not a measured SLA failure rate.",
  ],
  imbalance: [
    "Workload imbalance",
    "Variance of the maximum CPU/RAM pressure across active servers. Smaller means those servers have more similar predicted pressure.",
  ],
  migrations: [
    "Migrations",
    "Number of already assigned VMs moved to a different server by this plan. Initial assignment of pending VMs is not a migration.",
  ],
  migration_gb: [
    "Moved RAM (GB)",
    "Sum of full reserved RAM for migrated VMs; used to estimate migration energy and duration.",
  ],
  score: [
    "Optimization score",
    "Weighted energy, pressure, balance and migration objective. Lower is preferred under the same weights, assumptions and served workload. This is not model accuracy.",
  ],
  scheduled_vms: [
    "Scheduled VMs",
    "Number of VMs with a destination in the allocation. Fewer served VMs must not be used to claim an energy saving.",
  ],
  servers: [
    "Server count",
    "Number of simulated physical servers in your saved topology. Create capacity in Data Center Simulator.",
  ],
  vms: [
    "VM count",
    "Number of simulated VMs, including pending VMs. Create and allocate them in Data Center Simulator.",
  ],
  assigned: [
    "Assigned VMs",
    "VMs currently placed on a simulated server. Their full reservations consume its available capacity.",
  ],
  unassigned: [
    "Pending VMs",
    "VMs without a server. Allocate them manually or include them in a complete optimization plan.",
  ],
  "reserved cpu": [
    "Reserved CPU",
    "The full vCPU amounts allocated to VMs divided by server vCPU capacity. This is not measured CPU utilization and does not shrink when a forecast is low.",
  ],
  "reserved ram": [
    "Reserved RAM",
    "The full allocated VM memory divided by server RAM capacity. Forecast demand is a separate estimated quantity.",
  ],
  "cpu capacity (vcpu)": [
    "Server CPU capacity",
    "Enter a positive number of available virtual CPU units. The sum of assigned VM CPU reservations cannot exceed it.",
  ],
  "memory capacity (gb)": [
    "Server memory capacity",
    "Enter a positive RAM capacity in GB. The sum of assigned VM RAM reservations cannot exceed it.",
  ],
  "required vcpu": [
    "VM CPU reservation",
    "Enter how many vCPU units this VM reserves. This stays a hard requirement even when predicted utilization is low.",
  ],
  "required memory (gb)": [
    "VM memory reservation",
    "Enter the VM’s reserved RAM in GB. For example, 8 GB at 50% utilization estimates 4 GB demand, while still reserving 8 GB.",
  ],
  "destination server": [
    "Destination server",
    "Choose where to place this VM. CPU and RAM must both have enough spare capacity; migrating to the current server is invalid.",
  ],
  vm: [
    "Choose a VM",
    "Select the VM whose observations or allocation you want to work with. IDs refer to your saved simulated topology.",
  ],
  "server id": [
    "Server ID",
    "Use a unique identifier such as S4. Only letters, numbers, underscore and hyphen are accepted.",
  ],
  "vm id": [
    "VM ID",
    "Use a unique identifier such as VM7. Only letters, numbers, underscore and hyphen are accepted.",
  ],
  "server name": [
    "Server name",
    "Enter a nonempty display name so you can recognize this simulated server.",
  ],
  "vm name": [
    "VM name",
    "Enter a nonempty display name for this VM, such as Database or Analytics worker.",
  ],
  cpu: [
    "Predicted CPU pressure",
    "Estimated VM demand is aggregated and divided by server capacity. These percentages are forecasts, while reservation bars show hard allocated resources.",
  ],
  ram: [
    "Predicted RAM pressure",
    "Estimated RAM demand is aggregated and divided by server capacity. It is a prediction rather than a measured live value.",
  ],
  "cpu frequency (ghz)": [
    "CPU frequency (GHz)",
    "Enter the source machine’s CPU frequency in GHz for the separate energy regressor. This field does not perform real DVFS control.",
  ],
  "memory usage (gb)": [
    "Energy-model memory (GB)",
    "Enter memory used in GB for the SWEAT energy-model input. It is separate from a simulated VM reservation.",
  ],
  "disk writes": [
    "Disk writes",
    "Enter nonnegative disk write counts during the source measurement interval, matching the energy training feature.",
  ],
  "disk reads": [
    "Disk reads",
    "Enter nonnegative disk read counts during the source measurement interval, matching the energy training feature.",
  ],
};
Object.assign(terms, {
  "cpu mean %": [
    "CPU mean (%)",
    "Average CPU utilization during the energy observation interval. Enter a nonnegative value in the source feature’s percentage units.",
  ],
  "cpu max %": [
    "CPU maximum (%)",
    "Highest CPU utilization in that same interval. Keep it at least as large as the minimum and mean.",
  ],
  "cpu min %": [
    "CPU minimum (%)",
    "Lowest CPU utilization in the same interval. Keep it no greater than the mean and maximum.",
  ],
  "cpu std": [
    "CPU standard deviation",
    "Variation in CPU utilization within the energy observation interval. Enter a nonnegative standard deviation, not a percentage of allocated vCPU.",
  ],
  "cpu median %": [
    "CPU median (%)",
    "Middle CPU utilization value in the same energy observation interval. Use the measured/source statistic rather than a VM reservation.",
  ],
  "predicted workload": [
    "Predicted workload",
    "The CPU regressor’s estimate for the next observation. This is inference from your inputs, not a measured future value.",
  ],
  "predicted energy": [
    "Predicted energy (J)",
    "The separate SWEAT regressor estimates joules per source measurement interval. Its interval is not assumed to match the placement simulator’s five-minute interval.",
  ],
  "estimated saving": [
    "Estimated scenario saving",
    "An exploratory difference between model-input scenarios. It is not a guarantee that changing a real CPU allocation saves this energy.",
  ],
  "estimated energy saving": [
    "Estimated energy saving",
    "Read only against a stated baseline serving the same workload. Negative values mean more energy than that baseline. Original model-lab savings are exploratory CPU-input scenarios.",
  ],
  "saving %": [
    "Saving versus static (%)",
    "Percentage energy reduction relative to static for the same served workload and interval. Migration energy is included. A negative value means the alternative uses more energy.",
  ],
  source: [
    "Data source",
    "Indicates whether a recorded value came from saved user input, synthetic generation or the simulation. A provenance label does not independently verify measurements.",
  ],
  interval: [
    "Simulation interval",
    "A successive simulation step, not necessarily a real wall-clock timestamp. Observations should still be entered in oldest-to-newest order.",
  ],
  "after wh": [
    "Estimated energy after the decision",
    "Analytical interval Wh after the recorded decision, including migration energy when applicable. Compare with its before metric and served workload.",
  ],
  retry: [
    "Retry loading simulation",
    "Ask the backend for the saved simulation again. Check that the backend is running if loading still fails.",
  ],
  "current allocation": [
    "Current CPU-input scenario",
    "The current CPU value in the original model experiment. This input is not a real hypervisor CPU-cap setting.",
  ],
  "predicted demand": [
    "Predicted CPU demand",
    "Expected next CPU utilization from the original workload model. Resource allocation decisions in the integrated pipeline use per-VM CPU and RAM estimates.",
  ],
  "ai recommendation": [
    "Exploratory CPU recommendation",
    "The original model lab compares hypothetical CPU-input scenarios. Use the integrated placement preview to review capacity-safe VM destinations.",
  ],
  "energy saving": [
    "Exploratory energy difference",
    "Difference between the original lab’s model-input scenarios. It does not validate physical CPU control or actual cloud energy savings.",
  ],
  "recommended cpu": [
    "Recommended CPU-input scenario",
    "A candidate CPU percentage selected by the original lab’s scenario search, not a command sent to a real server.",
  ],
});
const aliases: Record<string, string> = {
  active: "active_servers",
  moves: "migrations",
  "migration wh": "migration_energy_wh",
  pressure: "sla_pressure_proxy",
  "total wh": "total_energy_wh",
  "cpu frequency ghz": "cpu frequency (ghz)",
  "memory gb": "memory usage (gb)",
  "active servers": "active_servers",
  "pressure proxy": "sla_pressure_proxy",
  "allocated cpu": "reserved cpu",
  "allocated memory": "reserved ram",
  "physical servers": "servers",
  "virtual machines": "vms",
  "assigned vms": "assigned",
  "unassigned vms": "unassigned",
  "current cpu": "cpu_util_percent",
  "cpu %": "cpu_util_percent",
  "memory %": "mem_util_percent",
  "net in": "net_in",
  "net out": "net_out",
  "disk i/o %": "disk_io_percent",
  "interval (minutes)": "interval_minutes",
  "energy weight": "energy_weight",
  "pressure weight": "risk_weight",
  "migration weight": "migration_weight",
  "balance weight": "balance_weight",
  "forecast headroom": "headroom",
  "server idle w": "idle_watts",
  "server peak w": "peak_watts",
  "server sleep w": "sleep_watts",
  "migration wh / gb": "migration_wh_per_gb",
};
export function termHelp(label: string): HelpContent {
  const clean = label.trim().toLowerCase();
  let key = aliases[clean] || clean;
  if (key.startsWith("preview")) key = "preview";
  if (key.includes("advance") || key === "advancing…") key = "advance";
  if (key.includes("original model") || key.includes("original single-host"))
    return {
      title: label,
      summary:
        "Open or hide the preserved original single-host model experiment.",
      sections: [
        section(
          "How it differs",
          "This lab uses editable CPU/energy inputs but does not save VM histories. Use Workload Intelligence and placement for the integrated pipeline.",
        ),
      ],
    };
  if (key.startsWith("server id")) key = "server id";
  if (key.startsWith("vm id")) key = "vm id";
  const item = terms[key];
  return {
    title: item?.[0] || label,
    summary:
      item?.[1] ||
      "Inspect this value alongside the page guide and the declared data source.",
    sections: item
      ? []
      : [
          section(
            "Simulation context",
            "Results reflect your saved scenario and the current inputs. For predictions, save or run the relevant action after editing; values on a results screen are estimates, not live cloud measurements.",
          ),
        ],
  };
}
