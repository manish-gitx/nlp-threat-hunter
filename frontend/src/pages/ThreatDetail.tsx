import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Api, ThreatDetail as TD } from "../api";
import SeverityBadge from "../components/SeverityBadge";

export default function ThreatDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState<TD | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    Api.getThreat(Number(id))
      .then(setData)
      .catch((e) => setErr(e.message));
  }, [id]);

  if (err) return <div className="card p-6 text-red-400">Failed: {err}</div>;
  if (!data) return <div className="card p-6 text-slate-400">Loading…</div>;

  return (
    <div className="flex flex-col gap-5">
      <Link to="/threats" className="text-sm text-slate-400 hover:text-accent flex items-center gap-1">
        <ArrowLeft size={14} /> Back to threats
      </Link>

      <header className="card p-5 flex flex-wrap items-center gap-3">
        <div className="font-mono text-slate-500 text-sm">#{data.id}</div>
        <span className="cat-badge">{data.category}</span>
        <SeverityBadge value={data.severity} />
        <div className="text-xs text-slate-400">
          confidence {(data.confidence * 100).toFixed(1)}% · sev score {data.severity_score}
        </div>
        <div className="ml-auto text-xs text-slate-500">
          {new Date(data.created_at).toLocaleString()} · source {data.source} · cluster{" "}
          {data.cluster_id >= 0 ? data.cluster_id : "—"}
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="card p-5 lg:col-span-2">
          <div className="text-sm text-slate-400 mb-2">Raw text</div>
          <pre className="whitespace-pre-wrap break-words text-sm text-slate-200 font-mono bg-bg/60 border border-border rounded-md p-3">
            {data.raw_text}
          </pre>
          <div className="text-sm text-slate-400 mt-5 mb-2">Summary</div>
          <div className="text-slate-200">{data.summary}</div>
        </div>

        <div className="flex flex-col gap-5">
          <div className="card p-5">
            <div className="text-sm text-slate-400 mb-2">Entities ({data.entities.length})</div>
            <div className="flex flex-wrap gap-1">
              {data.entities.length === 0 && <span className="text-xs text-slate-500">none</span>}
              {data.entities.map((e, i) => (
                <span key={i} className="chip bg-accent2/10 border-accent2/30 text-accent2">
                  {e.label} · {e.text}
                </span>
              ))}
            </div>
          </div>
          <div className="card p-5">
            <div className="text-sm text-slate-400 mb-2">IOCs ({data.iocs.length})</div>
            <div className="flex flex-wrap gap-1">
              {data.iocs.length === 0 && <span className="text-xs text-slate-500">none</span>}
              {data.iocs.map((i, idx) => (
                <span key={idx} className="chip bg-accent/10 border-accent/30 text-accent font-mono">
                  {i.ioc_type}:{i.value}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
