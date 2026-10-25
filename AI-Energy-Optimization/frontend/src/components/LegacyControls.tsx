import { HelpText } from "./help/Help";
import { Explained } from "./help/Help";
import type React from "react";
export function StatCard({
  icon,
  title,
  value,
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
}) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>

      <div>
        <HelpText title={title} />

        <strong>{value}</strong>
      </div>
    </div>
  );
}

export function NumberInput({
  value,
  onChange,
}: {
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <input
      className="table-input"
      type="number"
      value={value}
      onChange={(event) => onChange(Number(event.target.value))}
    />
  );
}

export function InputField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <Explained title={String(label)}>
      <label className="input-field">
        <span>{label}</span>

        <input
          aria-label={label}
          type="number"
          value={value}
          onChange={(event) => onChange(Number(event.target.value))}
        />
      </label>
    </Explained>
  );
}

export function ComparisonBar({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="comparison-row">
      <div className="comparison-label">
        <HelpText title={label} />

        <strong>{value.toFixed(1)}%</strong>
      </div>

      <div className="bar">
        <div
          className="bar-fill"
          style={{
            width: `${Math.min(Math.max(value, 0), 100)}%`,
          }}
        />
      </div>
    </div>
  );
}
