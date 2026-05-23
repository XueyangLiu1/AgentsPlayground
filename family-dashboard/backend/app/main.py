"""FastAPI application entry."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import (
    cardholders, cards, benefits, benefit_progress,
    sign_up_bonuses, reminders, dashboard, presets,
)

# Auto-create tables (MVP; switch to alembic later)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Family Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Routers mounted under /api
for r in (
    cardholders.router, cards.router, benefits.router, benefit_progress.router,
    sign_up_bonuses.router, reminders.router, dashboard.router, presets.router,
):
    app.include_router(r, prefix="/api")
