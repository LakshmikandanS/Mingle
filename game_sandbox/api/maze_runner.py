"""Maze Runner API routes.

The route layer owns lookup, HTTP errors, and JSON serialization. Maze Runner's
domain modules remain the source of truth for environment rules, player runs,
search algorithms, traces, hints, documentation, and comparisons.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from game_sandbox.api.schemas import (
    MazeComparisonRequest,
    MazeEnvironmentRequest,
    MazeHintRequest,
    MazeIntermediateComparisonRequest,
    MazePlayerActionRequest,
    MazePlayerRunRequest,
    MazeSearchRunRequest,
)
from game_sandbox.games.maze_runner.comparison import (
    compare_player_to_search,
    intermediate_search_insight,
)
from game_sandbox.games.maze_runner.documentation import (
    ALGORITHM_DOCUMENTATION,
    get_algorithm_documentation,
)
from game_sandbox.games.maze_runner.environment import (
    ACTION_ORDER,
    MazeEnvironment,
    State,
)
from game_sandbox.games.maze_runner.hints import (
    DEFAULT_HINT_COSTS,
    HintProvider,
)
from game_sandbox.games.maze_runner.runs import (
    HintEvent,
    PlayerActionRecord,
    PlayerRun,
)
from game_sandbox.games.maze_runner.search import (
    SearchAlgorithm,
    SearchRun,
    normalize_algorithm,
)
from game_sandbox.games.maze_runner.search_models import (
    SearchEvent,
    StateSearchInsight,
)

router = APIRouter(prefix="/maze", tags=["maze-runner"])

_environments: dict[str, MazeEnvironment] = {}
_player_runs: dict[str, PlayerRun] = {}
_search_runs: dict[str, SearchRun] = {}

_PLANNED_ALGORITHMS: dict[str, dict[str, str]] = {
    "ida_star": {
        "name": "Iterative Deepening A*",
        "category": "memory_bounded",
        "status": "planned",
    },
    "rbfs": {
        "name": "Recursive Best-First Search",
        "category": "memory_bounded",
        "status": "planned",
    },
    "sma_star": {
        "name": "Simplified Memory-Bounded A*",
        "category": "memory_bounded",
        "status": "planned",
    },
}

_ALGORITHM_CATEGORIES: dict[SearchAlgorithm, str] = {
    SearchAlgorithm.BFS: "uninformed",
    SearchAlgorithm.DFS: "uninformed",
    SearchAlgorithm.DLS: "uninformed",
    SearchAlgorithm.IDDFS: "uninformed",
    SearchAlgorithm.UCS: "cost",
    SearchAlgorithm.GREEDY_BEST_FIRST: "heuristic",
    SearchAlgorithm.ASTAR: "heuristic",
}


@router.post("/environments")
def create_environment_endpoint(request: MazeEnvironmentRequest) -> dict[str, Any]:
    try:
        environment = _create_environment(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _environments[environment.environment_id or ""] = environment
    return _environment_to_dict(environment)


@router.get("/environments/{environment_id}")
def get_environment_endpoint(environment_id: str) -> dict[str, Any]:
    return _environment_to_dict(_get_environment(environment_id))


@router.post("/runs/player")
def create_player_run_endpoint(request: MazePlayerRunRequest) -> dict[str, Any]:
    player_run = PlayerRun(_get_environment(request.environment_id))
    _player_runs[player_run.run_id] = player_run
    return _player_run_to_dict(player_run)


@router.get("/runs/player/{run_id}")
def get_player_run_endpoint(run_id: str) -> dict[str, Any]:
    return _player_run_to_dict(_get_player_run(run_id))


@router.post("/runs/player/{run_id}/action")
def move_player_run_endpoint(run_id: str, request: MazePlayerActionRequest) -> dict[str, Any]:
    player_run = _get_player_run(run_id)
    try:
        record = player_run.move(request.action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _player_action_response(player_run, record)


@router.post("/runs/player/{run_id}/give-up")
def give_up_player_run_endpoint(run_id: str) -> dict[str, Any]:
    player_run = _get_player_run(run_id)
    try:
        player_run.give_up()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _player_run_to_dict(player_run)


@router.get("/runs/player/{run_id}/history")
def get_player_history_endpoint(run_id: str) -> dict[str, Any]:
    player_run = _get_player_run(run_id)
    return {
        "player_run_id": player_run.run_id,
        "environment_id": player_run.environment_id,
        "status": player_run.status.value,
        "actions": [_action_record_to_dict(record) for record in player_run.action_history],
        "trajectory": [_state_to_list(state) for state in player_run.trajectory],
        "metrics": _dataclass_to_dict(player_run.metrics()),
    }


@router.get("/runs/player/{run_id}/hints")
def get_hint_history_endpoint(run_id: str) -> dict[str, Any]:
    player_run = _get_player_run(run_id)
    return {
        "player_run_id": player_run.run_id,
        "environment_id": player_run.environment_id,
        "hints": [
            _hint_to_dict(hint, player_run=player_run, index=index)
            for index, hint in enumerate(player_run.hint_history, start=1)
        ],
        "metrics": _dataclass_to_dict(player_run.metrics()),
    }


@router.post("/runs/player/{run_id}/hints")
def create_hint_endpoint(run_id: str, request: MazeHintRequest) -> dict[str, Any]:
    player_run = _get_player_run(run_id)
    level = request.hint_level or request.level
    if level is None:
        raise HTTPException(status_code=400, detail="hint_level is required.")

    search_run = _search_run_for_hint(player_run, request)
    try:
        hint = HintProvider().generate_hint(player_run, search_run, level)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _hint_to_dict(
        hint,
        player_run=player_run,
        index=len(player_run.hint_history),
        search_run=search_run,
    )


@router.post("/runs/search")
def create_search_run_endpoint(request: MazeSearchRunRequest) -> dict[str, Any]:
    environment = _get_environment(request.environment_id)
    algorithm = _implemented_algorithm_or_error(request.algorithm)
    try:
        search_run = SearchRun.run(environment, algorithm, **request.configuration)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _search_runs[search_run.run_id] = search_run
    return _search_run_to_dict(search_run)


@router.get("/runs/search/{run_id}")
def get_search_run_endpoint(run_id: str) -> dict[str, Any]:
    return _search_run_to_dict(_get_search_run(run_id))


@router.get("/runs/search/{run_id}/trace")
def get_search_trace_endpoint(
    run_id: str,
    from_index: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1),
) -> dict[str, Any]:
    search_run = _get_search_run(run_id)
    events = search_run.trace.replay()
    selected = events[from_index:] if limit is None else events[from_index : from_index + limit]
    return {
        "search_run_id": search_run.run_id,
        "environment_id": search_run.environment_id,
        "algorithm": search_run.algorithm.value,
        "from_index": from_index,
        "count": len(selected),
        "total_events": len(events),
        "events": [_search_event_to_dict(event) for event in selected],
    }


@router.get("/runs/search/{run_id}/replay")
def get_search_replay_endpoint(
    run_id: str,
    from_index: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1),
) -> dict[str, Any]:
    return get_search_trace_endpoint(run_id, from_index=from_index, limit=limit)


@router.get("/runs/search/{run_id}/trace/{step}")
def get_search_trace_step_endpoint(run_id: str, step: int) -> dict[str, Any]:
    search_run = _get_search_run(run_id)
    for event in search_run.trace.replay():
        if event.step == step:
            return _search_event_to_dict(event)
    raise HTTPException(status_code=404, detail=f"Unknown trace step '{step}'.")


@router.get("/hints/costs")
def get_hint_costs_endpoint() -> dict[str, Any]:
    return {
        "costs": {
            algorithm: {level.value: cost for level, cost in levels.items()}
            for algorithm, levels in DEFAULT_HINT_COSTS.items()
        }
    }


@router.get("/algorithms")
def list_algorithms_endpoint() -> dict[str, Any]:
    available = [
        _algorithm_summary_to_dict(algorithm)
        for algorithm in sorted(SearchAlgorithm, key=lambda item: item.value)
    ]
    planned = [
        {
            "algorithm": algorithm,
            "available": False,
            **metadata,
        }
        for algorithm, metadata in _PLANNED_ALGORITHMS.items()
    ]
    return {"available": available, "planned": planned}


@router.get("/algorithms/{algorithm}")
def get_algorithm_documentation_endpoint(algorithm: str) -> dict[str, Any]:
    normalized = _implemented_algorithm_or_error(algorithm)
    return _algorithm_documentation_to_dict(normalized)


@router.post("/comparisons")
def compare_runs_endpoint(request: MazeComparisonRequest) -> dict[str, Any]:
    player_run = _get_player_run(request.player_run_id)
    search_run = _get_search_run(request.search_run_id)
    _ensure_same_environment(player_run, search_run)
    comparison = compare_player_to_search(player_run, search_run)
    return _comparison_to_dict(comparison, player_run, search_run)


@router.post("/comparisons/intermediate")
def compare_intermediate_endpoint(request: MazeIntermediateComparisonRequest) -> dict[str, Any]:
    player_run = _get_player_run(request.player_run_id)
    search_run = _get_search_run(request.search_run_id)
    _ensure_same_environment(player_run, search_run)
    state = _state_from_value(request.state, "state") if request.state is not None else None
    try:
        insight = intermediate_search_insight(player_run, search_run, state=state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "player_run_id": player_run.run_id,
        "search_run_id": search_run.run_id,
        "environment_id": player_run.environment_id,
        "player_state": _state_to_list(player_run.current_state),
        "insight": _insight_to_dict(insight),
    }


def _create_environment(request: MazeEnvironmentRequest) -> MazeEnvironment:
    string_rows = request.string_rows or request.map_rows
    if string_rows is None and isinstance(request.rows, list):
        string_rows = request.rows
    if string_rows is not None:
        return MazeEnvironment.from_strings(
            string_rows,
            terrain_costs=_terrain_costs_from_value(request.terrain_costs),
            seed=request.seed,
        )

    rows = _dimension(
        "height",
        request.height if request.height is not None else request.rows,
    )
    columns = _dimension(
        "width",
        request.width if request.width is not None else request.columns,
    )
    start = _state_from_value(request.start or [0, 0], "start")
    goal = _state_from_value(request.goal or [rows - 1, columns - 1], "goal")
    strategy = request.generation_strategy
    if strategy in {"random", "random_obstacles"}:
        return MazeEnvironment.random_obstacles(
            rows,
            columns,
            obstacle_probability=request.obstacle_probability,
            seed=request.seed,
            start=start,
            goal=goal,
            ensure_solvable=request.ensure_solvable,
            max_attempts=request.max_attempts,
        )
    if strategy not in {"manual", "empty"}:
        raise ValueError(f"Unsupported generation_strategy '{strategy}'.")

    config = dict(request.generation_config)
    if request.obstacles:
        config.setdefault("obstacles", request.obstacles)
    if request.terrain_costs:
        config.setdefault("terrain_costs", request.terrain_costs)
    return MazeEnvironment(
        rows=rows,
        columns=columns,
        start=start,
        goal=goal,
        obstacles=frozenset(_state_from_value(value, "obstacle") for value in request.obstacles),
        terrain_costs=_terrain_costs_from_value(request.terrain_costs),
        seed=request.seed,
        generation_strategy=strategy,
        generation_config=config,
    )


def _dimension(name: str, value: Any) -> int:
    if value is None:
        raise ValueError(f"{name} is required.")
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer.")
    return int(value)


def _state_from_value(value: Any, name: str) -> State:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{name} must be a [row, column] pair.")
    return (int(value[0]), int(value[1]))


def _terrain_costs_from_value(value: Any) -> dict[State, int]:
    if value in (None, ""):
        return {}
    costs: dict[State, int] = {}
    if isinstance(value, dict):
        for raw_state, raw_cost in value.items():
            costs[_state_key_to_state(raw_state)] = int(raw_cost)
        return costs
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                state = _state_from_value(item.get("state"), "terrain state")
                cost = item.get("cost")
            elif isinstance(item, (list, tuple)) and len(item) == 3:
                state = (int(item[0]), int(item[1]))
                cost = item[2]
            else:
                raise ValueError("terrain_costs entries must be {'state': [row, column], 'cost': n}.")
            costs[state] = int(cost)
        return costs
    raise ValueError("terrain_costs must be an object or list.")


def _state_key_to_state(value: Any) -> State:
    if isinstance(value, (list, tuple)):
        return _state_from_value(value, "terrain state")
    parts = str(value).split(",")
    if len(parts) != 2:
        raise ValueError("terrain_costs keys must look like 'row,column'.")
    return (int(parts[0]), int(parts[1]))


def _get_environment(environment_id: str) -> MazeEnvironment:
    try:
        return _environments[environment_id]
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown Maze Runner environment '{environment_id}'.",
        ) from exc


def _get_player_run(run_id: str) -> PlayerRun:
    try:
        return _player_runs[run_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown player run '{run_id}'.") from exc


def _get_search_run(run_id: str) -> SearchRun:
    try:
        return _search_runs[run_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown search run '{run_id}'.") from exc


def _implemented_algorithm_or_error(algorithm: str) -> SearchAlgorithm:
    token = algorithm.lower()
    if token in _PLANNED_ALGORITHMS:
        raise HTTPException(
            status_code=501,
            detail=f"Algorithm '{algorithm}' is planned but not implemented.",
        )
    try:
        return normalize_algorithm(algorithm)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _search_run_for_hint(player_run: PlayerRun, request: MazeHintRequest) -> SearchRun:
    if request.search_run_id is not None:
        search_run = _get_search_run(request.search_run_id)
        _ensure_same_environment(player_run, search_run)
        return search_run
    if request.algorithm is None:
        raise HTTPException(status_code=400, detail="algorithm or search_run_id is required.")
    algorithm = _implemented_algorithm_or_error(request.algorithm)
    try:
        search_run = SearchRun.run(player_run.environment, algorithm, **request.configuration)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _search_runs[search_run.run_id] = search_run
    return search_run


def _ensure_same_environment(player_run: PlayerRun, search_run: SearchRun) -> None:
    if player_run.environment_id != search_run.environment_id:
        raise HTTPException(
            status_code=400,
            detail="PlayerRun and SearchRun must reference the same environment.",
        )


def _environment_to_dict(environment: MazeEnvironment) -> dict[str, Any]:
    payload = environment.to_dict()
    payload.update(
        {
            "width": environment.columns,
            "height": environment.rows,
            "metadata": {
                "environment_id": environment.environment_id,
                "seed": environment.seed,
                "generation_strategy": environment.generation_strategy,
            },
            "cells": [
                [
                    {
                        "row": row,
                        "column": column,
                        "kind": _cell_kind(environment, (row, column)),
                        "terrain_cost": (
                            None
                            if (row, column) in environment.obstacles
                            else environment.terrain_cost((row, column))
                        ),
                    }
                    for column in range(environment.columns)
                ]
                for row in range(environment.rows)
            ],
        }
    )
    return payload


def _cell_kind(environment: MazeEnvironment, state: State) -> str:
    if state == environment.start:
        return "start"
    if state == environment.goal:
        return "goal"
    if state in environment.obstacles:
        return "obstacle"
    return "free"


def _player_run_to_dict(player_run: PlayerRun) -> dict[str, Any]:
    payload = player_run.to_dict()
    payload.update(
        {
            "player_run_id": player_run.run_id,
            "started_at": player_run.started_at.isoformat(),
            "completed_at": (
                player_run.completed_at.isoformat() if player_run.completed_at else None
            ),
            "completed": player_run.status.value == "COMPLETED",
            "metrics": _dataclass_to_dict(player_run.metrics()),
            "legal_actions": [
                action.value for action in player_run.environment.get_legal_actions(player_run.current_state)
            ]
            if player_run.status.value == "IN_PROGRESS"
            else [],
        }
    )
    return payload


def _player_action_response(player_run: PlayerRun, record: PlayerActionRecord) -> dict[str, Any]:
    payload = _action_record_to_dict(record)
    payload.update(
        {
            "player_run_id": player_run.run_id,
            "environment_id": player_run.environment_id,
            "current_state": _state_to_list(player_run.current_state),
            "status": player_run.status.value,
            "completed": player_run.status.value == "COMPLETED",
            "transition_cost": record.cost,
            "metrics": _dataclass_to_dict(player_run.metrics()),
            "trajectory": [_state_to_list(state) for state in player_run.trajectory],
        }
    )
    return payload


def _action_record_to_dict(record: PlayerActionRecord) -> dict[str, Any]:
    return {
        "action": record.action.value,
        "from_state": _state_to_list(record.from_state),
        "to_state": _state_to_list(record.to_state),
        "valid": record.valid,
        "cost": record.cost,
        "transition_cost": record.cost,
        "timestamp": record.timestamp.isoformat(),
        "reason": record.reason,
    }


def _search_run_to_dict(search_run: SearchRun) -> dict[str, Any]:
    path = [_state_to_list(state) for state in search_run.path] if search_run.path else None
    return {
        "search_run_id": search_run.run_id,
        "run_id": search_run.run_id,
        "environment_id": search_run.environment_id,
        "algorithm": search_run.algorithm.value,
        "status": "COMPLETED",
        "search_status": search_run.result.status.value,
        "path": path,
        "path_length": search_run.stats.path_length,
        "path_cost": search_run.stats.path_cost,
        "statistics": _dataclass_to_dict(search_run.stats),
        "trace_metadata": {
            "event_count": len(search_run.trace.events),
            "first_step": search_run.trace.events[0].step if search_run.trace.events else None,
            "last_step": search_run.trace.events[-1].step if search_run.trace.events else None,
        },
    }


def _search_event_to_dict(event: SearchEvent) -> dict[str, Any]:
    return {
        "step": event.step,
        "event_type": event.event_type.value,
        "state": _state_to_list(event.state),
        "action": event.action.value if event.action else None,
        "parent": _state_to_list(event.parent),
        "depth": event.depth,
        "cost": event.cost,
        "frontier_size": event.frontier_size,
        "iteration": event.iteration,
        "metadata": _jsonable(event.metadata),
    }


def _hint_to_dict(
    hint: HintEvent,
    *,
    player_run: PlayerRun,
    index: int,
    search_run: Optional[SearchRun] = None,
) -> dict[str, Any]:
    payload = {
        "hint_id": f"{player_run.run_id}:hint:{index}",
        "player_run_id": player_run.run_id,
        "environment_id": player_run.environment_id,
        "algorithm": hint.algorithm,
        "hint_level": hint.level,
        "level": hint.level,
        "state_when_requested": _state_to_list(hint.requested_state),
        "requested_state": _state_to_list(hint.requested_state),
        "timestamp": hint.timestamp.isoformat(),
        "points_spent": hint.cost,
        "cost": hint.cost,
        "available": hint.available,
        "suggested_action": hint.suggested_action.value if hint.suggested_action else None,
        "suggested_state": _state_to_list(hint.suggested_state),
        "partial_path": [_state_to_list(state) for state in hint.route] if hint.route else None,
        "route": [_state_to_list(state) for state in hint.route] if hint.route else None,
        "reason": hint.reason,
    }
    if search_run is not None:
        payload["search_run_id"] = search_run.run_id
    return payload


def _algorithm_summary_to_dict(algorithm: SearchAlgorithm) -> dict[str, Any]:
    docs = get_algorithm_documentation(algorithm)
    return {
        "algorithm": algorithm.value,
        "name": docs.name,
        "category": _ALGORITHM_CATEGORIES[algorithm],
        "available": True,
        "description": docs.description,
    }


def _algorithm_documentation_to_dict(algorithm: SearchAlgorithm) -> dict[str, Any]:
    docs = ALGORITHM_DOCUMENTATION[algorithm]
    return {
        "algorithm": algorithm.value,
        "name": docs.name,
        "category": _ALGORITHM_CATEGORIES[algorithm],
        "description": docs.description,
        "core_idea": docs.core_idea,
        "state_representation": docs.state_representation,
        "pseudocode": list(docs.pseudocode),
        "step_by_step": list(docs.step_by_step),
        "data_structure": docs.data_structure,
        "completeness": docs.completeness,
        "optimality": docs.optimality,
        "time_complexity": docs.time_complexity,
        "space_complexity": docs.space_complexity,
        "heuristic_requirements": _heuristic_requirements(algorithm),
        "weighted_cost_requirements": _weighted_cost_requirements(algorithm),
        "mingle_specific_notes": docs.implementation_notes,
        "implementation_notes": docs.implementation_notes,
        "available": True,
    }


def _heuristic_requirements(algorithm: SearchAlgorithm) -> str:
    if algorithm == SearchAlgorithm.ASTAR:
        return "Uses a heuristic; optimality depends on admissible and consistent estimates."
    if algorithm == SearchAlgorithm.GREEDY_BEST_FIRST:
        return "Uses a heuristic to prioritize apparent closeness to the goal."
    return "No heuristic required."


def _weighted_cost_requirements(algorithm: SearchAlgorithm) -> str:
    if algorithm in {SearchAlgorithm.UCS, SearchAlgorithm.ASTAR}:
        return "Supports positive weighted terrain costs."
    return "Does not require weighted terrain; behavior may not be cost-optimal on weighted grids."


def _comparison_to_dict(comparison: Any, player_run: PlayerRun, search_run: SearchRun) -> dict[str, Any]:
    return {
        "environment_id": comparison.environment_id,
        "same_environment": comparison.same_environment,
        "player_run_id": player_run.run_id,
        "search_run_id": search_run.run_id,
        "player_completed": comparison.player_completed,
        "search_found_path": comparison.search_found_path,
        "player_metrics": _dataclass_to_dict(comparison.player_metrics),
        "search_metrics": _dataclass_to_dict(comparison.search_stats),
        "search_stats": _dataclass_to_dict(comparison.search_stats),
        "path_length_delta": comparison.path_length_delta,
        "path_cost_delta": comparison.path_cost_delta,
    }


def _insight_to_dict(insight: StateSearchInsight) -> dict[str, Any]:
    return {
        "state": _state_to_list(insight.state),
        "discovered": insight.discovered,
        "expanded": insight.expanded,
        "closed": insight.closed,
        "discovered_step": insight.discovered_step,
        "expanded_step": insight.expanded_step,
        "closed_step": insight.closed_step,
        "parent": _state_to_list(insight.parent),
        "depth": insight.depth,
        "cost": insight.cost,
        "metadata": _jsonable(insight.metadata),
    }


def _dataclass_to_dict(value: Any) -> dict[str, Any]:
    return _jsonable(asdict(value))


def _state_to_list(state: Optional[State]) -> Optional[list[int]]:
    if state is None:
        return None
    return [state[0], state[1]]


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(_jsonable(key)): _jsonable(item) for key, item in value.items()}
    if is_dataclass(value):
        return _jsonable(asdict(value))
    return value
