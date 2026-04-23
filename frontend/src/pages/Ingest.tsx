import { useState } from "react";
import { Loader2, Sparkles, Save } from "lucide-react";
import { Api, AnalyzeResponse } from "../api";
import SeverityBadge from "../components/SeverityBadge";

const SAMPLE = `EDR detected Cobalt Strike beacon on host WIN-DC01 calling out to 185.23.12.44 on port 443. Process tree shows rundll32.exe spawning from winword.exe. MITRE T1059.001 observed.`;

export default function Ingest() {
  const [text, setText] = useState("");
  const [source, setSource] = useState("manual");
  const [preview, setPreview] = useState<AnalyzeResponse | null>(null);
  const [busy, setBusy] = useState<"analyze" | "save" | null>(null);
  const [saved, setSaved] = useState<number | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function onAnalyze() {
    setErr(null);
    setSaved(null);
    setBusy("analyze");
    try {
      const res = await Api.analyze(text);
      setPreview(res);
    } catch (e: any) {
      setErr(e?.response?.data?.detail || e.message);
    } finally {
      setBusy(null);
    }
  }

  async function onIngest() {
    setErr(null);
    setSaved(null);
    setBusy("save");
    try {
      const res = await Api.ingest(text, source);
      setSaved(res.id);
      setPreview({
        category: res.category,
        confidence: res.confidence,
        severity: res.severity,
        severity_score: res.severity_score,
        summary: res.summary,
        entities: res.entities,
        iocs: res.iocs,
        cleaned_text: res.cleaned_text,
      });
    } catch (e: any) {
      setErr(e?.response?.data?.detail || e.message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="text-2xl font-semibold">Ingest security text</h1>
        <p className="text-sm text-slate-400 mt-1">
          Paste a log line, alert, or incident report. The NLP pipeline will classify it,
          extract IOCs and entities, and assign a severity.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm text-slate-400">Raw text</label>
            <button
              className="text-xs text-accent hover:underline"
              onClick={() => setText(SAMPLE)}
              type="button"
            >
              Insert sample
            </button>
          </div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={10}
            placeholder="Paste alert, log, or incident report…"
            className="w-full rounded-lg bg-bg border border-border p-3 text-sm font-mono outline-none focus:border-accent/50"
          />

          <div className="flex items-center gap-3 mt-3">
            <label className="text-xs text-slate-400">Source:</label>
            <input
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="flex-1 rounded-lg bg-bg border border-border px-3 py-1.5 text-sm outline-none focus:border-accent/50"
            />
          </div>

          <div className="flex gap-2 mt-4">
            <button
              className="btn-ghost"
              disabled={!text.trim() || busy !== null}
              onClick={onAnalyze}
            >
              {busy === "analyze" ? <Loader2 className="animate-spin" size={16} /> : <Sparkles size={16} />}
              Analyze (preview)
            </button>
            <button
              className="btn-primary"
              disabled={!text.trim() || busy !== null}
              onClick={onIngest}
            >
              {busy === "save" ? <Loader2 className="animate-spin" size={16} /> : <Save size={16} />}
              Ingest & store
            </button>
          </div>

          {saved !== null && (
            <div className="mt-3 text-xs text-emerald-400">
              Saved as threat #{saved}.
            </div>
          )}
          {err && <div className="mt-3 text-xs text-red-400">{err}</div>}
        </div>

        <div className="card p-5">
          <div className="text-sm text-slate-400 mb-3">Analysis</div>
          {!preview ? (
            <div className="text-sm text-slate-500">
              Analysis results will appear here after you click <span className="text-slate-300">Analyze</span>.
            </div>
          ) : (
            <div className="flex flex-col gap-3 text-sm">
              <div className="flex items-center gap-2">
                <span className="cat-badge">{preview.category}</span>
                <SeverityBadge value={preview.severity} />
                <span className="text-xs text-slate-400">
                  confidence {(preview.confidence * 100).toFixed(1)}% · sev score {preview.severity_score}
                </span>
              </div>
              <div>
                <div className="text-xs text-slate-400 mb-1">Summary</div>
                <div className="rounded-md bg-bg/60 border border-border p-2 text-slate-200">{preview.summary}</div>
              </div>
              <div>
                <div className="text-xs text-slate-400 mb-1">Entities ({preview.entities.length})</div>
                <div className="flex flex-wrap gap-1">
                  {preview.entities.length === 0 && <span className="text-xs text-slate-500">none</span>}
                  {preview.entities.map((e, i) => (
                    <span key={i} className="chip bg-accent2/10 border-accent2/30 text-accent2">
                      {e.label} · {e.text}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-400 mb-1">IOCs ({preview.iocs.length})</div>
                <div className="flex flex-wrap gap-1">
                  {preview.iocs.length === 0 && <span className="text-xs text-slate-500">none</span>}
                  {preview.iocs.map((i, idx) => (
                    <span key={idx} className="chip bg-accent/10 border-accent/30 text-accent font-mono">
                      {i.ioc_type}:{i.value}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
