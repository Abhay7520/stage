# MASTER PROJECT UPGRADE REQUIREMENTS

## Project Title

**AI-Based Energy Optimization for Cloud Data Center Resource Management Using Workload Prediction and Intelligent Resource Allocation**

## 1. Existing Project and Development Approach

I will provide my latest project ZIP, containing the implementation completed up to Phase 6.

You must:

- Extract and thoroughly analyze the entire existing project.
- Understand the current frontend, backend, datasets, trained ML models, APIs, simulation engine, and optimization algorithms.
- Preserve all existing working functionality.
- Fix existing bugs and incomplete features.
- Improve existing components wherever necessary.
- Continue development from Phase 6 through the final phase.
- Complete all remaining development in one integrated project upgrade rather than providing individual phases.
- Do not unnecessarily rebuild the application from scratch.

The goal is to produce a complete, functional, research-oriented final-year major project.

## 2. Mandatory Frontend Folder Structure

**Every sidebar navigation heading must have its own dedicated folder under `frontend/src/pages/`.**

Each folder must contain the page component and its related components, styles, and page-specific logic.

Example (LIKE BELOW BUT YOU CAN ADD MORE , DO THE SAME FOR ENTIRE PROJECT STRUCTURE INCLDUNF BACJKEND)

```text
frontend/
└── src/
    ├── pages/
    │   ├── Dashboard/
    │   │   ├── Dashboard.tsx
    │   │   ├── components/
    │   │   └── Dashboard.css
    │   │
    │   ├── ResourceMonitor/
    │   │   ├── ResourceMonitor.tsx
    │   │   ├── components/
    │   │   └── ResourceMonitor.css
    │   │
    │   ├── AIOptimization/
    │   │   ├── AIOptimization.tsx
    │   │   ├── components/
    │   │   └── AIOptimization.css
    │   │
    │   ├── DataCenterSimulator/
    │   │   ├── DataCenterSimulator.tsx
    │   │   ├── components/
    │   │   └── DataCenterSimulator.css
    │   │
    │   ├── WorkloadIntelligence/
    │   │   ├── WorkloadIntelligence.tsx
    │   │   ├── components/
    │   │   └── WorkloadIntelligence.css
    │   │
    │   ├── VMPlacement/
    │   ├── VMConsolidation/
    │   ├── EnergyAnalytics/
    │   ├── OptimizationComparison/
    │   ├── SimulationHistory/
    │   └── Reports/
    │
    ├── components/
    ├── services/
    ├── hooks/
    ├── types/
    ├── utils/
    ├── App.tsx
    └── main.tsx
```

The final sidebar navigation and folder names should be decided based on the actual features.

Requirements:

- One dedicated folder per sidebar page.
- Reusable components should be placed in shared component folders.
- API functions should be separated from UI code.
- Avoid massive single-file React components.
- Preserve the existing visual design while improving responsiveness, consistency, and navigation.
- All buttons, forms, charts, filters, and actions must perform meaningful functions.
- Remove dummy results and misleading placeholder information from operational screens.
- Clearly label intentionally simulated or example data.

## 3. Complete All Remaining Development Phases

Implement the remaining project phases, starting with improvements to Phase 6 and continuing through Phase 7, 8, 9, 10, 11, 12, 13, 14, or however many phases are genuinely required to complete the project.

The features must include:

### Phase 6 — Multi-VM and Multi-Server Simulation

- Physical server management.
- Virtual machine management.
- CPU and memory capacity tracking.
- VM allocation and migration.
- Capacity constraint validation.
- Server overload detection.
- Resource visualization.
- Simulation reset and state management.

### Phase 7 — Advanced Workload Intelligence

- AI-based CPU workload prediction.
- AI-based memory workload prediction.
- VM-level workload estimation.
- Server-level workload forecasting.
- Resource-demand prediction.
- Workload warnings.
- Proper model training and evaluation.

### Phase 8 — Intelligent VM Placement

- Energy-aware VM placement.
- Reinforcement learning or another justified intelligent optimization algorithm.
- Placement decisions based on predicted workloads and server capacity.
- Comparison with conventional allocation strategies.
- Prevention of invalid allocations.

### Phase 9 — Intelligent VM Consolidation

- Detect underutilized servers.
- Recommend VM migrations.
- Consolidate workloads onto fewer servers when feasible.
- Simulate idle or low-power server states.
- Account for migration overhead and resource constraints.
- Compare resource utilization before and after consolidation.

### Phase 10 — Multi-Objective Optimization

Optimize multiple objectives together:

- Energy consumption.
- Resource utilization.
- Application performance.
- SLA violation risk.
- Migration cost.
- Workload balance.
- Server capacity constraints.

Provide interpretable optimization recommendations with explanations and trade-offs.

### Phase 11 — Interactive Cloud Data Center Dashboard

- Visualize all servers and VMs.
- Monitor allocated and estimated utilized resources.
- Interactively select VM placement and migration decisions.
- Run simulated optimization.
- Display before-and-after resource allocation.
- Show optimization recommendations.
- Provide useful charts and resource status indicators.

### Phase 12 — Energy Analytics and Algorithm Comparison

- Energy prediction and estimation.
- Baseline versus AI optimization comparisons.
- Compare multiple allocation strategies.
- Energy usage and estimated energy savings.
- Resource utilization comparisons.
- SLA risk and migration overhead comparisons.
- Explain the evaluation methodology.

### Phase 13 — Adaptive Resource Optimization

- Reoptimization across successive simulation intervals.
- Adjust decisions according to updated predicted demand.
- Simulate workload fluctuations.
- Track changes in VM allocation.
- Compare adaptive and static allocation.
- Maintain decision history.
- Prevent unstable or unnecessary repeated migrations.

### Phase 14 — Final Integration, Validation, and Reporting

- Integrate frontend, backend, ML models, and simulator.
- Verify all API connections.
- Fix bugs and compatibility issues.
- Perform automated and integration testing.
- Test frontend build.
- Validate resource-allocation constraints.
- Produce experimental comparison results.
- Generate reports.
- Finalize project documentation.

Phases may be reorganized, merged, or expanded if the source-code audit reveals a more technically correct implementation sequence.

## 4. Research Gap Fulfillment — Highest Priority

**The completed project must go beyond the existing base-paper solution.**

The research gap involves the limitations of conventional or standalone VM placement techniques, particularly insufficient integration of:

- Predictive CPU and memory workload intelligence.
- Intelligent energy-aware VM placement.
- Multi-resource allocation.
- Dynamic VM consolidation.
- Migration-cost awareness.
- Multi-objective optimization.
- Continuous adaptive reoptimization.
- Interactive simulation.
- Comparative experimental evaluation.

Develop a unified optimization pipeline that connects these capabilities.

The system must demonstrate what the proposed approach adds compared with the selected research baseline.

Do not simply reproduce an existing Q-learning VM placement solution or rename conventional heuristics as AI.

Any claimed improvement must be supported by suitable experiments, baselines, and actual evaluation results.

## 5. Machine Learning and Dataset Requirements

- Review all existing datasets.
- Identify which dataset supports each ML task.
- Check data quality, feature definitions, units, and timestamps.
- Avoid incorrectly pairing unrelated workload and energy measurements.
- Prevent data leakage during training and evaluation.
- Reuse existing trained models when appropriate.
- Retrain or modify models where necessary and feasible.
- Save trained model artifacts and evaluation metrics.
- Compare AI predictions against appropriate baselines.
- Use realistic and documented energy-estimation assumptions.
- Clearly distinguish model predictions, simulated values, and measured data.
- Do not invent training accuracy, energy savings, or benchmark results.

## 6. Backend and Architecture Requirements

- Organize backend code into meaningful modules.
- Keep simulation logic independent of HTTP routes.
- Separate ML model inference from resource-allocation logic.
- Use validated API request and response schemas.
- Handle invalid operations and API errors properly.
- Provide consistent resource state across integrated features.
- Avoid losing simulated changes unexpectedly during normal usage.
- Keep the application extensible and maintainable.
- Preserve existing working APIs wherever possible.

## 7. Testing Requirements

Perform all feasible testing before delivering the updated project:

- Python unit tests.
- Backend API tests.
- ML inference tests.
- Resource capacity tests.
- Allocation and migration tests.
- Optimization constraint tests.
- Frontend build checks.
- Frontend and backend integration checks.
- Algorithm comparison tests.
- Regression testing of existing features.

Fix errors discovered during testing.

Clearly document anything that could not be tested, including environment-specific or deployment-dependent functionality.

## 8. Required Documentation

Include:

1. `README.md` — project overview, features, architecture, datasets, and technologies.
2. `SETUP.md` — exact Windows/VS Code installation and execution instructions.
3. `setup.py` or appropriate Python packaging configuration.
4. `requirements.txt` — Python dependencies.
5. Frontend package configuration.
6. `.env.example` — required environment variable names without secrets.
7. `TESTING.md` — test commands, results, and limitations.
8. `RESEARCH_GAP_MAPPING.md` — research gaps mapped to implementations and evidence.
9. `MODEL_EVALUATION.md` — datasets, methods, metrics, and model limitations.
10. `PHASE_IMPLEMENTATION.md` — completed features and corresponding project files.
11. `API_DOCUMENTATION.md` — endpoints and examples.

## 9. Final Deliverable

Provide **one updated, complete, downloadable ZIP file** containing the modified project.

The ZIP must include:

- Updated frontend.
- Updated backend.
- Existing and newly implemented optimization algorithms.
- ML training and inference code.
- Available trained model artifacts.
- Simulation modules.
- Automated tests.
- Required configuration files.
- Complete documentation.
- Research-gap mapping.
- Setup and execution instructions.

Also provide a brief summary indicating:

- Which features were completed.
- Which algorithms were implemented.
- Which research gaps were addressed.
- Which tests passed.
- Which limitations or outstanding tasks remain.

## 10. Final Instruction

Do not stop after implementing only the next phase.

Use my uploaded latest Phase 6 project as the foundation and complete the remaining development to produce the strongest technically justified end-to-end implementation feasible.

Prioritize **correct functionality, research novelty through meaningful integration, measurable evaluation, maintainable folder organization, and realistic results** over unnecessary decorative features.

Once the updated ZIP is delivered, I will review the project and request any additional corrections or missing functionality.
