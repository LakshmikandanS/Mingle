"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from game_sandbox.api.games import router as games_router

app = FastAPI(title="Mingle API")
app.include_router(games_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
