"""Public search API for Maze Runner.

Concrete implementations live in focused modules so the Maze Runner package
keeps the same small-module shape as the rest of Mingle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from uuid import uuid4

from game_sandbox.games.maze_runner.environment import MazeEnvironment, State
from game_sandbox.games.maze_runner.heuristics import (
    Heuristic,
    heuristic_name,
    manhattan_distance,
    zero_heuristic,
)
from game_sandbox.games.maze_runner.search_algorithms import (
    a_star_search,
    breadth_first_search,
    depth_first_search,
    depth_limited_search,
    greedy_best_first_search,
    iterative_deepening_search,
    uniform_cost_search,
)
from game_sandbox.games.maze_runner.search_models import (
    SearchAlgorithm,
    SearchEvent,
    SearchEventType,
    SearchResult,
    SearchStats,
    SearchStatus,
    SearchTrace,
    StateSearchInsight,
    normalize_algorithm,
)


@dataclass
class SearchRun:
    run_id: str
    environment_id: str
    algorithm: SearchAlgorithm
    result: SearchResult

    @property
    def path(self) -> Optional[list[State]]:
        return self.result.path

    @property
    def stats(self) -> SearchStats:
        return self.result.stats

    @property
    def trace(self) -> SearchTrace:
        return self.result.trace

    @classmethod
    def run(
        cls,
        environment: MazeEnvironment,
        algorithm: SearchAlgorithm | str,
        **config: Any,
    ) -> "SearchRun":
        normalized = normalize_algorithm(algorithm)
        result = run_search(environment, normalized, **config)
        return cls(
            run_id=str(uuid4()),
            environment_id=environment.environment_id or "",
            algorithm=normalized,
            result=result,
        )


def run_search(
    environment: MazeEnvironment,
    algorithm: SearchAlgorithm | str,
    **config: Any,
) -> SearchResult:
    normalized = normalize_algorithm(algorithm)
    if normalized == SearchAlgorithm.BFS:
        return breadth_first_search(environment)
    if normalized == SearchAlgorithm.DFS:
        return depth_first_search(environment)
    if normalized == SearchAlgorithm.DLS:
        return depth_limited_search(environment, depth_limit=int(config.get("depth_limit", 0)))
    if normalized == SearchAlgorithm.IDDFS:
        max_depth = config.get("max_depth")
        return iterative_deepening_search(
            environment,
            max_depth=None if max_depth is None else int(max_depth),
        )
    if normalized == SearchAlgorithm.UCS:
        return uniform_cost_search(environment)
    if normalized == SearchAlgorithm.GREEDY_BEST_FIRST:
        return greedy_best_first_search(
            environment,
            heuristic=config.get("heuristic", manhattan_distance),
        )
    if normalized == SearchAlgorithm.ASTAR:
        return a_star_search(
            environment,
            heuristic=config.get("heuristic", manhattan_distance),
        )
    raise ValueError(f"Unsupported algorithm {normalized}.")


__all__ = [
    "Heuristic",
    "SearchAlgorithm",
    "SearchEvent",
    "SearchEventType",
    "SearchResult",
    "SearchRun",
    "SearchStats",
    "SearchStatus",
    "SearchTrace",
    "StateSearchInsight",
    "a_star_search",
    "breadth_first_search",
    "depth_first_search",
    "depth_limited_search",
    "greedy_best_first_search",
    "heuristic_name",
    "iterative_deepening_search",
    "manhattan_distance",
    "normalize_algorithm",
    "run_search",
    "uniform_cost_search",
    "zero_heuristic",
]
