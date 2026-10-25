# In-app guidance and your own data

Every sidebar page now has an **ⓘ page guide** above its content. Dashboard's guide contains the complete seven-step workflow, from capacity setup through data entry, forecasting, preview/apply, comparison, adaptation and reporting.

Smaller **ⓘ buttons** beside controls, actions, table columns and metrics explain:

- What the value/action means.
- What to enter, with units or ranges where applicable.
- What changes in the saved simulation.
- Whether the result is a prediction, reservation or analytical estimate.

Help opens a modal popup. Close with **Got it**, the close button, Escape or a backdrop click. Keyboard focus stays inside the modal and returns to the help button when dismissed. Buttons use `type="button"`, so opening help does not submit a form, reset the scenario or apply a plan. Help beside a disabled action still explains its purpose.

## Use your own readings

1. Create your servers and VMs in Data Center Simulator. Positive vCPU and GB values define actual simulated capacities and reservations.
2. Open Workload Intelligence, select a VM and choose **Enter four readings**.
3. Enter observations oldest first. CPU, RAM and disk percentages must be 0–100; network readings must be nonnegative and use units consistent with the source trace.
4. Choose an honest source label and click **Save & forecast VM**. Your exact accepted observations are saved and sent to the trained predictors; they are not replaced by fixed demo results.
5. Repeat for other VMs. The saved histories drive subsequent forecast demand, allocation scoring and comparisons.
6. Preview placement again after changing data. Review before/after values and apply only the plan you choose.

Editing readings clears displayed forecasts and shows an unsaved-changes message. Batch forecasting is disabled until those edits are saved. Editing loaded synthetic readings relabels them `user-entered`; changing a source label also requires saving. Inputs are disabled while a request is being processed to avoid showing a response for newly edited values.

Changing inputs does **not** retrain models. Tree models can produce similar or identical predictions for nearby values, and resource constraints or costs can keep a placement unchanged even when demand estimates change. This is a meaningful result, not a requirement to invent a different allocation for every edit.

Adaptive **Saved observations unchanged** mode uses your saved data as-is. **Seeded synthetic fluctuations** deliberately generates and saves new example readings and changes provenance to synthetic; it is not a source of real measurements.

## Source locations

- `frontend/src/components/help/Help.tsx`: reusable info buttons, modal dialog, page guide, explanatory field/action wrappers and metric labels.
- `frontend/src/components/help/helpContent.ts`: plain-language guides for all 12 pages and the contextual glossary.
- `frontend/src/components/help/Help.css`: responsive dialog and help-button styling.
- `frontend/src/App.tsx`: per-page help entry point.
- `frontend/src/pages/WorkloadIntelligence/WorkloadIntelligence.tsx`: custom-data save/dirty-state behavior.
- Page folders and shared components contain their own nearby help entry points; no DOM injection is used.

No forecasting, energy or optimization claims have been strengthened by these UI additions. The original model and simulation limitations continue to apply.
