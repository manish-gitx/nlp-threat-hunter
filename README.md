# Automated Threat Hunting with NLP

Full-stack platform that applies Natural Language Processing to unstructured
security data (logs, alerts, incident reports) to automatically classify
threats, extract IOCs, cluster similar incidents, and generate SOC reports.

## Architecture

```
┌──────────────────────────┐          ┌──────────────────────────────┐
│   React + Vite (5173)    │  HTTP    │   FastAPI backend (8000)     │
│   Tailwind · Recharts    │ ───────► │   spaCy · scikit-learn       │
│   Dashboard · Chat · etc │          │   SQLAlchemy + SQLite        │
└──────────────────────────┘          └──────────────────────────────┘
```

**NLP pipeline (`backend/app/nlp/`)**

1. `preprocessing.py` – cleaning, normalisation, summarisation
2. `iocs.py` – regex extraction for IPs, URLs, domains, hashes, CVEs, registry keys, MITRE IDs
3. `ner.py` – spaCy Named Entity Recognition + custom patterns for threat actors / malware / tools
4. `classifier.py` – TF-IDF + Logistic Regression trained on a seed SOC corpus (auto-trains on first run, cached to disk)
5. `severity.py` – hybrid rule + ML severity scoring
6. `clustering.py` – KMeans clustering of similar incidents
7. `pipeline.py` – orchestrator that combines the above into one call

## Project layout

```
nlp/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI app factory
│   │   ├── config.py            Pydantic settings
│   │   ├── database.py          SQLAlchemy engine + session
│   │   ├── models.py            Threat / Entity / IOC tables
│   │   ├── schemas.py           Pydantic I/O models
│   │   ├── nlp/                 NLP pipeline (see above)
│   │   ├── routers/             ingest · threats · stats · reports · chat · entities
│   │   └── services/            threat ingestion + clustering
│   ├── seed.py                  Populate DB with 12 realistic SOC samples
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.tsx              Sidebar + routing
    │   ├── api.ts               Axios client + types
    │   ├── pages/               Dashboard · Ingest · Threats · ThreatDetail · Entities · Reports · Chat
    │   └── components/          StatCard · SeverityBadge · EmptyState
    ├── package.json
    ├── vite.config.ts           Dev proxy /api → :8000
    └── .env.example
```

## Setup

### 1. Backend

```bash
cd backend

# Create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download the spaCy English model (the app falls back to a blank pipeline if missing,
# but this is strongly recommended for quality NER)
python -m spacy download en_core_web_sm

# Copy the env file and adjust if needed
cp .env.example .env

# (Optional) seed the DB with 12 sample events so the dashboard has data
python seed.py

# Run the API
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy the env file (you can leave VITE_API_URL empty for dev — Vite proxies /api to :8000)
cp .env.example .env

# Run the dev server
npm run dev
```

UI: http://localhost:5173

## API endpoints

| Method | Path                    | Purpose                                              |
|--------|-------------------------|------------------------------------------------------|
| POST   | `/api/ingest`           | Ingest one event, run pipeline, persist              |
| POST   | `/api/ingest/bulk`      | Ingest many events at once                           |
| POST   | `/api/ingest/analyze`   | Run pipeline in preview mode (no persist)            |
| GET    | `/api/threats`          | List threats (filter by `category`, `severity`)      |
| GET    | `/api/threats/{id}`     | Full threat detail with entities and IOCs            |
| DELETE | `/api/threats/{id}`     | Delete a threat                                      |
| GET    | `/api/stats`            | Dashboard metrics (7-day trend, categories, IOCs)    |
| GET    | `/api/reports/generate` | Auto-generated period report with recommendations    |
| POST   | `/api/chat`             | Rule-based analyst assistant over the indexed corpus |
| GET    | `/api/entities`         | Aggregated NER entities                              |
| GET    | `/api/entities/iocs`    | Aggregated IOCs by type                              |

## Threat categories

The seed classifier distinguishes:
`malware`, `phishing`, `apt`, `brute_force`, `ddos`, `data_exfiltration`,
`insider_threat`, `benign`.

To extend: add labelled examples to `backend/app/nlp/training_data.py`
and delete `backend/model_cache/threat_classifier.joblib` to force a retrain.

## Environment variables

**Backend (`backend/.env`)**

| Key                | Default                                           | Notes                                           |
|--------------------|---------------------------------------------------|-------------------------------------------------|
| `APP_NAME`         | `Automated Threat Hunting with NLP`               | Used in API metadata                            |
| `DATABASE_URL`     | `sqlite:///./threat_hunter.db`                    | Any SQLAlchemy URL (Postgres, etc.)             |
| `CORS_ORIGINS`     | `http://localhost:5173,http://127.0.0.1:5173`     | Comma-separated allowed origins                 |
| `SPACY_MODEL`      | `en_core_web_sm`                                  | Any installed spaCy pipeline                    |
| `MODEL_CACHE_DIR`  | `./model_cache`                                   | Where the trained classifier is persisted       |

**Frontend (`frontend/.env`)**

| Key            | Default | Notes                                                                          |
|----------------|---------|--------------------------------------------------------------------------------|
| `VITE_API_URL` | *(empty)* | Leave empty in dev (Vite proxies `/api`). Set to backend origin in production. |

## Quick smoke test

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/api/ingest/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"Cobalt Strike beacon on WIN-DC01 to 185.23.12.44 port 443"}' | jq
```

You should see `category: "malware"` (or `"apt"`), a severity score, extracted
IOCs (the IP, port), and relevant entities.
