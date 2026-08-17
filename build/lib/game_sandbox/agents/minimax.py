"""Minimax search for deterministic two-player zero-sum games.

The default terminal evaluator preserves the Tic-Tac-Toe notebook behavior:
X win = 1, O win = -1, draw = 0.
"""

from __future__ import annotations

import copy
from typing import Callable, Optional

from game_sandbox.core.game import Action, Game
from game_sandbox.games.tic_tac_toe.state import status
from game_sandbox.observability.metrics import SearchMetrics

TerminalEvaluator = Callable[[Game], int]


def evaluate_tic_tac_toe_terminal(engine: Game) -> int:
    if engine.get_status() == status.PLAYER_X_WINS:
        return 1
    if engine.get_status() == status.PLAYER_O_WINS:
        return -1
    return 0


def minimax_search(
    engine: Game,
    maximizing_player: bool,
    search_metrics: SearchMetrics,
    depth: int = 0,
    terminal_evaluator: TerminalEvaluator = evaluate_tic_tac_toe_terminal,
) -> int:
    search_metrics.nodes_explored += 1
    search_metrics.max_depth = max(search_metrics.max_depth, depth)

    if engine.is_game_over():
        search_metrics.terminal_nodes += 1
        return terminal_evaluator(engine)

    if maximizing_player:
        max_eval = float("-inf")
        for action in engine.get_legal_actions():
            search_metrics.branches_considered += 1
            new_engine = copy.deepcopy(engine)
            search_metrics.deep_copies += 1
            new_engine.apply_action(action)
            eval_score = minimax_search(
                new_engine,
                False,
                search_metrics,
                depth + 1,
                terminal_evaluator,
            )
            max_eval = max(max_eval, eval_score)
        return int(max_eval)

    min_eval = float("inf")
    for action in engine.get_legal_actions():
        search_metrics.branches_considered += 1
        new_engine = copy.deepcopy(engine)
        search_metrics.deep_copies += 1
        new_engine.apply_action(action)
        eval_score = minimax_search(
            new_engine,
            True,
            search_metrics,
            depth + 1,
            terminal_evaluator,
        )
        min_eval = min(min_eval, eval_score)
    return int(min_eval)


def minmax_agent(
    engine: Game,
    maximizing_player: bool,
    search_metrics: Optional[SearchMetrics] = None,
    terminal_evaluator: TerminalEvaluator = evaluate_tic_tac_toe_terminal,
) -> Optional[Action]:
    if search_metrics is None:
        search_metrics = SearchMetrics()

    best_action = None
    if maximizing_player:
        best_eval = float("-inf")
        for action in engine.get_legal_actions():
            search_metrics.branches_considered += 1
            new_engine = copy.deepcopy(engine)
            search_metrics.deep_copies += 1
            new_engine.apply_action(action)
            eval_score = minimax_search(
                new_engine,
                False,
                search_metrics,
                depth=1,
                terminal_evaluator=terminal_evaluator,
            )
            if eval_score > best_eval:
                best_eval = eval_score
                best_action = action
    else:
        best_eval = float("inf")
        for action in engine.get_legal_actions():
            search_metrics.branches_considered += 1
            new_engine = copy.deepcopy(engine)
            search_metrics.deep_copies += 1
            new_engine.apply_action(action)
            eval_score = minimax_search(
                new_engine,
                True,
                search_metrics,
                depth=1,
                terminal_evaluator=terminal_evaluator,
            )
            if eval_score < best_eval:
                best_eval = eval_score
                best_action = action
    return best_action


class MinimaxAgent:
    def __init__(
        self,
        maximizing_player: bool,
        terminal_evaluator: TerminalEvaluator = evaluate_tic_tac_toe_terminal,
    ) -> None:
        self.maximizing_player = maximizing_player
        self.terminal_evaluator = terminal_evaluator
        self.last_search_metrics = SearchMetrics()

    def choose_action(self, game: Game) -> Optional[Action]:
        self.last_search_metrics = SearchMetrics()
        return minmax_agent(
            game,
            self.maximizing_player,
            self.last_search_metrics,
            self.terminal_evaluator,
        )

    def __call__(self, game: Game) -> Optional[Action]:
        return self.choose_action(game)


def minimax_wrapper(engine: Game, decision_metrics: object, maximizing_player: bool) -> Optional[Action]:
    return minmax_agent(engine, maximizing_player, decision_metrics.search_metrics)


def minimax_x_wrapper(engine: Game, decision_metrics: object) -> Optional[Action]:
    return minmax_agent(engine, True, decision_metrics.search_metrics)


def minimax_o_wrapper(engine: Game, decision_metrics: object) -> Optional[Action]:
    return minmax_agent(engine, False, decision_metrics.search_metrics)

