"""Reusable matchup runner."""

from __future__ import annotations

import inspect
import time
from copy import copy
from typing import Callable, Optional

from game_sandbox.core.game import Action, Game
from game_sandbox.observability.metrics import DecisionMetrics, MatchMetrics

PlayerAssignment = tuple[object, object, str]


def _player_name(player: object) -> str:
    return getattr(player, "name", str(player))


def _agent_action(agent: object, game: Game, decision_metrics: DecisionMetrics) -> Optional[Action]:
    if hasattr(agent, "choose_action"):
        action = agent.choose_action(game)
        search_metrics = getattr(agent, "last_search_metrics", None)
        if search_metrics is not None:
            decision_metrics.search_metrics = copy(search_metrics)
        return action

    if not callable(agent):
        raise TypeError("Agent must be callable or implement choose_action(game).")

    signature = inspect.signature(agent)
    positional = [
        parameter
        for parameter in signature.parameters.values()
        if parameter.kind
        in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
    ]
    if len(positional) >= 2:
        return agent(game, decision_metrics)
    return agent(game)


def _resolve_agent(
    current_player: object,
    player_assignments: list[PlayerAssignment],
    agent_o: object,
    agent_o_name: str,
) -> tuple[object, str]:
    for player, agent, agent_name in player_assignments:
        if current_player == player:
            return agent, agent_name

    if len(player_assignments) == 1:
        player_assignments.append((current_player, agent_o, agent_o_name))
        return agent_o, agent_o_name

    raise ValueError(f"No agent is assigned for player {_player_name(current_player)}.")


def matchup(
    game: Game,
    agent_x: Callable[..., Optional[Action]] | object,
    agent_o: Callable[..., Optional[Action]] | object,
    agent_x_name: str = "Agent 1",
    agent_o_name: str = "Agent 2",
) -> MatchMetrics:
    match_metrics = MatchMetrics(
        player_x_agent=agent_x_name,
        player_o_agent=agent_o_name,
        winner=game.get_status(),
    )

    player_assignments: list[PlayerAssignment] = [
        (game.get_current_player(), agent_x, agent_x_name)
    ]

    match_start = time.perf_counter()
    while not game.is_game_over():
        current_player = game.get_current_player()
        agent, agent_name = _resolve_agent(
            current_player,
            player_assignments,
            agent_o,
            agent_o_name,
        )

        decision_metrics = DecisionMetrics(
            player=_player_name(current_player),
            agent=agent_name,
        )

        decision_start = time.perf_counter()
        action = _agent_action(agent, game, decision_metrics)
        decision_end = time.perf_counter()

        decision_metrics.duration_ms = (decision_end - decision_start) * 1000
        decision_metrics.chosen_action = action
        match_metrics.decisions.append(decision_metrics)

        if action is not None:
            game.apply_action(action)
            match_metrics.no_of_moves += 1
        else:
            break

    match_end = time.perf_counter()
    match_metrics.duration_ms = (match_end - match_start) * 1000
    match_metrics.winner = game.get_status()
    return match_metrics
