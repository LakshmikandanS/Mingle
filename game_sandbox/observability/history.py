"""Replay and thinking records for game sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from game_sandbox.observability.metrics import SearchMetrics


@dataclass
class DecisionRecord:
    decision_id: str
    player: str
    agent: str
    chosen_action: Optional[Any]
    duration_ms: float
    metrics: SearchMetrics = field(default_factory=SearchMetrics)


@dataclass
class MoveRecord:
    move_number: int
    player: str
    action: Any
    resulting_state: Any
    decision_id: Optional[str] = None


@dataclass
class GameHistory:
    initial_state: Any
    moves: list[MoveRecord] = field(default_factory=list)
    final_state: Optional[Any] = None
