"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from game_sandbox.api.games import router as games_router
from game_sandbox.api.maze_runner import router as maze_runner_router

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
app.include_router(maze_runner_router)


@app.get("/")
def home() -> dict[str, object]:
    return {
        "name": "Mingle API",
        "status": "ok",
        "endpoints": {
            "health": "/health",
            "tic_tac_toe": "/games",
            "maze_runner": "/maze",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
