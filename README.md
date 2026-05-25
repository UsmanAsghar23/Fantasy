# Fantasy Sports Analytics

Multi-sport (NFL + NBA) fantasy analytics platform.

- **Frontend:** Next.js (`apps/web`)
- **Backend:** FastAPI (`apps/api`)
- **Database:** PostgreSQL (Docker)

## Upload 1 — Local setup

Scaffold only: Postgres via Docker, FastAPI `/health`, Next.js placeholder home.

### Prerequisites

- Docker Desktop
- Node.js 20+ and npm
- Python 3.12+

### 1. Environment

```bash
cp .env.example .env
```

### 2. Start PostgreSQL

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 3. API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Web

```bash
cd apps/web
npm install
npm run dev
```

App: [http://localhost:3000](http://localhost:3000)

## Project layout

```
Fantasy/
├── apps/
│   ├── api/          # FastAPI
│   └── web/          # Next.js
├── docker/
│   └── docker-compose.yml
└── README.md
```

## Roadmap

Incremental uploads to GitHub — see project plan. Upload 1 is scaffold only; database, ETL, auth, and UI follow in later uploads.
