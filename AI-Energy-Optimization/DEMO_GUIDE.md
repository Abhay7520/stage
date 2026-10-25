# Suggested demonstration

First click the Dashboard’s ⓘ button to open the overall workflow. Every page has its own guide, and smaller ⓘ buttons explain controls and results. See USER_GUIDANCE.md for details.

1. Open Dashboard. Identify the three demonstration servers, six VMs and one pending VM. Explain reservations versus actual utilization.
2. Open Data Center Simulator. Create a small VM and allocate it. Try a VM larger than a destination's RAM and show the rejection. Reset to the supplied demonstration topology before the remaining steps.
3. Open Workload Intelligence. Choose each VM, use **Load synthetic example**, then **Save & forecast VM**. State clearly that these are illustrative readings. Alternatively enter four actual readings and select their provenance.
4. Select **Forecast all saved histories**. Discuss CPU/RAM forecasts, warnings and aggregate server demand. Missing VM histories remain explicit.
5. Open VM Placement. Preview a full placement, inspect every action and both reservations, then apply. A pending VM is included in the plan; an increased served workload prevents a direct before/after savings claim.
6. Open Optimization Comparison. Run the comparison. Every strategy sees the same served VM set and demand. Compare interval energy including migration overhead, active servers, migration count and pressure proxy.
7. Open AI Optimization or VM Consolidation. Change weights or power assumptions and preview again. Look for trade-offs; a no-change plan is a valid outcome.
8. Open Adaptive Optimization. Choose seeded synthetic fluctuations and advance several intervals. Explain cooldown and why a server/VM may remain in its current placement.
9. Open Simulation History and inspect decisions. Reload the browser, or restart the backend, and show that the shared state survives.
10. Download JSON and CSV from Reports. For academic results, use the reproducible files in `experiments`, not hand-entered example outputs.

Original single-host analysis remains available in Resource Monitor and collapsible model-lab sections. It is an exploratory CPU-input energy scenario, not a physical CPU-control experiment.
