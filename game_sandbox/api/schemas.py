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


class MazeEnvironmentRequest(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    rows: Any = None
    columns: Optional[int] = None
    start: Optional[list[int]] = None
    goal: Optional[list[int]] = None
    generation_strategy: str = "manual"
    seed: Optional[int] = None
    obstacle_probability: float = 0.25
    ensure_solvable: bool = True
    max_attempts: int = 100
    obstacles: list[Any] = Field(default_factory=list)
    terrain_costs: Any = Field(default_factory=dict)
    string_rows: Optional[list[str]] = None
    map_rows: Optional[list[str]] = None
    generation_config: dict[str, Any] = Field(default_factory=dict)


class MazePlayerRunRequest(BaseModel):
    environment_id: str


class MazePlayerActionRequest(BaseModel):
    action: str


class MazeSearchRunRequest(BaseModel):
    environment_id: str
    algorithm: str
    configuration: dict[str, Any] = Field(default_factory=dict)


class MazeHintRequest(BaseModel):
    hint_level: Optional[str] = None
    level: Optional[str] = None
    algorithm: Optional[str] = None
    search_run_id: Optional[str] = None
    configuration: dict[str, Any] = Field(default_factory=dict)


class MazeComparisonRequest(BaseModel):
    player_run_id: str
    search_run_id: str


class MazeIntermediateComparisonRequest(MazeComparisonRequest):
    state: Optional[list[int]] = None
