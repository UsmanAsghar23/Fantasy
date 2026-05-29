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

## Upload 2 — Database

SQLAlchemy models and Alembic migrations live under `apps/api`. Requires Postgres running (step 2 above).

```bash
cd apps/api
source .venv/bin/activate
pip install -r requirements.txt

# From repo root, copy env if needed: cp .env.example .env
alembic upgrade head
```

Verify tables:

```bash
docker exec -it fantasy-postgres psql -U fantasy -d fantasy -c "\dt"
```

Expected tables: `sports`, `users`, `teams`, `players`, `player_season_stats`, `player_game_logs`, `user_watchlists`. Seed rows: `nfl`, `nba` in `sports`.

## Upload 3 — ETL and player API

Sync data (requires Upload 2 migrations and Postgres running). NFL uses [nflverse](https://github.com/nflverse/nflverse-data) via `nflreadpy`; NBA uses [balldontlie](https://www.balldontlie.io/) (rate-limited — first sync can take several minutes).

```bash
cd apps/api
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# One sport at a time (recommended)
python -m scripts.sync_stats --sport nfl --season 2024
python -m scripts.sync_stats --sport nba --season 2024
```

Start the API and try:

- [http://localhost:8000/docs](http://localhost:8000/docs)
- `GET /players?sport=nfl&q=mahomes`
- `GET /players/{player_id}`

## Upload 4 — Auth and watchlist API

Configure Google OAuth (Web client) in [Google Cloud Console](https://console.cloud.google.com/apis/credentials). Authorized JavaScript origins: `http://localhost:3000`. Copy client ID/secret into `.env`:

```bash
JWT_SECRET=your-long-random-secret
GOOGLE_CLIENT_ID=....apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=...
```

**Flow:** The Next.js app (Upload 5) obtains a Google **ID token** and sends it to the API. The API verifies it, upserts the user, and returns a JWT.

| Endpoint | Auth | Description |
|----------|------|-------------|
| `POST /auth/sync` | No | Body: `{ "id_token": "..." }` → JWT + user |
| `GET /auth/me` | Bearer | Current user |
| `GET /watchlist` | Bearer | Saved players |
| `POST /watchlist/{player_id}` | Bearer | Add player |
| `DELETE /watchlist/{player_id}` | Bearer | Remove player |

**Test with curl** (replace tokens):

```bash
# After obtaining a Google ID token from your OAuth client:
curl -X POST http://localhost:8000/auth/sync \
  -H "Content-Type: application/json" \
  -d '{"id_token": "GOOGLE_ID_TOKEN"}'

export TOKEN="your-jwt"
curl http://localhost:8000/auth/me -H "Authorization: Bearer $TOKEN"
curl http://localhost:8000/watchlist -H "Authorization: Bearer $TOKEN"
curl -X POST "http://localhost:8000/watchlist/PLAYER_UUID" -H "Authorization: Bearer $TOKEN"
```

Use **Authorize** in [Swagger UI](http://localhost:8000/docs) with `Bearer <jwt>` for watchlist routes.

## Roadmap

| Upload | Status |
|--------|--------|
| 1 — Scaffold | Done |
| 2 — Database | Done (local) |
| 3 — ETL + player search API | Done (local) |
| 4 — Auth + watchlist API | Done (local) |
| 5 — Web UI | |
| 6 — Analytics | |
| 7 — Deploy + CI | |
