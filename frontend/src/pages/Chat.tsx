import { useRef, useState, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";
import { Api } from "../api";

interface Msg {
  role: "user" | "assistant";
  text: string;
}

const SUGGESTIONS = [
  "What's the top threat category?",
  "How many critical alerts in the last 7 days?",
  "Show me trends this week",
  "analyze User clicked link in phishing email and entered credentials",
];

export default function Chat() {
  const [msgs, setMsgs] = useState<Msg[]>([
    {
      role: "assistant",
      text:
        "Hi, I'm the threat-hunting assistant. Ask me about top categories, critical counts, trends, or paste an IOC to look it up. Start a message with `analyze <text>` to run live classification.",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 9e9, behavior: "smooth" });
  }, [msgs, busy]);

  async function send(text?: string) {
    const q = (text ?? input).trim();
    if (!q || busy) return;
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: q }]);
    setBusy(true);
    try {
      const r = await Api.chat(q);
      setMsgs((m) => [...m, { role: "assistant", text: r.reply }]);
    } catch (e: any) {
      setMsgs((m) => [
        ...m,
        { role: "assistant", text: `Error: ${e?.response?.data?.detail || e.message}` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-5 h-[calc(100vh-4rem)]">
      <header>
        <h1 className="text-2xl font-semibold">Analyst Assistant</h1>
        <p className="text-sm text-slate-400 mt-1">
          Conversational query over the ingested corpus.
        </p>
      </header>

      <div className="card flex-1 flex flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 space-y-4">
          {msgs.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : ""}`}>
              {m.role === "assistant" && (
                <div className="w-7 h-7 rounded-full bg-accent/15 border border-accent/30 grid place-items-center text-accent flex-shrink-0">
                  <Bot size={14} />
                </div>
              )}
              <div
                className={`max-w-[70%] rounded-xl px-3 py-2 text-sm whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-accent text-slate-900"
                    : "bg-panel2 text-slate-200 border border-border"
                }`}
              >
                {m.text}
              </div>
              {m.role === "user" && (
                <div className="w-7 h-7 rounded-full bg-slate-700 grid place-items-center text-slate-300 flex-shrink-0">
                  <User size={14} />
                </div>
              )}
            </div>
          ))}
          {busy && <div className="text-xs text-slate-500">Thinking…</div>}
        </div>

        <div className="border-t border-border p-3">
          <div className="flex flex-wrap gap-1 mb-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                className="text-xs rounded-md bg-bg border border-border px-2 py-1 text-slate-400 hover:text-accent hover:border-accent/40"
              >
                {s}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") send();
              }}
              placeholder="Ask about threats, or paste an IOC…"
              className="flex-1 bg-bg border border-border rounded-lg px-3 py-2 text-sm outline-none focus:border-accent/50"
            />
            <button className="btn-primary" onClick={() => send()} disabled={busy || !input.trim()}>
              <Send size={14} /> Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
