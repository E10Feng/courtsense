"""FastAPI entry point for CourtSense."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import sessions, digest, drills
from backend.database import init_db

app = FastAPI(title="CourtSense", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(digest.router, prefix="/digest", tags=["digest"])
app.include_router(drills.router, prefix="/drills", tags=["drills"])


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"message": "CourtSense API — Log sessions, get your weekly breakdown."}
