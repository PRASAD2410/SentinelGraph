# SentinelGraph — Criminal Network Intelligence MVP

An investigator-facing hackathon demo for turning synthetic FIR/police-report text into an explainable relationship network. **All included records are fictional.** Scores and alerts are investigative leads only; they are not evidence or proof of criminality.

## What works

- Polished React + Cytoscape relationship graph
- FIR/report ingestion, deterministic entity extraction, normalization, candidate relationships, and report provenance
- Person, phone, vehicle, location, account, and organization entities
- NetworkX degree, betweenness, and PageRank analytics
- Explainable high-connectivity and shared-association lead rules
- Timeline, case metrics, seeded synthetic dataset, and a natural-language investigation assistant
- FastAPI backend designed to run in demo-memory mode now; `.env` and Docker include Neo4j connection settings for the next persistence step.

## Fastest path on Windows: Docker Desktop

1. Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/). Enable its WSL 2 integration when prompted.
2. In PowerShell, open this folder:

   ```powershell
   cd C:\Users\prasa\Documents\Codex\2026-09-12\referenced-chatgpt-conversation-this-is-an\criminal
   Copy-Item .env.example .env
   docker compose up --build
   ```

3. Open `http://localhost:5173`. The API docs are at `http://localhost:8000/docs`; Neo4j Browser is at `http://localhost:7474` (user `neo4j`, password `change-me`).
4. Stop with `Ctrl+C`. To remove only the containers, run `docker compose down`. Keep the volume unless you intentionally want to erase Neo4j data.

## Local development (without Docker)

Install Python 3.12+ and Node.js 20+. In one PowerShell window:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another:

```powershell
cd frontend
npm install
npm run dev
```

If PowerShell prevents virtual environment activation, run this once for the current window: `Set-ExecutionPolicy -Scope Process Bypass`.

## Architecture

`frontend/` is the React/Vite UI. `backend/app/main.py` is the FastAPI vertical slice. `extraction.py` combines spaCy (using a no-download fallback) and transparent rules; `llm.py` defines a provider-agnostic boundary for a vetted OpenAI, Azure OpenAI, or local structured-extraction provider without changing API callers. `demo_data.py` provides the seeded case. `neo_store.py` writes normalized nodes and provenance-bearing relationships to Neo4j whenever it is available; the app falls back to in-memory demo mode if it is not.

The app deliberately retains an in-memory cache so the demo works immediately. The Docker composition starts Neo4j alongside the app and writes seeded and ingested findings there, preserving `reportId`, extraction confidence, and provenance on every relationship. A production version would make Neo4j the read repository too, and add a durable report/audit schema.

## Responsible-use guardrails

- Keep raw source reports, confidence, analyst review state, and provenance with all findings.
- Never represent graph centrality or rule matches as guilt, identity verification, or a legal conclusion.
- Require authorized access, human review, retention controls, audit logging, and jurisdiction-specific privacy/legal review before using real-world data.

## Hosting on Render

Deploy the API first from the repository root using `render.yaml`. Set `GEMINI_API_KEY` in Render's secret-environment-variable prompt; never commit it. Once Render provides the API URL, deploy `frontend/` as a Static Site with build command `npm install && npm run build`, publish directory `dist`, and build-time environment variable `VITE_API_URL` set to the API URL. Finally set the API service's `FRONTEND_ORIGIN` to the Static Site URL and redeploy it.
