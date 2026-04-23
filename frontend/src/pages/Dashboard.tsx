import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Area,
  AreaChart,
} from "recharts";
import { Activity, AlertTriangle, Boxes, ShieldAlert } from "lucide-react";
import { Api, Stats } from "../api";
import StatCard from "../components/StatCard";

const CATEGORY_COLORS = [
  "#22d3ee",
  "#a78bfa",
  "#f472b6",
  "#34d399",
  "#fbbf24",
  "#60a5fa",
  "#f87171",
  "#c084fc",
];

const SEV_COLORS: Record<string, string> = {
  critical: "#ef4444",
  high: "#f59e0b",
  medium: "#eab308",
  low: "#10b981",
};

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    Api.stats()
      .then(setStats)
      .catch((e) => setErr(e.message));
  }, []);

  if (err) {
    return <div className="card p-6 text-red-400">Failed to load stats: {err}</div>;
  }
  if (!stats) {
    return <div className="card p-6 text-slate-400">Loading…</div>;
  }

  const categoryData = Object.entries(stats.by_category).map(([name, value]) => ({
    name,
    value,
  }));
  const severityData = Object.entries(stats.by_severity).map(([name, value]) => ({
    name,
    value,
  }));
  const total = stats.total_threats;
  const critical = stats.by_severity.critical || 0;
  const high = stats.by_severity.high || 0;

  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="text-2xl font-semibold">Security Operations Overview</h1>
        <p className="text-sm text-slate-400 mt-1">
          Real-time NLP-driven classification of ingested security text.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard label="Total Threats" value={total} icon={<Activity size={18} />} />
        <StatCard
          label="Critical (all time)"
          value={critical}
          icon={<AlertTriangle size={18} />}
          accent="text-danger"
        />
        <StatCard label="High" value={high} icon={<ShieldAlert size={18} />} accent="text-warn" />
        <StatCard
          label="Clusters"
          value={stats.cluster_count}
          icon={<Boxes size={18} />}
          accent="text-accent2"
          hint="Similar incidents grouped"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card p-5 lg:col-span-2">
          <div className="text-sm text-slate-400 mb-3">Activity · last 7 days</div>
          <div className="h-64">
            <ResponsiveContainer>
              <AreaChart data={stats.recent_7d}>
                <defs>
                  <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.6} />
                    <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #1f2937",
                    borderRadius: 8,
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#22d3ee"
                  fill="url(#g1)"
                  strokeWidth={2}
                />
                <Area type="monotone" dataKey="critical" stroke="#ef4444" fill="#ef4444" fillOpacity={0.15} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-5">
          <div className="text-sm text-slate-400 mb-3">Severity mix</div>
          <div className="h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={severityData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                >
                  {severityData.map((entry, i) => (
                    <Cell key={i} fill={SEV_COLORS[entry.name] || "#64748b"} />
                  ))}
                </Pie>
                <Legend />
                <Tooltip
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #1f2937",
                    borderRadius: 8,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card p-5 lg:col-span-2">
          <div className="text-sm text-slate-400 mb-3">Threats by category</div>
          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={categoryData}>
                <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #1f2937",
                    borderRadius: 8,
                  }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-5">
          <div className="text-sm text-slate-400 mb-3">Top IOCs</div>
          <ul className="space-y-2 text-sm">
            {stats.top_iocs.length === 0 && (
              <li className="text-slate-500 text-sm">No IOCs extracted yet.</li>
            )}
            {stats.top_iocs.map((i) => (
              <li
                key={`${i.ioc_type}:${i.value}`}
                className="flex items-center justify-between gap-2 border-b border-border/60 pb-1"
              >
                <span className="font-mono text-slate-200 truncate">{i.value}</span>
                <span className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="cat-badge">{i.ioc_type}</span>× {i.count}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
