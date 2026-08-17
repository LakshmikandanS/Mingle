"""Hint mechanics backed by actual Maze Runner search runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from game_sandbox.games.maze_runner.runs import HintEvent, PlayerRun
from game_sandbox.games.maze_runner.search import SearchRun


class HintLevel(Enum):
    NEXT_ACTION = "NEXT_ACTION"
    NEXT_STATE = "NEXT_STATE"
    PARTIAL_ROUTE = "PARTIAL_ROUTE"
    FULL_SOLUTION = "FULL_SOLUTION"


DEFAULT_HINT_COSTS: dict[str, dict[HintLevel, int]] = {
    "dfs": {
        HintLevel.NEXT_ACTION: 1,
        HintLevel.NEXT_STATE: 1,
        HintLevel.PARTIAL_ROUTE: 2,
        HintLevel.FULL_SOLUTION: 3,
    },
    "bfs": {
        HintLevel.NEXT_ACTION: 1,
        HintLevel.NEXT_STATE: 1,
        HintLevel.PARTIAL_ROUTE: 2,
        HintLevel.FULL_SOLUTION: 3,
    },
    "dls": {
        HintLevel.NEXT_ACTION: 1,
        HintLevel.NEXT_STATE: 1,
        HintLevel.PARTIAL_ROUTE: 2,
        HintLevel.FULL_SOLUTION: 3,
    },
    "iddfs": {
        HintLevel.NEXT_ACTION: 2,
        HintLevel.NEXT_STATE: 2,
        HintLevel.PARTIAL_ROUTE: 3,
        HintLevel.FULL_SOLUTION: 4,
    },
    "ucs": {
        HintLevel.NEXT_ACTION: 2,
        HintLevel.NEXT_STATE: 2,
        HintLevel.PARTIAL_ROUTE: 3,
        HintLevel.FULL_SOLUTION: 4,
    },
    "greedy_best_first": {
        HintLevel.NEXT_ACTION: 2,
        HintLevel.NEXT_STATE: 2,
        HintLevel.PARTIAL_ROUTE: 3,
        HintLevel.FULL_SOLUTION: 4,
    },
    "astar": {
        HintLevel.NEXT_ACTION: 3,
        HintLevel.NEXT_STATE: 3,
        HintLevel.PARTIAL_ROUTE: 4,
        HintLevel.FULL_SOLUTION: 5,
    },
}


@dataclass(frozen=True)
class HintCostPolicy:
    costs: dict[str, dict[HintLevel, int]] = field(default_factory=lambda: DEFAULT_HINT_COSTS)
    default_cost: int = 1

    def cost_for(self, algorithm: str, level: HintLevel) -> int:
        return self.costs.get(algorithm, {}).get(level, self.default_cost)


@dataclass
class HintProvider:
    cost_policy: HintCostPolicy = field(default_factory=HintCostPolicy)
    partial_route_length: int = 3

    def generate_hint(
        self,
        player_run: PlayerRun,
        search_run: SearchRun,
        level: HintLevel | str,
    ) -> HintEvent:
        normalized_level = normalize_hint_level(level)
        algorithm = search_run.algorithm.value
        cost = self.cost_policy.cost_for(algorithm, normalized_level)
        timestamp = datetime.now(timezone.utc)

        if player_run.environment_id != search_run.environment_id:
            hint = HintEvent(
                algorithm=algorithm,
                level=normalized_level.value,
                requested_state=player_run.current_state,
                cost=cost,
                timestamp=timestamp,
                available=False,
                reason="Search run belongs to a different environment.",
            )
            player_run.record_hint(hint)
            return hint

        path = search_run.path
        if not path:
            hint = HintEvent(
                algorithm=algorithm,
                level=normalized_level.value,
                requested_state=player_run.current_state,
                cost=cost,
                timestamp=timestamp,
                available=False,
                reason="Search run did not find a solution.",
            )
            player_run.record_hint(hint)
            return hint

        try:
            current_index = path.index(player_run.current_state)
        except ValueError:
            hint = HintEvent(
                algorithm=algorithm,
                level=normalized_level.value,
                requested_state=player_run.current_state,
                cost=cost,
                timestamp=timestamp,
                available=False,
                reason="Current player state is not on the search run solution path.",
            )
            player_run.record_hint(hint)
            return hint

        if current_index == len(path) - 1:
            hint = HintEvent(
                algorithm=algorithm,
                level=normalized_level.value,
                requested_state=player_run.current_state,
                cost=cost,
                timestamp=timestamp,
                available=False,
                reason="Player is already at the goal.",
            )
            player_run.record_hint(hint)
            return hint

        next_state = path[current_index + 1]
        action = player_run.environment.action_between(player_run.current_state, next_state)
        route = path[current_index:]
        if normalized_level == HintLevel.NEXT_ACTION:
            hint = HintEvent(
                algorithm=algorithm,
                level=normalized_level.value,
                requested_state=player_run.current_state,
                cost=cost,
                timestamp=timestamp,
                available=True,
                suggested_action=action,
            )
        elif normalized_level == HintLevel.NEXT_STATE:
            hint = HintEvent(
                algorithm=algorithm,
                level=normalized_level.value,
                requested_state=player_run.current_state,
                cost=cost,
                timestamp=timestamp,
                available=True,
                suggested_state=next_state,
            )
        elif normalized_level == HintLevel.PARTIAL_ROUTE:
            hint = HintEvent(
                algorithm=algorithm,
                level=normalized_level.value,
                requested_state=player_run.current_state,
                cost=cost,
                timestamp=timestamp,
                available=True,
                route=route[: self.partial_route_length + 1],
            )
        else:
            hint = HintEvent(
                algorithm=algorithm,
                level=normalized_level.value,
                requested_state=player_run.current_state,
                cost=cost,
                timestamp=timestamp,
                available=True,
                route=route,
            )

        player_run.record_hint(hint)
        return hint


def normalize_hint_level(level: HintLevel | str) -> HintLevel:
    if isinstance(level, HintLevel):
        return level
    token = str(level).upper()
    try:
        return HintLevel[token]
    except KeyError:
        for known in HintLevel:
            if known.value == token:
                return known
    valid = ", ".join(known.value for known in HintLevel)
    raise ValueError(f"Unknown hint level '{level}'. Valid levels: {valid}.")
