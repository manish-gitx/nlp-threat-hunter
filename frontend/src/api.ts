import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "";

export const api = axios.create({
  baseURL,
  timeout: 20000,
});

export type Severity = "critical" | "high" | "medium" | "low";

export interface ThreatSummary {
  id: number;
  source: string;
  category: string;
  confidence: number;
  severity: Severity;
  severity_score: number;
  cluster_id: number;
  summary: string;
  created_at: string;
}

export interface Entity {
  text: string;
  label: string;
}

export interface IOC {
  value: string;
  ioc_type: string;
}

export interface ThreatDetail extends ThreatSummary {
  raw_text: string;
  cleaned_text: string;
  entities: Entity[];
  iocs: IOC[];
}

export interface Stats {
  total_threats: number;
  by_category: Record<string, number>;
  by_severity: Record<string, number>;
  recent_7d: { date: string; count: number; critical: number; high: number }[];
  top_iocs: { value: string; ioc_type: string; count: number }[];
  top_entities: { text: string; label: string; count: number }[];
  cluster_count: number;
}

export interface AnalyzeResponse {
  category: string;
  confidence: number;
  severity: Severity;
  severity_score: number;
  summary: string;
  entities: Entity[];
  iocs: IOC[];
  cleaned_text: string;
}

export interface Report {
  generated_at: string;
  period_days: number;
  total_threats: number;
  by_category: Record<string, number>;
  by_severity: Record<string, number>;
  top_iocs: { value: string; ioc_type: string; count: number }[];
  narrative: string;
  recommendations: string[];
}

export interface ChatResponse {
  reply: string;
  context?: Record<string, any>;
}

export const Api = {
  ingest: (text: string, source = "manual") =>
    api.post<ThreatDetail>("/api/ingest", { text, source }).then((r) => r.data),
  ingestBulk: (items: { text: string; source?: string }[]) =>
    api.post<ThreatSummary[]>("/api/ingest/bulk", { items }).then((r) => r.data),
  analyze: (text: string) =>
    api.post<AnalyzeResponse>("/api/ingest/analyze", { text }).then((r) => r.data),
  listThreats: (params: { category?: string; severity?: string; limit?: number; offset?: number } = {}) =>
    api.get<ThreatSummary[]>("/api/threats", { params }).then((r) => r.data),
  getThreat: (id: number) => api.get<ThreatDetail>(`/api/threats/${id}`).then((r) => r.data),
  deleteThreat: (id: number) => api.delete(`/api/threats/${id}`).then((r) => r.data),
  stats: () => api.get<Stats>("/api/stats").then((r) => r.data),
  report: (days = 7) =>
    api.get<Report>("/api/reports/generate", { params: { days } }).then((r) => r.data),
  chat: (message: string) =>
    api.post<ChatResponse>("/api/chat", { message }).then((r) => r.data),
  entities: () => api.get("/api/entities").then((r) => r.data),
  iocs: () => api.get("/api/entities/iocs").then((r) => r.data),
};
