"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from game_sandbox.api.games import router as games_router

app = FastAPI(title="Mingle API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://mingle-seven-nu.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
