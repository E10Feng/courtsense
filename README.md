# CourtSense 🎾

Log pickleball and tennis sessions → get AI-powered weekly digests with specific weaknesses and drill recommendations.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with `pgvector` extension

### Setup

```bash
# 1. Create PostgreSQL database
createdb courtsense
# Run in psql:
# CREATE EXTENSION IF NOT EXISTS vector;

# 2. Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set DATABASE_URL
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/courtsense"

# Seed drill data
python ../seed_drill_data.py

# Run server
uvicorn backend.main:app --reload

# 3. Frontend
cd ../frontend
npm install
npm run dev
```

Visit http://localhost:3000

## Tech Stack

- **Backend:** Python 3.11, FastAPI, LangGraph, PostgreSQL/pgvector
- **Frontend:** React 18, Vite
- **AI:** MiniMax M2.7 via OpenClaw agent integration

## API

- `POST /sessions` — Log a session
- `GET /sessions/{user_id}?days=7` — Get recent sessions
- `POST /digest/generate` — Generate weekly digest
- `GET /digest/{user_id}` — Get latest digest
- `GET /drills/search?query=net+play&sport=pickleball` — Search drills

## Project Structure

```
courtsense/
├── backend/
│   ├── main.py              # FastAPI entry
│   ├── models.py             # Pydantic models
│   ├── database.py           # SQLAlchemy models + pgvector
│   ├── routers/              # API route handlers
│   └── services/             # Business logic + LangGraph agents
├── frontend/                  # React + Vite
├── seed_drill_data.py        # Seeds 24 drills with embeddings
└── BUILD-SPEC.md
```
