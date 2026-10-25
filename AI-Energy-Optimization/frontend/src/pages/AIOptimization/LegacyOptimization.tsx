import { Explained } from "../../components/help/Help";
import { useLegacy } from "../../hooks/useLegacy";
import { StatCard } from "../../components/LegacyControls";
import { Activity, Brain, Cpu, Leaf } from "lucide-react";
export default function LegacyOptimization() {
  const { optimization, loading, runAnalysis } = useLegacy();
  return (
    <>
      <section>
        <div className="page-title">
          <span className="eyebrow">AI OPTIMIZATION ENGINE</span>

          <h2>Resource Allocation</h2>

          <p>
            Compare candidate CPU allocations against predicted workload and
            estimated energy consumption.
          </p>
        </div>

        {!optimization ? (
          <div className="panel empty-state large">
            <Brain size={48} />

            <h3>No optimization result yet</h3>

            <p>
              Run the AI analysis from the dashboard to generate
              recommendations.
            </p>

            <Explained action title="Run AI Analysis">
              <button
                className="primary-button"
                onClick={runAnalysis}
                disabled={loading}
              >
                <Brain size={18} />
                Run AI Analysis
              </button>
            </Explained>
          </div>
        ) : (
          <>
            <div className="stat-grid">
              <StatCard
                icon={<Cpu />}
                title="Current Allocation"
                value={`${optimization.current_cpu.toFixed(1)}%`}
              />

              <StatCard
                icon={<Activity />}
                title="Predicted Demand"
                value={`${optimization.predicted_workload.toFixed(1)}%`}
              />

              <StatCard
                icon={<Brain />}
                title="AI Recommendation"
                value={`${optimization.recommended_cpu.toFixed(1)}%`}
              />

              <StatCard
                icon={<Leaf />}
                title="Energy Saving"
                value={`${optimization.estimated_energy_saving_percent.toFixed(
                  1,
                )}%`}
              />
            </div>

            <div className="panel">
              <div className="panel-header">
                <div>
                  <h3>Candidate Allocations</h3>

                  <p>Allocations evaluated by the optimization engine.</p>
                </div>
              </div>

              <div className="candidate-list">
                {optimization.candidate_allocations.map((candidate, index) => (
                  <div
                    className={
                      candidate.cpu_allocation === optimization.recommended_cpu
                        ? "candidate recommended"
                        : "candidate"
                    }
                    key={index}
                  >
                    <div>
                      <strong>{candidate.cpu_allocation.toFixed(1)}%</strong>

                      <span>CPU allocation</span>
                    </div>

                    <div>
                      <strong>{candidate.predicted_energy.toFixed(2)} J</strong>

                      <span>predicted energy</span>
                    </div>

                    <div>
                      {candidate.feasible ? (
                        <span className="badge good">Feasible</span>
                      ) : (
                        <span className="badge">Insufficient</span>
                      )}
                    </div>

                    {candidate.cpu_allocation ===
                      optimization.recommended_cpu && (
                      <span className="recommended-label">AI Recommended</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </section>
    </>
  );
}
