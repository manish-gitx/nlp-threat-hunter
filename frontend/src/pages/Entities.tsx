import { useEffect, useState } from "react";
import { Api } from "../api";

interface EntityItem {
  text: string;
  label: string;
  count: number;
}
interface IOCItem {
  value: string;
  ioc_type: string;
  count: number;
}

export default function Entities() {
  const [entities, setEntities] = useState<EntityItem[]>([]);
  const [iocs, setIocs] = useState<IOCItem[]>([]);
  const [byType, setByType] = useState<Record<string, number>>({});

  useEffect(() => {
    Api.entities().then((r) => setEntities(r.items));
    Api.iocs().then((r) => {
      setIocs(r.items);
      setByType(r.by_type);
    });
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="text-2xl font-semibold">Entities & IOCs</h1>
        <p className="text-sm text-slate-400 mt-1">
          Aggregated extractions across all ingested events.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-5">
          <div className="text-sm text-slate-400 mb-3">
            Top entities <span className="text-slate-600">({entities.length})</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {entities.length === 0 && <span className="text-xs text-slate-500">no entities yet</span>}
            {entities.map((e, i) => (
              <span key={i} className="chip bg-accent2/10 border-accent2/30 text-accent2">
                <span className="uppercase tracking-wider text-[10px] text-accent2/80">
                  {e.label}
                </span>
                <span className="text-slate-200">{e.text}</span>
                <span className="text-slate-500">×{e.count}</span>
              </span>
            ))}
          </div>
        </div>

        <div className="card p-5">
          <div className="text-sm text-slate-400 mb-3">IOCs by type</div>
          <div className="flex flex-wrap gap-2">
            {Object.keys(byType).length === 0 && (
              <span className="text-xs text-slate-500">no IOCs yet</span>
            )}
            {Object.entries(byType).map(([t, c]) => (
              <span key={t} className="chip bg-panel2 border-border text-slate-300">
                <span className="text-accent">{t}</span>
                <span className="text-slate-500">×{c}</span>
              </span>
            ))}
          </div>
          <div className="mt-5 text-sm text-slate-400 mb-2">
            Top IOCs <span className="text-slate-600">({iocs.length})</span>
          </div>
          <div className="max-h-96 overflow-auto">
            <table className="w-full text-sm">
              <thead className="text-slate-500 text-xs uppercase tracking-wider">
                <tr>
                  <th className="text-left py-1.5">Type</th>
                  <th className="text-left py-1.5">Value</th>
                  <th className="text-right py-1.5">Count</th>
                </tr>
              </thead>
              <tbody>
                {iocs.map((i, idx) => (
                  <tr key={idx} className="border-t border-border/60">
                    <td className="py-1.5 text-accent">{i.ioc_type}</td>
                    <td className="py-1.5 font-mono truncate max-w-[280px]">{i.value}</td>
                    <td className="py-1.5 text-right text-slate-400">{i.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
