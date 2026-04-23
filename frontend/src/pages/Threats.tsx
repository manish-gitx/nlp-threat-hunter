import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Search, Trash2 } from "lucide-react";
import { Api, ThreatSummary } from "../api";
import SeverityBadge from "../components/SeverityBadge";
import EmptyState from "../components/EmptyState";

export default function Threats() {
  const [items, setItems] = useState<ThreatSummary[]>([]);
  const [q, setQ] = useState("");
  const [severity, setSeverity] = useState<string>("");
  const [category, setCategory] = useState<string>("");
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    const res = await Api.listThreats({
      severity: severity || undefined,
      category: category || undefined,
      limit: 200,
    });
    setItems(res);
    setLoading(false);
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [severity, category]);

  const filtered = useMemo(
    () =>
      items.filter((i) =>
        q.trim() ? i.summary.toLowerCase().includes(q.toLowerCase()) : true
      ),
    [items, q]
  );

  async function onDelete(id: number) {
    if (!confirm(`Delete threat #${id}?`)) return;
    await Api.deleteThreat(id);
    load();
  }

  return (
    <div className="flex flex-col gap-5">
      <header>
        <h1 className="text-2xl font-semibold">Threats</h1>
        <p className="text-sm text-slate-400 mt-1">
          All ingested and classified events. Click any row for full analysis.
        </p>
      </header>

      <div className="card p-4 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-[220px]">
          <Search size={14} className="text-slate-500" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search summaries…"
            className="bg-transparent outline-none text-sm w-full"
          />
        </div>
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          className="bg-bg border border-border rounded-md px-2 py-1.5 text-sm"
        >
          <option value="">All severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="bg-bg border border-border rounded-md px-2 py-1.5 text-sm"
        >
          <option value="">All categories</option>
          <option value="malware">Malware</option>
          <option value="phishing">Phishing</option>
          <option value="apt">APT</option>
          <option value="brute_force">Brute Force</option>
          <option value="ddos">DDoS</option>
          <option value="data_exfiltration">Data Exfil</option>
          <option value="insider_threat">Insider</option>
          <option value="benign">Benign</option>
        </select>
      </div>

      <div className="card overflow-hidden">
        {loading ? (
          <div className="p-6 text-sm text-slate-400">Loading…</div>
        ) : filtered.length === 0 ? (
          <EmptyState
            title="No threats match"
            description="Adjust filters or ingest new data from the Ingest page."
          />
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-panel2/60 text-slate-400 text-xs uppercase tracking-wider">
              <tr>
                <th className="text-left p-3">ID</th>
                <th className="text-left p-3">Category</th>
                <th className="text-left p-3">Severity</th>
                <th className="text-left p-3">Summary</th>
                <th className="text-left p-3">Source</th>
                <th className="text-left p-3">When</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((t) => (
                <tr key={t.id} className="border-t border-border hover:bg-panel2/40">
                  <td className="p-3 font-mono text-slate-400">#{t.id}</td>
                  <td className="p-3"><span className="cat-badge">{t.category}</span></td>
                  <td className="p-3"><SeverityBadge value={t.severity} /></td>
                  <td className="p-3 max-w-[420px] truncate">
                    <Link to={`/threats/${t.id}`} className="hover:text-accent">
                      {t.summary}
                    </Link>
                  </td>
                  <td className="p-3 text-slate-400">{t.source}</td>
                  <td className="p-3 text-slate-500 text-xs">
                    {new Date(t.created_at).toLocaleString()}
                  </td>
                  <td className="p-3">
                    <button
                      onClick={() => onDelete(t.id)}
                      className="text-slate-500 hover:text-red-400"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
