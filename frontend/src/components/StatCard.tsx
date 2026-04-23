import { ReactNode } from "react";

export default function StatCard({
  label,
  value,
  icon,
  accent = "text-accent",
  hint,
}: {
  label: string;
  value: ReactNode;
  icon?: ReactNode;
  accent?: string;
  hint?: string;
}) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase tracking-wider text-slate-400">{label}</div>
        {icon && <div className={accent}>{icon}</div>}
      </div>
      <div className="mt-3 text-3xl font-semibold">{value}</div>
      {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
    </div>
  );
}
