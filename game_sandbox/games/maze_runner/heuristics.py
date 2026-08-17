"""Heuristic functions for informed Maze Runner search algorithms."""

from __future__ import annotations

from typing import Callable

from game_sandbox.games.maze_runner.environment import State

Heuristic = Callable[[State, State], int]


def manhattan_distance(state: State, goal: State) -> int:
    return abs(goal[0] - state[0]) + abs(goal[1] - state[1])


def zero_heuristic(state: State, goal: State) -> int:
    return 0


def heuristic_name(heuristic: Heuristic) -> str:
    return getattr(heuristic, "__name__", heuristic.__class__.__name__)
