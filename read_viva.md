# Automated Threat Hunting with NLP — Viva Guide

A from-scratch explanation of every part of the project: the problem, the ML,
the code, the database, the API, the UI, the Docker setup, and the cloud
deployment. Written so you can walk into a viva and defend any layer.

Live URLs:
- Frontend: https://nlp-frontend-244293793844.asia-south1.run.app
- Backend:  https://nlp-backend-244293793844.asia-south1.run.app
- API docs: https://nlp-backend-244293793844.asia-south1.run.app/docs
- GitHub:   https://github.com/manish-gitx/nlp-threat-hunter

---

## 1. What problem does this project solve?

Security Operations Centers (SOCs) drown in **unstructured text** — firewall
logs, IDS alerts, antivirus verdicts, incident tickets, threat-intel feeds,
analyst notes. A human has to read each entry, decide if it's a real threat,
categorise it (malware? phishing? APT?), extract the interesting bits (IPs,
hashes, CVEs, actor names), and prioritise by severity.

That manual process is slow and inconsistent. The project uses **Natural
Language Processing** to automate it:

1. Clean and normalise the raw text.
2. Extract **IOCs** (Indicators of Compromise — IPs, hashes, URLs, CVEs…)
   with regex.
3. Extract **named entities** (threat actors, malware families, tools) with
   spaCy NER plus a rule-based `EntityRuler`.
4. **Classify** the event into a threat category with a TF-IDF + Logistic
   Regression model trained on a seed SOC corpus.
5. Compute a **severity score** (hybrid rule + ML) and a level
   (low / medium / high / critical).
6. **Cluster** related incidents with K-Means so an analyst sees "10 similar
   phishing events" instead of 10 separate rows.
7. Persist everything in a DB and expose it through a REST API + dashboard
   with charts, IOC lists, trend analysis, and a simple analyst chat.

## 2. High-level architecture

```
┌──────────────────────────┐    HTTPS     ┌──────────────────────────────┐
│   React + Vite           │  /api/*      │   FastAPI  (Uvicorn)         │
│   Tailwind  Recharts     │ ───────────► │   spaCy + scikit-learn       │
│   Dashboard · Chat · etc │              │   SQLAlchemy + SQLite        │
└──────────────────────────┘              └──────────────────────────────┘
          (Cloud Run)                             (Cloud Run)
```

- **Frontend** = a React single-page app bundled by Vite, served as static
  files by nginx in a container.
- **Backend**  = a FastAPI application running under Uvicorn inside a Python
  container.
- **Data**     = SQLite file local to the backend container (fine for demo;
  would be Postgres via Cloud SQL in production).
- **ML models** = spaCy `en_core_web_sm` and a scikit-learn `Pipeline`
  (TF-IDF → Logistic Regression) trained on first boot and cached to disk.

The frontend talks only to the backend over plain HTTP(S) JSON. CORS is
restricted to the deployed frontend origin.

## 3. Tech stack — one line each

| Layer | Tech | Why |
|---|---|---|
| Web framework | **FastAPI** | async, auto-generated OpenAPI/Swagger docs, Pydantic validation |
| ASGI server | **Uvicorn** | standard production ASGI server for FastAPI |
| Validation | **Pydantic v2** | type-safe request/response schemas |
| ORM | **SQLAlchemy 2.0** | typed ORM for threats/entities/IOCs tables |
| DB | **SQLite** | zero-config, embedded — swap URL for Postgres anywhere |
| NLP | **spaCy 3.8** | NER + `EntityRuler` for cyber-specific terms |
| ML | **scikit-learn** | TF-IDF vectoriser + Logistic Regression + KMeans |
| Frontend | **React 18 + TypeScript** | component model, type safety |
| Build | **Vite 5** | fast dev server + production bundling |
| Styling | **Tailwind CSS** | utility-first styling |
| Charts | **Recharts** | declarative charts for dashboard |
| HTTP | **Axios** | promise-based HTTP client |
| Container | **Docker** | reproducible images for backend and frontend |
| Registry | **Artifact Registry** | GCP-native container registry |
| CI build | **Cloud Build** | runs `docker build` remotely, pushes image |
| Runtime | **Cloud Run** | serverless containers, scales to zero |

## 4. Repository layout

```
nlp/
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI app factory (CORS, routers, startup)
│   │   ├── config.py          Pydantic-Settings (env-var config)
│   │   ├── database.py        SQLAlchemy engine + Session dependency
│   │   ├── models.py          Threat / Entity / IOC / IngestBatch tables
│   │   ├── schemas.py         Pydantic request/response models
│   │   ├── nlp/               The NLP pipeline (one file per stage)
│   │   ├── routers/           ingest · threats · stats · reports · chat · entities
│   │   └── services/          threat ingestion + clustering logic
│   ├── seed.py                Inserts 12 realistic SOC examples
│   ├── requirements.txt
│   ├── Dockerfile             Python 3.11-slim image
│   └── .dockerignore
└── frontend/
    ├── src/
    │   ├── App.tsx            Sidebar + routing
    │   ├── api.ts             Axios client + TS types
    │   ├── pages/             Dashboard / Ingest / Threats / Entities / Reports / Chat
    │   └── components/        StatCard / SeverityBadge / EmptyState
    ├── Dockerfile             Multi-stage: Node build → nginx serve
    ├── nginx.conf             SPA fallback + gzip + cache headers
    └── vite.config.ts
```

## 5. The NLP pipeline — file by file

The `pipeline.analyze(text)` function is the single entry point. It runs the
steps in this order:

```python
cleaned = clean_text(text)
category, confidence = classify(cleaned)
iocs = extract_iocs(cleaned)
entities = extract_entities(cleaned)
severity, score = score_severity(cleaned, category, len(iocs))
summary = summarize(cleaned)
```

### 5.1 Preprocessing (`nlp/preprocessing.py`)
- **Unicode normalisation** with `NFKC` — collapses compatibility characters
  (e.g. full-width digits become ASCII digits) so regex patterns match.
- Strips **control characters** (0x00–0x1F except tab/newline, plus 0x7F)
  because logs often contain them.
- Collapses whitespace runs to a single space.
- `summarize()` returns the first 180 chars, cut on a word boundary — used as
  a short teaser in list views.

### 5.2 IOC extraction (`nlp/iocs.py`)
Pure **regex**. One compiled pattern per IOC type:

| Type | What it matches |
|---|---|
| `ipv4` | dotted quads `0–255` in each octet |
| `ipv6` | eight groups of 1–4 hex chars |
| `url` | `http(s)://…` until whitespace |
| `domain` | labels ending in a known TLD (`com net org io ru cn co …`) |
| `email` | `user@host.tld` |
| `md5 / sha1 / sha256` | 32 / 40 / 64 hex chars |
| `cve` | `CVE-YYYY-NNNNN` |
| `file_path_windows` | `C:\...\file.ext` |
| `registry_key` | `HKEY_*\...` |
| `port` | `port 443`-style |
| `mitre_technique` | `T1059`, `T1059.001`-style IDs |

Results are **deduplicated** by `(type, lowercased value)`. Trailing
punctuation is trimmed because logs often end sentences with an IP.

### 5.3 Named Entity Recognition (`nlp/ner.py`)
Two-layer approach:
1. **Statistical NER** from spaCy's `en_core_web_sm` — detects generic labels
   `ORG`, `PERSON`, `GPE` (country/city), `LOC`, `PRODUCT`, `EVENT`, `DATE`,
   `TIME`.
2. **`EntityRuler`** — a rule-based spaCy component that runs **before** the
   statistical NER and assigns custom labels from curated lists:
   - `THREAT_ACTOR` — APT28, APT29, Lazarus, FIN7, Turla, Sandworm, …
   - `MALWARE` — Emotet, TrickBot, Ryuk, LockBit, Cobalt Strike, Mimikatz, …
   - `TOOL` — PowerShell, PsExec, BloodHound, Metasploit, Nmap, …

If the spaCy model isn't installed the code **falls back to a blank English
pipeline** (`spacy.blank("en")`) so the app still runs — quality drops but
the EntityRuler patterns still fire.

### 5.4 Classification (`nlp/classifier.py`)
A scikit-learn `Pipeline`:

```python
Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1,
                              max_df=0.95, sublinear_tf=True)),
    ("clf",   LogisticRegression(max_iter=1000, C=2.0,
                                 class_weight="balanced")),
])
```

- **TF-IDF** = Term Frequency × Inverse Document Frequency. It turns each
  document into a sparse vector where common-in-doc, rare-in-corpus words get
  high weight. `ngram_range=(1,2)` means both unigrams and bigrams
  (e.g. `"cobalt strike"`). `sublinear_tf=True` applies
  `1 + log(tf)` to damp dominant terms.
- **Logistic Regression** is a linear classifier — for multi-class it uses a
  one-vs-rest / softmax scheme. `class_weight="balanced"` down-weights
  majority classes so `benign` doesn't swallow everything.
- Training data = `TRAINING_SAMPLES` in `nlp/training_data.py`, ~45 labelled
  SOC sentences covering 8 classes: `malware`, `phishing`, `apt`,
  `brute_force`, `ddos`, `data_exfiltration`, `insider_threat`, `benign`.
- **Cached to disk** with `joblib` under `model_cache/threat_classifier.joblib`
  — first request trains (fast, ~1 s), later requests load in milliseconds.

`classify()` returns `(label, confidence)` where confidence is the max class
probability from `predict_proba`.

### 5.5 Severity scoring (`nlp/severity.py`)
**Hybrid** — ML category + keyword rules + IOC count.

1. Start with a **category baseline** (`apt=0.85, malware=0.7, phishing=0.55,
   benign=0.05, …`).
2. Add `+0.15` for each **critical** keyword hit (`ransomware`, `zero-day`,
   `domain controller`, `c2`, `exfiltrat`, …).
3. Add `+0.08` per **high** keyword (`mimikatz`, `cobalt strike`, `beacon`,
   `lateral movement`, …).
4. Add `+0.03` per **medium** keyword (`brute`, `spray`, `scan`, `suspicious`).
5. Add `+0.02` per IOC (capped at 10).
6. Clamp to `[0, 1]`.

Score → level:
- `>= 0.8` critical
- `>= 0.6` high
- `>= 0.35` medium
- else low
- `benign` category always caps at `low`.

### 5.6 Clustering (`nlp/clustering.py`)
K-Means over a fresh TF-IDF of all stored threats. `k = max(2, min(8, √N))`
where `N` is the number of threats — a simple heuristic for "a handful of
clusters, scaled gently with corpus size". Runs every time we bulk-ingest so
the `cluster_id` stays fresh.

Returned cluster IDs are persisted on each `Threat` row so the dashboard can
group "similar incidents".

## 6. Database layer

`database.py` creates a single SQLAlchemy **engine** + **sessionmaker**.
`get_db()` is a FastAPI dependency that yields a session per request and
closes it in a `finally` block.

### Tables (`models.py`)

- **`threats`** — one row per ingested event: `raw_text`, `cleaned_text`,
  `category`, `confidence`, `severity`, `severity_score`, `cluster_id`,
  `summary`, `created_at`, `source`.
- **`entities`** — NER results, `(threat_id, text, label)`, FK to threat.
- **`iocs`** — regex results, `(threat_id, value, ioc_type)`, FK to threat.
- **`ingest_batches`** — bookkeeping for bulk uploads.

Cascading `all, delete-orphan` on the relationships so deleting a threat
cleans up its child rows.

`DATABASE_URL` defaults to `sqlite:///./threat_hunter.db` — change the env
var to `postgresql+psycopg://…` and the code works unchanged.

## 7. REST API (FastAPI)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/ingest` | Ingest one event, run pipeline, persist |
| `POST` | `/api/ingest/bulk` | Ingest many events (reclusters at end) |
| `POST` | `/api/ingest/analyze` | Preview mode — run pipeline, don't persist |
| `GET`  | `/api/threats` | List, filter by `category` / `severity` |
| `GET`  | `/api/threats/{id}` | Full detail with entities + IOCs |
| `DELETE` | `/api/threats/{id}` | Delete a threat |
| `GET`  | `/api/stats` | Dashboard metrics (7-day trend, categories, top IOCs) |
| `GET`  | `/api/reports/generate` | Auto-generated period report |
| `POST` | `/api/chat` | Rule-based analyst assistant |
| `GET`  | `/api/entities` | Aggregated NER entities |
| `GET`  | `/api/entities/iocs` | Aggregated IOCs by type |
| `GET`  | `/health` | Liveness probe |
| `GET`  | `/docs` | Swagger UI (auto-generated) |

FastAPI reads the Pydantic models in `schemas.py` to validate input and
render the OpenAPI spec visible at `/docs`.

### The chat endpoint
`routers/chat.py` is **deliberately rule-based** — no external LLM, no API
keys. It:
- Detects the intent with substring/startswith checks
  (`"top threat"`, `"critical"`, `"trend"`, `"analyze <text>"`).
- For IOC-looking input (IP / hash / CVE) it runs an `ILIKE` query against
  the `iocs` table and returns the top 5 matches.
- Falls back to a help message listing what it can answer.

This keeps the demo self-contained and reproducible for a viva.

## 8. Frontend (React + Vite)

- `src/api.ts` — a single Axios instance, with `baseURL` from
  `import.meta.env.VITE_API_URL`. All typed request helpers live in the
  `Api` object so pages just call `Api.stats()`, `Api.listThreats()`, etc.
- **Pages**:
  - `Dashboard` — `StatCard`s + Recharts line chart of the 7-day trend, plus
    top IOCs / categories.
  - `Ingest` — paste text, call `/api/ingest/analyze` for preview, then
    `/api/ingest` to save.
  - `Threats` — filterable list of threat rows.
  - `ThreatDetail` — raw text, cleaned text, entities, IOCs.
  - `Entities` — aggregated NER + IOC views.
  - `Reports` — calls `/api/reports/generate?days=7`.
  - `Chat` — simple message box against `/api/chat`.
- **Components** — `StatCard` (metric box), `SeverityBadge` (colour-coded
  pill), `EmptyState`.

Build = `tsc -b && vite build` — TypeScript compile check, then Vite bundles
to `dist/` (a plain directory of static HTML/CSS/JS).

### nginx config (`frontend/nginx.conf`)
- **SPA fallback** — `try_files $uri $uri/ /index.html;` so client-side
  routing works (any unknown path serves the index and React Router handles
  it).
- Gzip compression.
- 30-day cache headers on static assets with cache-busted filenames.
- Listens on `$PORT` (defaults to 8080) — required because Cloud Run
  injects `PORT` at runtime.

## 9. Containerisation

### Backend Dockerfile
```
FROM python:3.11-slim
...
RUN apt-get install build-essential curl   # needed by some wheels
COPY requirements.txt .
RUN pip install -r requirements.txt \
    && python -m spacy download en_core_web_sm
COPY app ./app
COPY seed.py ./seed.py
RUN python seed.py || true        # bake a seeded SQLite into the image
EXPOSE 8080
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

Notes:
- **`python:3.11-slim`** — small Debian-based Python base.
- **spaCy model is downloaded at build time** (~15 MB) so the container is
  self-contained.
- `seed.py` runs at build time so the image ships with 12 sample threats —
  the dashboard looks alive on a cold start.
- **`PORT` env var** — Cloud Run sets this; we default to 8080.

### Frontend Dockerfile (multi-stage)
```
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build                 # produces dist/

FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
CMD [...]                         # substitute PORT into the nginx config
```

The **build arg `VITE_API_URL`** is baked into the JS bundle at build time —
Vite inlines `import.meta.env.VITE_API_URL` into the compiled output. So the
frontend image is pinned to a specific backend URL; changing that URL means
a rebuild.

Multi-stage keeps the final image tiny: only nginx + static files, no Node.

## 10. Cloud deployment (GCP)

### Services used
- **Artifact Registry** — private Docker registry at
  `asia-south1-docker.pkg.dev/nlp-threat-hunter-75853/nlp-threat-hunter`.
- **Cloud Build** — runs `docker build` on Google's infra and pushes the
  image to Artifact Registry. Invoked with `gcloud builds submit`.
- **Cloud Run** — serverless container platform. Runs N instances of the
  image, auto-scales based on traffic, **scales to zero** when idle.
- **Cloud Run service agent + Cloud Build builder** — service accounts GCP
  creates automatically to do the work on your behalf.

### Deploy commands (what we actually ran)

```bash
# 1. Create project + link billing + enable APIs
gcloud projects create nlp-threat-hunter-75853
gcloud billing projects link nlp-threat-hunter-75853 \
  --billing-account=014CB5-CFAC2F-330503
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com cloudbuild.googleapis.com

# 2. Create the image repository
gcloud artifacts repositories create nlp-threat-hunter \
  --repository-format=docker --location=asia-south1

# 3. Build + push backend image, then deploy
gcloud builds submit \
  --tag asia-south1-docker.pkg.dev/.../backend:v1 backend/
gcloud run deploy nlp-backend \
  --image asia-south1-docker.pkg.dev/.../backend:v1 \
  --region asia-south1 --allow-unauthenticated \
  --port 8080 --memory 1Gi --max-instances 3

# 4. Build + push frontend image (with backend URL baked in)
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_VITE_API_URL=<backend-url>,_IMAGE=...

gcloud run deploy nlp-frontend --image ...

# 5. Lock backend CORS to the frontend origin
gcloud run services update nlp-backend \
  --update-env-vars='^@^CORS_ORIGINS=<frontend-url>'
```

### Why Cloud Run?
- **Serverless** — we don't manage VMs, patching, load balancers.
- **Scales to zero** — cost while idle is near zero.
- **HTTPS out of the box** — each service gets a `*.run.app` URL with a
  managed certificate.
- **Region-pinned** — we chose `asia-south1` (Mumbai) for low RTT from India.

### Limitations we hit & how we handled them
- **SQLite is ephemeral on Cloud Run.** The container filesystem is wiped on
  every cold start, so writes don't persist across restarts. Fine for a demo
  with seeded data; for production we'd point `DATABASE_URL` at **Cloud SQL
  (Postgres)**.
- **Cold starts** (~5–10 s on first request) because the container has to
  boot and load spaCy + sklearn. Mitigation: set `--min-instances=1` (keeps
  one warm, ~$10/mo) or warm up with a scheduled ping.
- **CORS** — the backend initially allowed `*` for the first boot. We then
  tightened it to the frontend origin via `gcloud run services update`. The
  custom delimiter trick `^@^CORS_ORIGINS=url1,url2` was needed because
  gcloud splits env-var values on commas by default.

## 11. Full request lifecycle (example)

User pastes `"Cobalt Strike beacon on WIN-DC01 to 185.23.12.44 port 443"` in
the Ingest page and hits save.

1. Browser → `POST https://nlp-frontend.../` … no, wait — the frontend calls
   `Api.ingest(text)` which hits `POST https://nlp-backend.../api/ingest`.
2. Cloud Run routes the request to a backend container (cold-starts one if
   needed).
3. FastAPI validates the JSON body with the `IngestRequest` Pydantic schema.
4. `threat_service.ingest_one()` calls `pipeline.analyze(text)`:
   - `clean_text` → unicode NFKC, whitespace squeeze.
   - `classify` → TF-IDF vector → LR predicts `"malware"` (or `"apt"`),
     confidence e.g. 0.74.
   - `extract_iocs` → regex finds `ipv4=185.23.12.44`, `port=443`.
   - `extract_entities` → spaCy `EntityRuler` labels "Cobalt Strike" as
     `MALWARE`, "WIN-DC01" may come out as `ORG` from the base model.
   - `score_severity` → baseline 0.7 (malware) + 0.08 (`beacon` keyword) +
     0.08 (`cobalt strike`) + 2 × 0.02 (IOC bonus) = ~0.9 → `critical`.
   - `summarize` → first 180 chars.
5. A `Threat` row + child `Entity` and `IOC` rows are inserted in one
   transaction.
6. Response serialised via `ThreatDetail` Pydantic model and sent back.
7. Frontend routes to `ThreatDetail` page showing everything.

## 12. Likely viva questions — and short answers

**Q. Why TF-IDF + Logistic Regression instead of BERT / an LLM?**
Small labelled dataset (~45 examples), fast training, interpretable, runs
on CPU in milliseconds, no GPU needed, no API keys. A transformer would
overfit on 45 samples without heavy regularisation. The architecture is
pluggable — swap the classifier module for a fine-tuned DistilBERT later.

**Q. What is TF-IDF?**
Term Frequency × Inverse Document Frequency. A sparse vector representation
that weights words by how often they appear in a document but **discounts
words that appear in many documents** (stop-words, generic terms). Formula:
`tfidf(t,d) = tf(t,d) · log(N / df(t))`. `sublinear_tf` uses `1 + log(tf)`
to damp very frequent terms.

**Q. Why Logistic Regression?**
Linear, convex optimisation, probabilistic output (softmax), great baseline
for high-dim sparse features, robust with small data.

**Q. What's `class_weight="balanced"`?**
Each class weight is set to `N_total / (n_classes · N_class)` — rare classes
get bigger weight in the loss, so the model doesn't just predict the
majority class.

**Q. Why spaCy and what does `en_core_web_sm` give you?**
spaCy is a production NLP library with built-in tokeniser, POS tagger, and
a neural NER trained on OntoNotes. `en_core_web_sm` is the small English
model (~15 MB) with the CNN-based NER that labels `PERSON`, `ORG`, `GPE`,
etc. We augment it with an `EntityRuler` to catch cyber-specific terms.

**Q. Why regex for IOCs instead of NER?**
IOCs have **deterministic formats** (an IPv4 is literally four 0–255 octets).
Regex is 100 % precise, zero training data needed, trivial to extend.

**Q. What's K-Means and why √N clusters?**
K-Means partitions vectors into k clusters by minimising within-cluster
variance (Lloyd's algorithm: assign → re-centre → repeat). `√N` is a rule of
thumb — for small corpora it keeps k small (demo has 12 threats → k≈3);
grows gently as the corpus grows; capped at 8.

**Q. How does FastAPI work?**
It's an async Python web framework on top of Starlette (ASGI). You declare
Pydantic schemas; FastAPI auto-validates requests, generates OpenAPI JSON,
and renders Swagger UI at `/docs`.

**Q. What's the difference between WSGI and ASGI?**
WSGI is synchronous, one-request-per-thread (Flask, Django classic). ASGI is
async and supports WebSockets + long-lived connections. FastAPI needs ASGI,
which is why we use Uvicorn.

**Q. Why SQLAlchemy ORM?**
Typed Python objects instead of raw SQL, database-agnostic (SQLite →
Postgres with one env-var change), relationships + cascades expressed
declaratively, migration path via Alembic if needed.

**Q. What does Dockerfile `CMD` vs `ENTRYPOINT` do?**
`ENTRYPOINT` is the fixed executable; `CMD` is default arguments. We use
`CMD ["sh","-c","..."]` so we can expand the `$PORT` env var at container
start.

**Q. Why multi-stage for the frontend?**
Build stage has Node + 400 MB of `node_modules`. Runtime stage only needs
nginx + the compiled `dist/` folder (a few hundred KB). Final image is tiny
and has no build toolchain attack surface.

**Q. What is Cloud Run exactly?**
A Google-managed service that runs stateless containers. You give it an
image + port; it handles TLS, autoscaling, request routing, cold starts.
Billed per 100 ms of CPU + memory while a request is being served. Scales
to zero.

**Q. What is Artifact Registry?**
GCP's managed Docker (and other format) registry — a private replacement
for Docker Hub. Images live at
`<region>-docker.pkg.dev/<project>/<repo>/<image>:<tag>`.

**Q. What is Cloud Build?**
A managed build service. Point it at a Dockerfile, it runs `docker build`
on Google's infra and pushes the image to a registry. Avoids you pushing a
huge image from your laptop.

**Q. Why did the frontend need to be rebuilt to change the backend URL?**
Because Vite **inlines** `import.meta.env.VITE_API_URL` at build time into
the JS bundle. Runtime env vars don't reach the browser bundle unless you
either (a) serve a small config.json and fetch it, or (b) rebuild.

**Q. How does CORS work?**
Browser sees a cross-origin request (frontend `*.run.app` → backend
`*.run.app`), sends an `Origin` header, the backend responds with
`Access-Control-Allow-Origin: <that origin>`, browser allows the response.
For non-simple requests (JSON `POST`, custom headers) the browser first
sends an `OPTIONS` preflight. FastAPI's `CORSMiddleware` handles both.

**Q. What happens on a cold start?**
Cloud Run has no warm instance → spawns a new container → Python interpreter
boots → `app.main` import triggers `init_db()` + `get_classifier()` → spaCy
model loads → sklearn pipeline loads from joblib cache (or trains) → first
request served. Subsequent requests hit the warm instance in <100 ms.

**Q. How would you productionise this?**
- Cloud SQL (Postgres) instead of SQLite.
- Secret Manager for DB creds.
- Min-instances = 1 to eliminate cold starts.
- Cloud Build trigger on `git push` for CI/CD.
- Structured logging (JSON) to Cloud Logging.
- Authentication — API keys or IAM-based access.
- Replace the rule-based chat with a retrieval-augmented LLM.
- Replace the seed classifier with a fine-tuned DistilBERT on a larger
  labelled SOC corpus.

**Q. Data flow summary in one sentence?**
Raw log text → cleaned text → (regex IOCs + spaCy entities + TF-IDF/LR
category + hybrid severity) → persisted as `Threat + Entity + IOC` rows
→ surfaced to the React dashboard through a FastAPI JSON API.

---

## 13. Command cheatsheet

```bash
# Run locally
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev           # http://localhost:5173

# Rebuild + redeploy backend
gcloud builds submit \
  --tag asia-south1-docker.pkg.dev/nlp-threat-hunter-75853/nlp-threat-hunter/backend:v2 backend/
gcloud run deploy nlp-backend \
  --image asia-south1-docker.pkg.dev/nlp-threat-hunter-75853/nlp-threat-hunter/backend:v2 \
  --region asia-south1

# Check live API
curl -s https://nlp-backend-244293793844.asia-south1.run.app/health
curl -s https://nlp-backend-244293793844.asia-south1.run.app/api/stats | jq
curl -s -X POST https://nlp-backend-244293793844.asia-south1.run.app/api/ingest/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"Cobalt Strike beacon on WIN-DC01 to 185.23.12.44 port 443"}' | jq
```

That's the whole project, from first principles to production URL.
