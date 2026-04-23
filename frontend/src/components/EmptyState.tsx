import { ReactNode } from "react";

export default function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="card p-10 text-center">
      <div className="text-lg font-medium">{title}</div>
      {description && <div className="mt-2 text-sm text-slate-400">{description}</div>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
