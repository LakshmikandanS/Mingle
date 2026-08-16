"""Request and response schemas for the Mingle API."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class CreateGameRequest(BaseModel):
    game: str = "tic_tac_toe"
    players: dict[str, str] = Field(default_factory=lambda: {"X": "human", "O": "alphabeta"})


class ActionRequest(BaseModel):
    action: list[int]


class GameStateResponse(BaseModel):
    session_id: str
    game: str
    state: Any
    current_player: str
    legal_actions: list[Any]
    status: str


class MoveRecordResponse(BaseModel):
    move_number: int
    player: str
    action: Any
    resulting_state: Any
    decision_id: Optional[str] = None


class ReplayResponse(BaseModel):
    session_id: str
    game: str
    initial_state: Any
    moves: list[MoveRecordResponse]
    final_state: Optional[Any] = None


class DecisionResponse(BaseModel):
    decision_id: str
    player: str
    agent: str
    chosen_action: Any
    duration_ms: float
    metrics: Any
