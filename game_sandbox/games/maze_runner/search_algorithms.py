"""Concrete Maze Runner search algorithm implementations."""

from __future__ import annotations

import heapq
import itertools
import time
from collections import deque
from typing import Optional

from game_sandbox.games.maze_runner.environment import Action, MazeEnvironment, State
from game_sandbox.games.maze_runner.heuristics import (
    Heuristic,
    heuristic_name,
    manhattan_distance,
)
from game_sandbox.games.maze_runner.search_models import (
    SearchAlgorithm,
    SearchEventType,
    SearchResult,
    SearchStats,
    SearchStatus,
    SearchTrace,
)


def breadth_first_search(environment: MazeEnvironment) -> SearchResult:
    stats = SearchStats()
    trace = SearchTrace()
    parent: dict[State, Optional[State]] = {environment.start: None}
    depths: dict[State, int] = {environment.start: 0}
    costs: dict[State, int] = {environment.start: 0}
    frontier: deque[State] = deque([environment.start])
    visited: set[State] = {environment.start}

    started_at = time.perf_counter()
    _record_start(trace, stats, environment.start)

    while frontier:
        stats.max_frontier_size = max(stats.max_frontier_size, len(frontier))
        current = frontier.popleft()
        trace.add(SearchEventType.FRONTIER_POPPED, state=current, frontier_size=len(frontier))
        _record_expansion(trace, stats, current, depths[current], costs[current])

        if current == environment.goal:
            return _finish_found(
                environment,
                SearchAlgorithm.BFS,
                parent,
                stats,
                trace,
                started_at,
            )

        for transition in environment.neighbors(current):
            neighbor = transition.to_state
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = current
            depths[neighbor] = depths[current] + 1
            costs[neighbor] = costs[current] + transition.cost
            _record_discovery(
                trace,
                stats,
                neighbor,
                parent=current,
                action=transition.action,
                depth=depths[neighbor],
                cost=costs[neighbor],
            )
            frontier.append(neighbor)
            trace.add(
                SearchEventType.FRONTIER_PUSHED,
                state=neighbor,
                frontier_size=len(frontier),
                depth=depths[neighbor],
                cost=costs[neighbor],
            )
            stats.max_frontier_size = max(stats.max_frontier_size, len(frontier))
        trace.add(SearchEventType.NODE_CLOSED, state=current, depth=depths[current], cost=costs[current])

    return _finish_not_found(environment, SearchAlgorithm.BFS, stats, trace, started_at)


def depth_first_search(environment: MazeEnvironment) -> SearchResult:
    stats = SearchStats()
    trace = SearchTrace()
    parent: dict[State, Optional[State]] = {environment.start: None}
    depths: dict[State, int] = {environment.start: 0}
    costs: dict[State, int] = {environment.start: 0}
    frontier: list[State] = [environment.start]
    visited: set[State] = {environment.start}

    started_at = time.perf_counter()
    _record_start(trace, stats, environment.start)

    while frontier:
        stats.max_frontier_size = max(stats.max_frontier_size, len(frontier))
        current = frontier.pop()
        trace.add(SearchEventType.FRONTIER_POPPED, state=current, frontier_size=len(frontier))
        _record_expansion(trace, stats, current, depths[current], costs[current])

        if current == environment.goal:
            return _finish_found(
                environment,
                SearchAlgorithm.DFS,
                parent,
                stats,
                trace,
                started_at,
            )

        for transition in reversed(environment.neighbors(current)):
            neighbor = transition.to_state
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = current
            depths[neighbor] = depths[current] + 1
            costs[neighbor] = costs[current] + transition.cost
            _record_discovery(
                trace,
                stats,
                neighbor,
                parent=current,
                action=transition.action,
                depth=depths[neighbor],
                cost=costs[neighbor],
            )
            frontier.append(neighbor)
            trace.add(
                SearchEventType.FRONTIER_PUSHED,
                state=neighbor,
                frontier_size=len(frontier),
                depth=depths[neighbor],
                cost=costs[neighbor],
            )
            stats.max_frontier_size = max(stats.max_frontier_size, len(frontier))
        trace.add(SearchEventType.NODE_CLOSED, state=current, depth=depths[current], cost=costs[current])

    return _finish_not_found(environment, SearchAlgorithm.DFS, stats, trace, started_at)


def depth_limited_search(environment: MazeEnvironment, depth_limit: int) -> SearchResult:
    if depth_limit < 0:
        raise ValueError("depth_limit must be non-negative.")
    stats = SearchStats(depth_limit=depth_limit)
    trace = SearchTrace()
    started_at = time.perf_counter()
    parent: dict[State, Optional[State]] = {environment.start: None}
    found, cutoff = _depth_limited_iteration(
        environment,
        depth_limit,
        trace,
        stats,
        parent,
        iteration=None,
    )
    stats.cutoff_reached = cutoff
    if found:
        return _finish_found(
            environment,
            SearchAlgorithm.DLS,
            parent,
            stats,
            trace,
            started_at,
        )
    return _finish_not_found(
        environment,
        SearchAlgorithm.DLS,
        stats,
        trace,
        started_at,
        status=SearchStatus.CUTOFF if cutoff else SearchStatus.NOT_FOUND,
    )


def iterative_deepening_search(
    environment: MazeEnvironment,
    max_depth: Optional[int] = None,
) -> SearchResult:
    if max_depth is None:
        max_depth = environment.rows * environment.columns - 1
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative.")

    stats = SearchStats(depth_limit=max_depth)
    trace = SearchTrace()
    started_at = time.perf_counter()
    trace.add(SearchEventType.SEARCH_STARTED, state=environment.start)
    cutoff_seen = False

    for depth_limit in range(max_depth + 1):
        parent: dict[State, Optional[State]] = {environment.start: None}
        stats.iterations += 1
        trace.add(
            SearchEventType.ITERATION_STARTED,
            state=environment.start,
            depth=depth_limit,
            iteration=stats.iterations,
            metadata={"depth_limit": depth_limit},
        )
        before_expanded = stats.nodes_expanded
        before_discovered = stats.nodes_discovered
        found, cutoff = _depth_limited_iteration(
            environment,
            depth_limit,
            trace,
            stats,
            parent,
            iteration=stats.iterations,
            add_search_start=False,
        )
        cutoff_seen = cutoff_seen or cutoff
        stats.total_nodes_expanded += stats.nodes_expanded - before_expanded
        stats.total_nodes_discovered += stats.nodes_discovered - before_discovered
        if found:
            return _finish_found(
                environment,
                SearchAlgorithm.IDDFS,
                parent,
                stats,
                trace,
                started_at,
            )

    stats.cutoff_reached = cutoff_seen
    return _finish_not_found(
        environment,
        SearchAlgorithm.IDDFS,
        stats,
        trace,
        started_at,
        status=SearchStatus.CUTOFF if cutoff_seen else SearchStatus.NOT_FOUND,
    )


def uniform_cost_search(environment: MazeEnvironment) -> SearchResult:
    return _priority_search(
        environment,
        SearchAlgorithm.UCS,
        heuristic=None,
        priority_mode="cost",
    )


def greedy_best_first_search(
    environment: MazeEnvironment,
    heuristic: Heuristic = manhattan_distance,
) -> SearchResult:
    return _priority_search(
        environment,
        SearchAlgorithm.GREEDY_BEST_FIRST,
        heuristic=heuristic,
        priority_mode="heuristic",
    )


def a_star_search(
    environment: MazeEnvironment,
    heuristic: Heuristic = manhattan_distance,
) -> SearchResult:
    return _priority_search(
        environment,
        SearchAlgorithm.ASTAR,
        heuristic=heuristic,
        priority_mode="astar",
    )


def _priority_search(
    environment: MazeEnvironment,
    algorithm: SearchAlgorithm,
    *,
    heuristic: Optional[Heuristic],
    priority_mode: str,
) -> SearchResult:
    stats = SearchStats(heuristic_name=heuristic_name(heuristic) if heuristic else None)
    trace = SearchTrace()
    parent: dict[State, Optional[State]] = {environment.start: None}
    depths: dict[State, int] = {environment.start: 0}
    costs: dict[State, int] = {environment.start: 0}
    closed: set[State] = set()
    frontier: list[tuple[int, int, int, State]] = []
    sequence = itertools.count()

    started_at = time.perf_counter()
    trace.add(SearchEventType.SEARCH_STARTED, state=environment.start)
    start_h = heuristic(environment.start, environment.goal) if heuristic else 0
    start_priority = _priority_for(priority_mode, g=0, h=start_h)
    heapq.heappush(frontier, (start_priority, 0, next(sequence), environment.start))
    stats.nodes_discovered = 1
    stats.max_frontier_size = 1
    metadata = _priority_metadata(priority_mode, g=0, h=start_h, priority=start_priority)
    trace.add(SearchEventType.NODE_DISCOVERED, state=environment.start, depth=0, cost=0, metadata=metadata)
    trace.add(
        SearchEventType.FRONTIER_PUSHED,
        state=environment.start,
        frontier_size=1,
        depth=0,
        cost=0,
        metadata=metadata,
    )

    while frontier:
        stats.max_frontier_size = max(stats.max_frontier_size, len(frontier))
        priority, g_cost, _, current = heapq.heappop(frontier)
        if current in closed:
            continue
        if g_cost != costs[current] and priority_mode != "heuristic":
            continue

        current_h = heuristic(current, environment.goal) if heuristic else 0
        metadata = _priority_metadata(priority_mode, g=costs[current], h=current_h, priority=priority)
        trace.add(
            SearchEventType.FRONTIER_POPPED,
            state=current,
            frontier_size=len(frontier),
            depth=depths[current],
            cost=costs[current],
            metadata=metadata,
        )
        _record_expansion(
            trace,
            stats,
            current,
            depths[current],
            costs[current],
            metadata=metadata,
        )

        if current == environment.goal:
            return _finish_found(
                environment,
                algorithm,
                parent,
                stats,
                trace,
                started_at,
            )

        closed.add(current)
        trace.add(
            SearchEventType.NODE_CLOSED,
            state=current,
            depth=depths[current],
            cost=costs[current],
            metadata=metadata,
        )

        for transition in environment.neighbors(current):
            neighbor = transition.to_state
            if neighbor in closed:
                continue
            next_cost = costs[current] + transition.cost
            next_depth = depths[current] + 1
            h_value = heuristic(neighbor, environment.goal) if heuristic else 0
            next_priority = _priority_for(priority_mode, g=next_cost, h=h_value)
            if neighbor in costs and next_cost >= costs[neighbor]:
                continue

            is_new = neighbor not in costs
            parent[neighbor] = current
            depths[neighbor] = next_depth
            costs[neighbor] = next_cost
            metadata = _priority_metadata(
                priority_mode,
                g=next_cost,
                h=h_value,
                priority=next_priority,
            )
            trace.add(
                SearchEventType.PARENT_SET,
                state=neighbor,
                parent=current,
                action=transition.action,
                depth=next_depth,
                cost=next_cost,
                metadata=metadata,
            )
            if is_new:
                stats.nodes_discovered += 1
                trace.add(
                    SearchEventType.NODE_DISCOVERED,
                    state=neighbor,
                    action=transition.action,
                    parent=current,
                    depth=next_depth,
                    cost=next_cost,
                    metadata=metadata,
                )
            else:
                trace.add(
                    SearchEventType.FRONTIER_UPDATED,
                    state=neighbor,
                    action=transition.action,
                    parent=current,
                    depth=next_depth,
                    cost=next_cost,
                    metadata=metadata,
                )

            heapq.heappush(frontier, (next_priority, next_cost, next(sequence), neighbor))
            trace.add(
                SearchEventType.FRONTIER_PUSHED,
                state=neighbor,
                frontier_size=len(frontier),
                depth=next_depth,
                cost=next_cost,
                metadata=metadata,
            )
            stats.max_frontier_size = max(stats.max_frontier_size, len(frontier))

    return _finish_not_found(environment, algorithm, stats, trace, started_at)


def _priority_for(priority_mode: str, *, g: int, h: int) -> int:
    if priority_mode == "cost":
        return g
    if priority_mode == "heuristic":
        return h
    if priority_mode == "astar":
        return g + h
    raise ValueError(f"Unknown priority mode '{priority_mode}'.")


def _priority_metadata(priority_mode: str, *, g: int, h: int, priority: int) -> dict[str, int]:
    metadata = {"g": g, "priority": priority}
    if priority_mode in {"heuristic", "astar"}:
        metadata["h"] = h
    if priority_mode == "astar":
        metadata["f"] = priority
    return metadata


def _depth_limited_iteration(
    environment: MazeEnvironment,
    depth_limit: int,
    trace: SearchTrace,
    stats: SearchStats,
    parent: dict[State, Optional[State]],
    *,
    iteration: Optional[int],
    add_search_start: bool = True,
) -> tuple[bool, bool]:
    frontier: list[tuple[State, int, int, tuple[State, ...]]] = [
        (environment.start, 0, 0, (environment.start,))
    ]
    best_depth_seen: dict[State, int] = {environment.start: 0}
    cutoff_reached = False

    if add_search_start:
        trace.add(SearchEventType.SEARCH_STARTED, state=environment.start)
    trace.add(
        SearchEventType.NODE_DISCOVERED,
        state=environment.start,
        depth=0,
        cost=0,
        iteration=iteration,
    )
    trace.add(
        SearchEventType.FRONTIER_PUSHED,
        state=environment.start,
        frontier_size=1,
        depth=0,
        cost=0,
        iteration=iteration,
    )
    stats.nodes_discovered += 1
    stats.max_frontier_size = max(stats.max_frontier_size, 1)

    while frontier:
        stats.max_frontier_size = max(stats.max_frontier_size, len(frontier))
        current, depth, cost, path = frontier.pop()
        trace.add(
            SearchEventType.FRONTIER_POPPED,
            state=current,
            frontier_size=len(frontier),
            depth=depth,
            cost=cost,
            iteration=iteration,
        )
        _record_expansion(trace, stats, current, depth, cost, iteration=iteration)

        if current == environment.goal:
            return True, cutoff_reached

        if depth >= depth_limit:
            cutoff_reached = True
            trace.add(
                SearchEventType.DEPTH_LIMIT_REACHED,
                state=current,
                depth=depth,
                cost=cost,
                iteration=iteration,
            )
            trace.add(
                SearchEventType.NODE_CLOSED,
                state=current,
                depth=depth,
                cost=cost,
                iteration=iteration,
            )
            continue

        for transition in reversed(environment.neighbors(current)):
            neighbor = transition.to_state
            next_depth = depth + 1
            if neighbor in path:
                continue
            if best_depth_seen.get(neighbor, next_depth + 1) <= next_depth:
                continue
            best_depth_seen[neighbor] = next_depth
            parent[neighbor] = current
            next_cost = cost + transition.cost
            _record_discovery(
                trace,
                stats,
                neighbor,
                parent=current,
                action=transition.action,
                depth=next_depth,
                cost=next_cost,
                iteration=iteration,
            )
            frontier.append((neighbor, next_depth, next_cost, path + (neighbor,)))
            trace.add(
                SearchEventType.FRONTIER_PUSHED,
                state=neighbor,
                frontier_size=len(frontier),
                depth=next_depth,
                cost=next_cost,
                iteration=iteration,
            )
            stats.max_frontier_size = max(stats.max_frontier_size, len(frontier))
        trace.add(
            SearchEventType.NODE_CLOSED,
            state=current,
            depth=depth,
            cost=cost,
            iteration=iteration,
        )
    return False, cutoff_reached


def _record_start(trace: SearchTrace, stats: SearchStats, start: State) -> None:
    trace.add(SearchEventType.SEARCH_STARTED, state=start)
    trace.add(SearchEventType.NODE_DISCOVERED, state=start, depth=0, cost=0)
    trace.add(SearchEventType.FRONTIER_PUSHED, state=start, frontier_size=1)
    stats.nodes_discovered = 1
    stats.max_frontier_size = 1


def _record_discovery(
    trace: SearchTrace,
    stats: SearchStats,
    state: State,
    *,
    parent: Optional[State],
    action: Action,
    depth: int,
    cost: int,
    iteration: Optional[int] = None,
    metadata: Optional[dict[str, int]] = None,
) -> None:
    stats.nodes_discovered += 1
    trace.add(
        SearchEventType.PARENT_SET,
        state=state,
        parent=parent,
        action=action,
        depth=depth,
        cost=cost,
        iteration=iteration,
        metadata=metadata,
    )
    trace.add(
        SearchEventType.NODE_DISCOVERED,
        state=state,
        action=action,
        parent=parent,
        depth=depth,
        cost=cost,
        iteration=iteration,
        metadata=metadata,
    )


def _record_expansion(
    trace: SearchTrace,
    stats: SearchStats,
    state: State,
    depth: int,
    cost: int,
    *,
    iteration: Optional[int] = None,
    metadata: Optional[dict[str, int]] = None,
) -> None:
    stats.nodes_expanded += 1
    trace.add(
        SearchEventType.NODE_EXPANDED,
        state=state,
        depth=depth,
        cost=cost,
        iteration=iteration,
        metadata=metadata,
    )


def _finish_found(
    environment: MazeEnvironment,
    algorithm: SearchAlgorithm,
    parent: dict[State, Optional[State]],
    stats: SearchStats,
    trace: SearchTrace,
    started_at: float,
) -> SearchResult:
    path = _reconstruct_path(parent, environment.start, environment.goal)
    stats.path_found = True
    stats.path_length = len(path)
    stats.path_cost = environment.path_cost(path)
    stats.execution_time_ms = (time.perf_counter() - started_at) * 1000
    if stats.total_nodes_expanded == 0:
        stats.total_nodes_expanded = stats.nodes_expanded
    if stats.total_nodes_discovered == 0:
        stats.total_nodes_discovered = stats.nodes_discovered
    trace.add(
        SearchEventType.PATH_RECONSTRUCTED,
        state=environment.goal,
        metadata={"path": path},
    )
    trace.add(
        SearchEventType.SEARCH_FINISHED,
        state=environment.goal,
        metadata={"status": SearchStatus.FOUND.value},
    )
    return SearchResult(
        algorithm=algorithm,
        environment_id=environment.environment_id or "",
        status=SearchStatus.FOUND,
        path=path,
        stats=stats,
        trace=trace,
    )


def _finish_not_found(
    environment: MazeEnvironment,
    algorithm: SearchAlgorithm,
    stats: SearchStats,
    trace: SearchTrace,
    started_at: float,
    *,
    status: SearchStatus = SearchStatus.NOT_FOUND,
) -> SearchResult:
    stats.execution_time_ms = (time.perf_counter() - started_at) * 1000
    if stats.total_nodes_expanded == 0:
        stats.total_nodes_expanded = stats.nodes_expanded
    if stats.total_nodes_discovered == 0:
        stats.total_nodes_discovered = stats.nodes_discovered
    trace.add(
        SearchEventType.SEARCH_FINISHED,
        state=environment.goal,
        metadata={"status": status.value},
    )
    return SearchResult(
        algorithm=algorithm,
        environment_id=environment.environment_id or "",
        status=status,
        path=None,
        stats=stats,
        trace=trace,
    )


def _reconstruct_path(
    parent: dict[State, Optional[State]],
    start: State,
    goal: State,
) -> list[State]:
    if goal not in parent:
        return []
    path: list[State] = []
    current: Optional[State] = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    if not path or path[0] != start:
        raise ValueError("Parent map does not reconstruct a path from start to goal.")
    return path
