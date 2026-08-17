"""Player-run mechanics for Maze Runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from game_sandbox.games.maze_runner.environment import (
    Action,
    MazeEnvironment,
    State,
    normalize_action,
)


class PlayerRunStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


@dataclass(frozen=True)
class PlayerActionRecord:
    action: Action
    from_state: State
    to_state: State
    valid: bool
    cost: int
    timestamp: datetime
    reason: Optional[str] = None


@dataclass(frozen=True)
class HintEvent:
    algorithm: str
    level: str
    requested_state: State
    cost: int
    timestamp: datetime
    available: bool
    suggested_action: Optional[Action] = None
    suggested_state: Optional[State] = None
    route: Optional[list[State]] = None
    reason: Optional[str] = None


@dataclass
class PlayerMetrics:
    total_actions: int = 0
    valid_actions: int = 0
    invalid_actions: int = 0
    path_length: int = 0
    path_cost: int = 0
    unique_states: int = 0
    revisited_states: int = 0
    hints_used: int = 0
    hint_points_spent: int = 0
    total_duration_ms: Optional[float] = None


@dataclass
class PlayerRun:
    environment: MazeEnvironment
    run_id: str = field(default_factory=lambda: str(uuid4()))
    current_state: State = field(init=False)
    status: PlayerRunStatus = field(default=PlayerRunStatus.IN_PROGRESS, init=False)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    action_history: list[PlayerActionRecord] = field(default_factory=list)
    trajectory: list[State] = field(init=False)
    movement_cost: int = 0
    hint_history: list[HintEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.current_state = self.environment.start
        self.trajectory = [self.environment.start]

    @property
    def environment_id(self) -> str:
        return self.environment.environment_id or ""

    def move(
        self,
        action: Action | str,
        *,
        timestamp: Optional[datetime] = None,
    ) -> PlayerActionRecord:
        if self.status != PlayerRunStatus.IN_PROGRESS:
            raise ValueError("Player run is no longer in progress.")

        normalized_action = normalize_action(action)
        timestamp = timestamp or datetime.now(timezone.utc)
        transition = self.environment.transition(self.current_state, normalized_action)
        record = PlayerActionRecord(
            action=normalized_action,
            from_state=self.current_state,
            to_state=transition.to_state,
            valid=transition.valid,
            cost=transition.cost,
            timestamp=timestamp,
            reason=transition.reason,
        )
        self.action_history.append(record)

        if transition.valid:
            self.current_state = transition.to_state
            self.trajectory.append(self.current_state)
            self.movement_cost += transition.cost
            if self.current_state == self.environment.goal:
                self.status = PlayerRunStatus.COMPLETED
                self.completed_at = timestamp
        return record

    def give_up(self, *, timestamp: Optional[datetime] = None) -> None:
        if self.status != PlayerRunStatus.IN_PROGRESS:
            raise ValueError("Player run is no longer in progress.")
        self.status = PlayerRunStatus.ABANDONED
        self.completed_at = timestamp or datetime.now(timezone.utc)

    def record_hint(self, hint: HintEvent) -> None:
        self.hint_history.append(hint)

    def metrics(self, now: Optional[datetime] = None) -> PlayerMetrics:
        valid_actions = [record for record in self.action_history if record.valid]
        invalid_actions = [record for record in self.action_history if not record.valid]
        unique_states = set(self.trajectory)
        duration_end = self.completed_at or now
        total_duration_ms: Optional[float] = None
        if duration_end is not None:
            total_duration_ms = (duration_end - self.started_at).total_seconds() * 1000
        return PlayerMetrics(
            total_actions=len(self.action_history),
            valid_actions=len(valid_actions),
            invalid_actions=len(invalid_actions),
            path_length=max(len(self.trajectory) - 1, 0),
            path_cost=self.movement_cost,
            unique_states=len(unique_states),
            revisited_states=len(self.trajectory) - len(unique_states),
            hints_used=len(self.hint_history),
            hint_points_spent=sum(hint.cost for hint in self.hint_history),
            total_duration_ms=total_duration_ms,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "environment_id": self.environment_id,
            "current_state": list(self.current_state),
            "status": self.status.value,
            "trajectory": [list(state) for state in self.trajectory],
            "movement_cost": self.movement_cost,
            "actions": [
                {
                    "action": record.action.value,
                    "from_state": list(record.from_state),
                    "to_state": list(record.to_state),
                    "valid": record.valid,
                    "cost": record.cost,
                    "timestamp": record.timestamp.isoformat(),
                    "reason": record.reason,
                }
                for record in self.action_history
            ],
            "hints": [
                {
                    "algorithm": hint.algorithm,
                    "level": hint.level,
                    "requested_state": list(hint.requested_state),
                    "cost": hint.cost,
                    "available": hint.available,
                    "suggested_action": (
                        hint.suggested_action.value if hint.suggested_action else None
                    ),
                    "suggested_state": (
                        list(hint.suggested_state) if hint.suggested_state else None
                    ),
                    "route": [list(state) for state in hint.route] if hint.route else None,
                    "timestamp": hint.timestamp.isoformat(),
                    "reason": hint.reason,
                }
                for hint in self.hint_history
            ],
        }
