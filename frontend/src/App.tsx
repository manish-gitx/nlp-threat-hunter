import { NavLink, Route, Routes } from "react-router-dom";
import {
  LayoutDashboard,
  Upload,
  ShieldAlert,
  Boxes,
  FileText,
  Bot,
  ShieldCheck,
} from "lucide-react";
import Dashboard from "./pages/Dashboard";
import Ingest from "./pages/Ingest";
import Threats from "./pages/Threats";
import ThreatDetailPage from "./pages/ThreatDetail";
import Entities from "./pages/Entities";
import Reports from "./pages/Reports";
import Chat from "./pages/Chat";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/ingest", label: "Ingest", icon: Upload },
  { to: "/threats", label: "Threats", icon: ShieldAlert },
  { to: "/entities", label: "Entities & IOCs", icon: Boxes },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/chat", label: "Analyst Assistant", icon: Bot },
];

export default function App() {
  return (
    <div className="min-h-screen grid grid-cols-[260px_1fr]">
      <aside className="border-r border-border bg-panel/40 p-5 flex flex-col gap-6">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-accent" />
          <div>
            <div className="font-semibold leading-tight">Threat Hunter</div>
            <div className="text-xs text-slate-500 leading-tight">NLP for SOC</div>
          </div>
        </div>

        <nav className="flex flex-col gap-1">
          {nav.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition ${
                  isActive
                    ? "bg-accent/10 text-accent border border-accent/30"
                    : "text-slate-300 hover:bg-panel2"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto text-xs text-slate-500 leading-relaxed">
          Automated Threat Hunting with Natural Language Processing. Classifies
          unstructured security text into malware, phishing, APT and more.
        </div>
      </aside>

      <main className="p-6 md:p-8 overflow-x-hidden">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/ingest" element={<Ingest />} />
          <Route path="/threats" element={<Threats />} />
          <Route path="/threats/:id" element={<ThreatDetailPage />} />
          <Route path="/entities" element={<Entities />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
    </div>
  );
}
