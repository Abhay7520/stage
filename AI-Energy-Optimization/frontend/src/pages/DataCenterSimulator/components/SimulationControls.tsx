import { HelpText } from "../../../components/help/Help";
export function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="sim-metric">
      <HelpText title={label} />
      <strong>{value}</strong>
    </div>
  );
}

export function ResourceBar({
  label,
  used,
  total,
  unit,
}: {
  label: string;
  used: number;
  total: number;
  unit: string;
}) {
  const percent = total > 0 ? Math.min(100, (used / total) * 100) : 0;

  return (
    <div className="sim-resource">
      <div className="sim-resource-label">
        <HelpText title={label} />
        <strong>
          {used} / {total} {unit}
        </strong>
      </div>

      <div className="sim-progress">
        <div
          className={
            percent >= 85 ? "sim-progress-fill high" : "sim-progress-fill"
          }
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
