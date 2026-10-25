import { HelpText } from "../../components/help/Help";
import { Explained } from "../../components/help/Help";
import { useLegacy } from "../../hooks/useLegacy";
import { NumberInput, InputField } from "../../components/LegacyControls";
import { Brain, CheckCircle2 } from "lucide-react";
export default function ResourceMonitor() {
  const {
    history,
    energyInput,
    setEnergyInput,
    predictedWorkload,
    predictedEnergy,
    optimization,
    loading,
    updateHistory,
    runAnalysis,
  } = useLegacy();
  return (
    <>
      <section>
        <div className="page-title">
          <span className="eyebrow">RESOURCE MONITOR</span>

          <h2>Workload History</h2>

          <p>
            Provide four consecutive resource observations for workload
            prediction.
          </p>
        </div>

        <div className="panel">
          <div className="resource-table">
            <div className="table-row table-header">
              <HelpText title="Interval" />
              <HelpText title="CPU %" />
              <HelpText title="Memory %" />
              <HelpText title="Net In" />
              <HelpText title="Net Out" />
              <HelpText title="Disk I/O %" />
            </div>

            {history.map((row, index) => (
              <div className="table-row" key={index}>
                <span>T-{3 - index}</span>

                <NumberInput
                  value={row.cpu_util_percent}
                  onChange={(value) =>
                    updateHistory(index, "cpu_util_percent", value)
                  }
                />

                <NumberInput
                  value={row.mem_util_percent}
                  onChange={(value) =>
                    updateHistory(index, "mem_util_percent", value)
                  }
                />

                <NumberInput
                  value={row.net_in}
                  onChange={(value) => updateHistory(index, "net_in", value)}
                />

                <NumberInput
                  value={row.net_out}
                  onChange={(value) => updateHistory(index, "net_out", value)}
                />

                <NumberInput
                  value={row.disk_io_percent}
                  onChange={(value) =>
                    updateHistory(index, "disk_io_percent", value)
                  }
                />
              </div>
            ))}
          </div>
        </div>

        <div className="panel energy-input-panel">
          <div className="panel-header">
            <div>
              <h3>Energy Model Inputs</h3>

              <p>Parameters used by the energy prediction model.</p>
            </div>
          </div>

          <div className="input-grid">
            <InputField
              label="CPU Mean %"
              value={energyInput.cpu_mean}
              onChange={(value) =>
                setEnergyInput({
                  ...energyInput,
                  cpu_mean: value,
                })
              }
            />

            <InputField
              label="CPU Max %"
              value={energyInput.cpu_max}
              onChange={(value) =>
                setEnergyInput({
                  ...energyInput,
                  cpu_max: value,
                })
              }
            />

            <InputField
              label="CPU Min %"
              value={energyInput.cpu_min}
              onChange={(value) =>
                setEnergyInput({
                  ...energyInput,
                  cpu_min: value,
                })
              }
            />

            <InputField
              label="CPU Std"
              value={energyInput.cpu_std}
              onChange={(value) =>
                setEnergyInput({
                  ...energyInput,
                  cpu_std: value,
                })
              }
            />

            <InputField
              label="CPU Median %"
              value={energyInput.cpu_median}
              onChange={(value) =>
                setEnergyInput({
                  ...energyInput,
                  cpu_median: value,
                })
              }
            />

            <InputField
              label="CPU Frequency GHz"
              value={energyInput.cpu_frequency_ghz}
              onChange={(value) =>
                setEnergyInput({
                  ...energyInput,
                  cpu_frequency_ghz: value,
                })
              }
            />

            <InputField
              label="Memory GB"
              value={energyInput.memory_util_gb}
              onChange={(value) =>
                setEnergyInput({
                  ...energyInput,
                  memory_util_gb: value,
                })
              }
            />

            <InputField
              label="Disk Writes"
              value={energyInput.sda_write_count_during_interval}
              onChange={(value) =>
                setEnergyInput({
                  ...energyInput,
                  sda_write_count_during_interval: value,
                })
              }
            />

            <InputField
              label="Disk Reads"
              value={energyInput.sda_read_count_during_interval}
              onChange={(value) =>
                setEnergyInput({
                  ...energyInput,
                  sda_read_count_during_interval: value,
                })
              }
            />
          </div>

          <Explained action title="Run AI Analysis">
            <button
              className="primary-button"
              onClick={runAnalysis}
              disabled={loading}
            >
              <Brain size={18} />

              {loading ? "Running..." : "Run AI Analysis"}
            </button>
          </Explained>
        </div>
        {(predictedWorkload !== null ||
          predictedEnergy !== null ||
          optimization !== null) && (
          <div className="analysis-results">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <h3>AI Analysis Results</h3>
                  <p>Results generated from the FastAPI AI models.</p>
                </div>

                <CheckCircle2 size={20} className="result-icon" />
              </div>

              <div className="result-grid">
                <div className="result-card">
                  <HelpText title="Predicted Workload" />

                  <strong>
                    {predictedWorkload !== null
                      ? `${predictedWorkload.toFixed(2)}%`
                      : "--"}
                  </strong>

                  <small>Next CPU utilization</small>
                </div>

                <div className="result-card">
                  <HelpText title="Predicted Energy" />

                  <strong>
                    {predictedEnergy !== null
                      ? `${predictedEnergy.toFixed(2)} J`
                      : "--"}
                  </strong>

                  <small>Estimated energy consumption</small>
                </div>

                <div className="result-card recommended-card">
                  <HelpText title="Recommended CPU" />

                  <strong>
                    {optimization
                      ? `${optimization.recommended_cpu.toFixed(2)}%`
                      : "--"}
                  </strong>

                  <small>AI optimized allocation</small>
                </div>

                <div className="result-card saving-card">
                  <HelpText title="Estimated Energy Saving" />

                  <strong>
                    {optimization
                      ? `${optimization.estimated_energy_saving_percent.toFixed(
                          2,
                        )}%`
                      : "--"}
                  </strong>

                  <small>Compared with current allocation</small>
                </div>
              </div>

              {optimization && (
                <div className="resource-recommendation">
                  <div className="recommendation-icon">
                    <Brain size={22} />
                  </div>

                  <div>
                    <strong>AI Recommendation</strong>

                    <p>
                      Current CPU allocation is{" "}
                      <b>{optimization.current_cpu.toFixed(1)}%</b>. Based on
                      the predicted workload of{" "}
                      <b>{optimization.predicted_workload.toFixed(1)}%</b>, the
                      optimizer recommends{" "}
                      <b>{optimization.recommended_cpu.toFixed(1)}%</b> CPU
                      allocation.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </section>
    </>
  );
}
