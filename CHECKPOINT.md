# CHECKPOINT — CourtSense Build

## Architect: completed 2026-04-06

## Current Status: BUILDING (minimax agent spawned)

## Spec: C:\Users\ethan\.openclaw\workspace\specs\courtsense\BUILD-SPEC.md

## Slug: courtsense

## Key Implementation Notes
- LLM calls route through OpenClaw/minimax integration (no external API keys needed for MiniMax)
- OpenAI embeddings used for pgvector drill search (set OPENAI_API_KEY for embeddings, falls back to LIKE search)
- DATABASE_URL env var required for PostgreSQL
- Demo uses hardcoded user ID `00000000-0000-0000-0000-000000000001`
- seed_drill_data.py must be run once before the app starts

## File Structure
```
backend/
  main.py, models.py, database.py
  routers/: sessions.py, digest.py, drills.py
  services/: session_service.py, digest_agent.py, drill_agent.py, embedding_service.py
frontend/
  src/: App.jsx, api.js, main.jsx
  components/: SessionLogger.jsx, SessionList.jsx, WeeklyDigest.jsx, DrillCard.jsx
  index.html, vite.config.js, package.json
seed_drill_data.py
```

## Open Issues / Next Steps
- Build agent (minimax) is implementing the full project per BUILD-SPEC.md
- Tests not yet written (pytest target: 8/8)
- README is scaffolded, needs polish after build
