import { Explained } from "../../components/help/Help";
import { useLegacy } from "../../hooks/useLegacy";
import { StatCard, ComparisonBar } from "../../components/LegacyControls";
import { Activity, Brain, Cpu, Leaf, Zap, RefreshCw } from "lucide-react";
export default function LegacyDashboard() {
  const {
    predictedWorkload,
    predictedEnergy,
    optimization,
    loading,
    runAnalysis,
    currentCpu,
  } = useLegacy();
  return (
    <>
      <>
        <section className="hero">
          <div>
            <span className="eyebrow">AI-POWERED RESOURCE MANAGEMENT</span>

            <h2>Optimize energy without sacrificing performance.</h2>

            <p>
              Predict future workload, estimate energy consumption, and identify
              a more efficient CPU allocation.
            </p>
          </div>

          <Explained action title="Run AI Analysis">
            <button
              className="primary-button"
              onClick={runAnalysis}
              disabled={loading}
            >
              {loading ? (
                <>
                  <RefreshCw size={18} className="spin" />
                  Running AI...
                </>
              ) : (
                <>
                  <Brain size={18} />
                  Run AI Analysis
                </>
              )}
            </button>
          </Explained>
        </section>

        <section className="stat-grid">
          <StatCard
            icon={<Cpu />}
            title="Current CPU"
            value={`${currentCpu.toFixed(1)}%`}
          />

          <StatCard
            icon={<Activity />}
            title="Predicted Workload"
            value={
              predictedWorkload !== null
                ? `${predictedWorkload.toFixed(1)}%`
                : "--"
            }
          />

          <StatCard
            icon={<Zap />}
            title="Predicted Energy"
            value={
              predictedEnergy !== null
                ? `${predictedEnergy.toFixed(2)} J`
                : "--"
            }
          />

          <StatCard
            icon={<Leaf />}
            title="Estimated Saving"
            value={
              optimization
                ? `${optimization.estimated_energy_saving_percent.toFixed(1)}%`
                : "--"
            }
          />
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Optimization Result</h3>

                <p>AI recommendation based on predicted workload.</p>
              </div>
            </div>

            {optimization ? (
              <div className="optimization-result">
                <div className="recommendation">
                  <div className="recommendation-icon">
                    <Brain size={24} />
                  </div>

                  <div>
                    <span>Recommended CPU</span>

                    <strong>{optimization.recommended_cpu.toFixed(1)}%</strong>
                  </div>
                </div>

                <div className="comparison">
                  <ComparisonBar
                    label="Current CPU"
                    value={optimization.current_cpu}
                  />

                  <ComparisonBar
                    label="Predicted Workload"
                    value={optimization.predicted_workload}
                  />

                  <ComparisonBar
                    label="Recommended CPU"
                    value={optimization.recommended_cpu}
                  />
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <Brain size={32} />

                <p>
                  Run AI Analysis to generate an optimization recommendation.
                </p>
              </div>
            )}
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Energy Impact</h3>

                <p>Predicted before vs after optimization.</p>
              </div>
            </div>

            {optimization ? (
              <div className="energy-comparison">
                <div className="energy-item">
                  <span>Current</span>

                  <strong>
                    {optimization.current_predicted_energy.toFixed(2)} J
                  </strong>
                </div>

                <div className="arrow">→</div>

                <div className="energy-item">
                  <span>Optimized</span>

                  <strong>
                    {optimization.optimized_predicted_energy.toFixed(2)} J
                  </strong>
                </div>

                <div className="saving-box">
                  <Leaf size={20} />

                  <div>
                    <span>Estimated saving</span>

                    <strong>
                      {optimization.estimated_energy_saving_percent.toFixed(2)}%
                    </strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <Zap size={32} />

                <p>Energy comparison will appear after analysis.</p>
              </div>
            )}
          </div>
        </section>
      </>
    </>
  );
}
