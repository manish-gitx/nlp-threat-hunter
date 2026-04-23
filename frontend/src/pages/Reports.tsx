import { useEffect, useState } from "react";
import { Api, Report } from "../api";
import { Loader2 } from "lucide-react";

export default function Reports() {
  const [days, setDays] = useState(7);
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);

  async function load(d: number) {
    setLoading(true);
    try {
      setReport(await Api.report(d));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(days);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex flex-col gap-5">
      <header className="flex items-end justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Automated Reports</h1>
          <p className="text-sm text-slate-400 mt-1">
            NLP-generated executive summary with recommendations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {[1, 7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => {
                setDays(d);
                load(d);
              }}
              className={`btn ${d === days ? "btn-primary" : "btn-ghost"}`}
            >
              Last {d}d
            </button>
          ))}
        </div>
      </header>

      {loading || !report ? (
        <div className="card p-6 text-slate-400 flex items-center gap-2">
          <Loader2 className="animate-spin" size={16} /> Generating…
        </div>
      ) : (
        <div className="flex flex-col gap-5">
          <div className="card p-5">
            <div className="text-xs text-slate-500">
              Generated {new Date(report.generated_at).toLocaleString()} · period{" "}
              {report.period_days}d
            </div>
            <p className="mt-3 text-slate-200 leading-relaxed">{report.narrative}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            <div className="card p-5">
              <div className="text-sm text-slate-400 mb-2">By category</div>
              <ul className="text-sm space-y-1">
                {Object.entries(report.by_category).map(([k, v]) => (
                  <li key={k} className="flex justify-between">
                    <span className="text-slate-300">{k}</span>
                    <span className="text-slate-500">{v}</span>
                  </li>
                ))}
                {Object.keys(report.by_category).length === 0 && (
                  <li className="text-slate-500 text-xs">no events</li>
                )}
              </ul>
            </div>
            <div className="card p-5">
              <div className="text-sm text-slate-400 mb-2">By severity</div>
              <ul className="text-sm space-y-1">
                {Object.entries(report.by_severity).map(([k, v]) => (
                  <li key={k} className="flex justify-between">
                    <span className="text-slate-300">{k}</span>
                    <span className="text-slate-500">{v}</span>
                  </li>
                ))}
                {Object.keys(report.by_severity).length === 0 && (
                  <li className="text-slate-500 text-xs">no events</li>
                )}
              </ul>
            </div>
            <div className="card p-5">
              <div className="text-sm text-slate-400 mb-2">Top IOCs</div>
              <ul className="text-sm space-y-1">
                {report.top_iocs.map((i) => (
                  <li key={`${i.ioc_type}:${i.value}`} className="flex justify-between gap-2">
                    <span className="font-mono truncate">{i.value}</span>
                    <span className="text-slate-500 text-xs">{i.ioc_type} · {i.count}</span>
                  </li>
                ))}
                {report.top_iocs.length === 0 && <li className="text-slate-500 text-xs">none</li>}
              </ul>
            </div>
          </div>

          <div className="card p-5">
            <div className="text-sm text-slate-400 mb-2">Recommendations</div>
            <ol className="list-decimal ml-5 space-y-1.5 text-slate-200 text-sm">
              {report.recommendations.length === 0 && (
                <li className="text-slate-500 text-xs">No items.</li>
              )}
              {report.recommendations.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}
