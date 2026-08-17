"""Comparison primitives for Maze Runner player and search runs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from game_sandbox.games.maze_runner.environment import State
from game_sandbox.games.maze_runner.runs import PlayerMetrics, PlayerRun, PlayerRunStatus
from game_sandbox.games.maze_runner.search import SearchRun, SearchStats, StateSearchInsight


@dataclass(frozen=True)
class RunComparison:
    environment_id: str
    same_environment: bool
    player_completed: bool
    search_found_path: bool
    player_metrics: PlayerMetrics
    search_stats: SearchStats
    path_length_delta: Optional[int]
    path_cost_delta: Optional[int]


def compare_player_to_search(player_run: PlayerRun, search_run: SearchRun) -> RunComparison:
    same_environment = player_run.environment_id == search_run.environment_id
    player_metrics = player_run.metrics()
    search_stats = search_run.stats
    path_length_delta: Optional[int] = None
    path_cost_delta: Optional[int] = None

    if player_run.status == PlayerRunStatus.COMPLETED and search_stats.path_found:
        path_length_delta = player_metrics.path_length - max(search_stats.path_length - 1, 0)
        path_cost_delta = player_metrics.path_cost - search_stats.path_cost

    return RunComparison(
        environment_id=player_run.environment_id,
        same_environment=same_environment,
        player_completed=player_run.status == PlayerRunStatus.COMPLETED,
        search_found_path=search_stats.path_found,
        player_metrics=player_metrics,
        search_stats=search_stats,
        path_length_delta=path_length_delta,
        path_cost_delta=path_cost_delta,
    )


def intermediate_search_insight(
    player_run: PlayerRun,
    search_run: SearchRun,
    state: Optional[State] = None,
) -> StateSearchInsight:
    if player_run.environment_id != search_run.environment_id:
        raise ValueError("PlayerRun and SearchRun must reference the same environment.")
    return search_run.trace.insight_for_state(state or player_run.current_state)
