"""Grid environment mechanics for Maze Runner.

The environment is the authoritative search problem. It owns movement rules,
obstacles, terrain costs, validation, and deterministic generation.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Optional

State = tuple[int, int]


class Action(Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


ACTION_DELTAS: dict[Action, State] = {
    Action.UP: (-1, 0),
    Action.DOWN: (1, 0),
    Action.LEFT: (0, -1),
    Action.RIGHT: (0, 1),
}

ACTION_ORDER: tuple[Action, ...] = (
    Action.UP,
    Action.DOWN,
    Action.LEFT,
    Action.RIGHT,
)


class TerrainCost(Enum):
    NORMAL = 1
    MUD = 2
    DIFFICULT = 3


@dataclass(frozen=True)
class Transition:
    action: Action
    from_state: State
    to_state: State
    valid: bool
    cost: int = 0
    reason: Optional[str] = None


@dataclass(frozen=True)
class EnvironmentValidation:
    valid: bool
    errors: tuple[str, ...] = ()
    solvable: Optional[bool] = None


@dataclass(frozen=True)
class MazeEnvironment:
    rows: int
    columns: int
    start: State
    goal: State
    obstacles: frozenset[State] = field(default_factory=frozenset)
    terrain_costs: Mapping[State, int] = field(default_factory=dict)
    seed: Optional[int] = None
    generation_strategy: str = "manual"
    generation_config: Mapping[str, object] = field(default_factory=dict)
    environment_id: Optional[str] = None

    def __post_init__(self) -> None:
        normalized_obstacles = frozenset(self.obstacles)
        normalized_costs = dict(self.terrain_costs)
        object.__setattr__(self, "obstacles", normalized_obstacles)
        object.__setattr__(self, "terrain_costs", normalized_costs)

        validation = self.validate(check_solvable=False)
        if validation.errors:
            raise ValueError("; ".join(validation.errors))

        if self.environment_id is None:
            object.__setattr__(self, "environment_id", self._compute_environment_id())

    @classmethod
    def random_obstacles(
        cls,
        rows: int,
        columns: int,
        obstacle_probability: float = 0.25,
        seed: Optional[int] = None,
        start: State = (0, 0),
        goal: Optional[State] = None,
        ensure_solvable: bool = True,
        max_attempts: int = 100,
    ) -> "MazeEnvironment":
        if goal is None:
            goal = (rows - 1, columns - 1)
        if not 0 <= obstacle_probability <= 1:
            raise ValueError("obstacle_probability must be between 0 and 1.")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        rng = random.Random(seed)
        last_environment: Optional[MazeEnvironment] = None
        for attempt in range(max_attempts):
            obstacles: set[State] = set()
            for row in range(rows):
                for column in range(columns):
                    state = (row, column)
                    if state in (start, goal):
                        continue
                    if rng.random() < obstacle_probability:
                        obstacles.add(state)

            environment = cls(
                rows=rows,
                columns=columns,
                start=start,
                goal=goal,
                obstacles=frozenset(obstacles),
                seed=seed,
                generation_strategy="random_obstacles",
                generation_config={
                    "obstacle_probability": obstacle_probability,
                    "attempt": attempt,
                    "ensure_solvable": ensure_solvable,
                },
            )
            last_environment = environment
            if not ensure_solvable or environment.validate(check_solvable=True).solvable:
                return environment

        if last_environment is None:
            raise ValueError("Unable to generate environment.")
        raise ValueError(
            f"Unable to generate a solvable environment after {max_attempts} attempts."
        )

    @classmethod
    def from_strings(
        cls,
        rows: Iterable[str],
        *,
        terrain_costs: Optional[Mapping[State, int]] = None,
        seed: Optional[int] = None,
        environment_id: Optional[str] = None,
    ) -> "MazeEnvironment":
        grid = [line.rstrip("\n") for line in rows]
        if not grid:
            raise ValueError("At least one row is required.")
        width = len(grid[0])
        if width == 0 or any(len(row) != width for row in grid):
            raise ValueError("All rows must have the same non-zero width.")

        start: Optional[State] = None
        goal: Optional[State] = None
        obstacles: set[State] = set()
        parsed_costs: dict[State, int] = dict(terrain_costs or {})

        for row_index, line in enumerate(grid):
            for column_index, marker in enumerate(line):
                state = (row_index, column_index)
                if marker == "S":
                    if start is not None:
                        raise ValueError("Only one start cell is allowed.")
                    start = state
                elif marker == "G":
                    if goal is not None:
                        raise ValueError("Only one goal cell is allowed.")
                    goal = state
                elif marker == "#":
                    obstacles.add(state)
                elif marker == ".":
                    continue
                elif marker.isdigit() and marker != "0":
                    parsed_costs[state] = int(marker)
                else:
                    raise ValueError(f"Unsupported map marker '{marker}'.")

        if start is None or goal is None:
            raise ValueError("String maps must contain S and G cells.")

        return cls(
            rows=len(grid),
            columns=width,
            start=start,
            goal=goal,
            obstacles=frozenset(obstacles),
            terrain_costs=parsed_costs,
            seed=seed,
            generation_strategy="string_map",
            generation_config={"rows": tuple(grid)},
            environment_id=environment_id,
        )

    def in_bounds(self, state: State) -> bool:
        row, column = state
        return 0 <= row < self.rows and 0 <= column < self.columns

    def is_obstacle(self, state: State) -> bool:
        return state in self.obstacles

    def is_walkable(self, state: State) -> bool:
        return self.in_bounds(state) and not self.is_obstacle(state)

    def terrain_cost(self, state: State) -> int:
        if not self.in_bounds(state):
            raise ValueError(f"State {state} is outside the environment.")
        if self.is_obstacle(state):
            raise ValueError(f"State {state} is blocked.")
        return int(self.terrain_costs.get(state, TerrainCost.NORMAL.value))

    def transition(self, current: State, action: Action | str) -> Transition:
        normalized_action = normalize_action(action)
        if not self.in_bounds(current):
            return Transition(
                action=normalized_action,
                from_state=current,
                to_state=current,
                valid=False,
                reason="Current state is outside the environment.",
            )
        if self.is_obstacle(current):
            return Transition(
                action=normalized_action,
                from_state=current,
                to_state=current,
                valid=False,
                reason="Current state is blocked.",
            )

        row_delta, column_delta = ACTION_DELTAS[normalized_action]
        destination = (current[0] + row_delta, current[1] + column_delta)
        if not self.in_bounds(destination):
            return Transition(
                action=normalized_action,
                from_state=current,
                to_state=current,
                valid=False,
                reason="Destination is outside the environment.",
            )
        if self.is_obstacle(destination):
            return Transition(
                action=normalized_action,
                from_state=current,
                to_state=current,
                valid=False,
                reason="Destination is blocked.",
            )
        return Transition(
            action=normalized_action,
            from_state=current,
            to_state=destination,
            valid=True,
            cost=self.terrain_cost(destination),
        )

    def get_legal_actions(self, state: State) -> list[Action]:
        return [
            action
            for action in ACTION_ORDER
            if self.transition(state, action).valid
        ]

    def neighbors(self, state: State) -> list[Transition]:
        return [
            transition
            for action in ACTION_ORDER
            if (transition := self.transition(state, action)).valid
        ]

    def action_between(self, source: State, destination: State) -> Action:
        for action in ACTION_ORDER:
            if self.transition(source, action).to_state == destination:
                return action
        raise ValueError(f"{destination} is not reachable from {source} in one action.")

    def path_cost(self, path: Optional[list[State]]) -> int:
        if not path or len(path) == 1:
            return 0
        total = 0
        for source, destination in zip(path, path[1:]):
            action = self.action_between(source, destination)
            transition = self.transition(source, action)
            if not transition.valid:
                raise ValueError(f"Invalid path segment {source} -> {destination}.")
            total += transition.cost
        return total

    def validate(self, check_solvable: bool = False) -> EnvironmentValidation:
        errors: list[str] = []
        if self.rows <= 0:
            errors.append("rows must be positive.")
        if self.columns <= 0:
            errors.append("columns must be positive.")
        if not self.in_bounds(self.start):
            errors.append("start must be inside the environment.")
        if not self.in_bounds(self.goal):
            errors.append("goal must be inside the environment.")
        if self.start == self.goal:
            errors.append("start and goal must be different.")

        for state in sorted(self.obstacles):
            if not self.in_bounds(state):
                errors.append(f"Obstacle {state} is outside the environment.")
        if self.start in self.obstacles:
            errors.append("start cannot be blocked.")
        if self.goal in self.obstacles:
            errors.append("goal cannot be blocked.")

        for state, cost in sorted(self.terrain_costs.items()):
            if not self.in_bounds(state):
                errors.append(f"Terrain state {state} is outside the environment.")
            if state in self.obstacles:
                errors.append(f"Terrain state {state} is blocked.")
            if int(cost) <= 0:
                errors.append(f"Terrain cost for {state} must be positive.")

        solvable: Optional[bool] = None
        if not errors and check_solvable:
            solvable = self.has_solution()
        return EnvironmentValidation(valid=not errors, errors=tuple(errors), solvable=solvable)

    def has_solution(self) -> bool:
        frontier: deque[State] = deque([self.start])
        visited: set[State] = {self.start}
        while frontier:
            current = frontier.popleft()
            if current == self.goal:
                return True
            for transition in self.neighbors(current):
                if transition.to_state not in visited:
                    visited.add(transition.to_state)
                    frontier.append(transition.to_state)
        return False

    def to_dict(self) -> dict[str, object]:
        return {
            "environment_id": self.environment_id,
            "rows": self.rows,
            "columns": self.columns,
            "start": list(self.start),
            "goal": list(self.goal),
            "obstacles": [list(state) for state in sorted(self.obstacles)],
            "terrain_costs": {
                f"{row},{column}": cost
                for (row, column), cost in sorted(self.terrain_costs.items())
            },
            "seed": self.seed,
            "generation_strategy": self.generation_strategy,
            "generation_config": dict(self.generation_config),
        }

    def _compute_environment_id(self) -> str:
        payload = {
            "rows": self.rows,
            "columns": self.columns,
            "start": self.start,
            "goal": self.goal,
            "obstacles": sorted(self.obstacles),
            "terrain_costs": sorted(self.terrain_costs.items()),
            "seed": self.seed,
            "generation_strategy": self.generation_strategy,
            "generation_config": dict(self.generation_config),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]


def normalize_action(action: Action | str) -> Action:
    if isinstance(action, Action):
        return action
    try:
        return Action[str(action).upper()]
    except KeyError as exc:
        valid = ", ".join(action.name for action in ACTION_ORDER)
        raise ValueError(f"Unknown action '{action}'. Valid actions: {valid}.") from exc
