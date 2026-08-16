"""Structured metrics collected during decisions and matches."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SearchMetrics:
    nodes_explored: int = 0
    terminal_nodes: int = 0
    deep_copies: int = 0
    max_depth: int = 0
    branches_considered: int = 0
    pruning_cutoffs: int = 0


@dataclass
class DecisionMetrics:
    player: str
    agent: str
    duration_ms: float = 0.0
    search_metrics: SearchMetrics = field(default_factory=SearchMetrics)
    chosen_action: Optional[tuple] = None


@dataclass
class MatchMetrics:
    player_x_agent: str
    player_o_agent: str
    winner: Any
    no_of_moves: int = 0
    duration_ms: float = 0.0
    decisions: list[DecisionMetrics] = field(default_factory=list)

