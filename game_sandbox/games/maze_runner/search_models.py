"""Shared search result, trace, and statistics models for Maze Runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from game_sandbox.games.maze_runner.environment import Action, State


class SearchAlgorithm(Enum):
    BFS = "bfs"
    DFS = "dfs"
    DLS = "dls"
    IDDFS = "iddfs"
    UCS = "ucs"
    GREEDY_BEST_FIRST = "greedy_best_first"
    ASTAR = "astar"


class SearchStatus(Enum):
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    CUTOFF = "CUTOFF"


class SearchEventType(Enum):
    SEARCH_STARTED = "SEARCH_STARTED"
    ITERATION_STARTED = "ITERATION_STARTED"
    FRONTIER_PUSHED = "FRONTIER_PUSHED"
    FRONTIER_POPPED = "FRONTIER_POPPED"
    FRONTIER_UPDATED = "FRONTIER_UPDATED"
    NODE_DISCOVERED = "NODE_DISCOVERED"
    NODE_EXPANDED = "NODE_EXPANDED"
    NODE_CLOSED = "NODE_CLOSED"
    PARENT_SET = "PARENT_SET"
    DEPTH_LIMIT_REACHED = "DEPTH_LIMIT_REACHED"
    PATH_RECONSTRUCTED = "PATH_RECONSTRUCTED"
    SEARCH_FINISHED = "SEARCH_FINISHED"


@dataclass(frozen=True)
class SearchEvent:
    step: int
    event_type: SearchEventType
    state: Optional[State] = None
    action: Optional[Action] = None
    parent: Optional[State] = None
    depth: Optional[int] = None
    cost: Optional[int] = None
    frontier_size: Optional[int] = None
    iteration: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StateSearchInsight:
    state: State
    discovered: bool = False
    expanded: bool = False
    closed: bool = False
    discovered_step: Optional[int] = None
    expanded_step: Optional[int] = None
    closed_step: Optional[int] = None
    parent: Optional[State] = None
    depth: Optional[int] = None
    cost: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchTrace:
    events: list[SearchEvent] = field(default_factory=list)

    def add(
        self,
        event_type: SearchEventType,
        *,
        state: Optional[State] = None,
        action: Optional[Action] = None,
        parent: Optional[State] = None,
        depth: Optional[int] = None,
        cost: Optional[int] = None,
        frontier_size: Optional[int] = None,
        iteration: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> SearchEvent:
        event = SearchEvent(
            step=len(self.events) + 1,
            event_type=event_type,
            state=state,
            action=action,
            parent=parent,
            depth=depth,
            cost=cost,
            frontier_size=frontier_size,
            iteration=iteration,
            metadata=metadata or {},
        )
        self.events.append(event)
        return event

    def replay(self) -> list[SearchEvent]:
        return list(self.events)

    def expanded_order(self) -> list[State]:
        return [
            event.state
            for event in self.events
            if event.event_type == SearchEventType.NODE_EXPANDED and event.state is not None
        ]

    def discovered_order(self) -> list[State]:
        return [
            event.state
            for event in self.events
            if event.event_type == SearchEventType.NODE_DISCOVERED and event.state is not None
        ]

    def events_for_state(self, state: State) -> list[SearchEvent]:
        return [event for event in self.events if event.state == state]

    def insight_for_state(self, state: State) -> StateSearchInsight:
        insight = StateSearchInsight(state=state)
        for event in self.events_for_state(state):
            if event.event_type == SearchEventType.NODE_DISCOVERED:
                insight.discovered = True
                insight.discovered_step = insight.discovered_step or event.step
            elif event.event_type == SearchEventType.NODE_EXPANDED:
                insight.expanded = True
                insight.expanded_step = insight.expanded_step or event.step
            elif event.event_type == SearchEventType.NODE_CLOSED:
                insight.closed = True
                insight.closed_step = insight.closed_step or event.step
            elif event.event_type == SearchEventType.PARENT_SET:
                insight.parent = event.parent

            if event.depth is not None:
                insight.depth = event.depth
            if event.cost is not None:
                insight.cost = event.cost
            insight.metadata.update(event.metadata)
        return insight


@dataclass
class SearchStats:
    nodes_expanded: int = 0
    nodes_discovered: int = 0
    max_frontier_size: int = 0
    path_length: int = 0
    path_cost: int = 0
    execution_time_ms: float = 0.0
    path_found: bool = False
    iterations: int = 0
    depth_limit: Optional[int] = None
    cutoff_reached: bool = False
    total_nodes_expanded: int = 0
    total_nodes_discovered: int = 0
    heuristic_name: Optional[str] = None


@dataclass
class SearchResult:
    algorithm: SearchAlgorithm
    environment_id: str
    status: SearchStatus
    path: Optional[list[State]]
    stats: SearchStats
    trace: SearchTrace


def normalize_algorithm(algorithm: SearchAlgorithm | str) -> SearchAlgorithm:
    if isinstance(algorithm, SearchAlgorithm):
        return algorithm
    token = str(algorithm).lower()
    aliases = {
        "gbfs": SearchAlgorithm.GREEDY_BEST_FIRST,
        "greedy": SearchAlgorithm.GREEDY_BEST_FIRST,
        "greedy_best_first_search": SearchAlgorithm.GREEDY_BEST_FIRST,
        "a*": SearchAlgorithm.ASTAR,
        "a_star": SearchAlgorithm.ASTAR,
    }
    if token in aliases:
        return aliases[token]
    for known in SearchAlgorithm:
        if known.value == token or known.name.lower() == token:
            return known
    valid = ", ".join(known.value for known in SearchAlgorithm)
    raise ValueError(f"Unknown search algorithm '{algorithm}'. Valid algorithms: {valid}.")
