import { Severity } from "../api";

export default function SeverityBadge({ value }: { value: Severity | string }) {
  const cls = `chip sev-${value}`;
  return <span className={cls}>{value}</span>;
}
