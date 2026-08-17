"""Alpha-Beta pruning search.

The default terminal evaluator preserves the Tic-Tac-Toe notebook behavior:
X win = 1, O win = -1, draw = 0.
"""

from __future__ import annotations

import copy
from typing import Optional

from game_sandbox.agents.minimax import TerminalEvaluator, evaluate_tic_tac_toe_terminal
from game_sandbox.core.game import Action, Game
from game_sandbox.observability.metrics import SearchMetrics


def alphabeta_search(
    engine: Game,
    maximizing_player: bool,
    search_metrics: SearchMetrics,
    alpha: float,
    beta: float,
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
            eval_score = alphabeta_search(
                new_engine,
                False,
                search_metrics,
                alpha,
                beta,
                depth + 1,
                terminal_evaluator,
            )
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                search_metrics.pruning_cutoffs += 1
                break
        return int(max_eval)

    min_eval = float("inf")
    for action in engine.get_legal_actions():
        search_metrics.branches_considered += 1
        new_engine = copy.deepcopy(engine)
        search_metrics.deep_copies += 1
        new_engine.apply_action(action)
        eval_score = alphabeta_search(
            new_engine,
            True,
            search_metrics,
            alpha,
            beta,
            depth + 1,
            terminal_evaluator,
        )
        min_eval = min(min_eval, eval_score)
        beta = min(beta, eval_score)
        if beta <= alpha:
            search_metrics.pruning_cutoffs += 1
            break
    return int(min_eval)


def alphabeta_agent(
    engine: Game,
    maximizing_player: bool,
    search_metrics: Optional[SearchMetrics] = None,
    terminal_evaluator: TerminalEvaluator = evaluate_tic_tac_toe_terminal,
) -> Optional[Action]:
    if search_metrics is None:
        search_metrics = SearchMetrics()

    alpha = float("-inf")
    beta = float("inf")
    best_action = None
    best_is_immediate_terminal = False

    if maximizing_player:
        best_eval = float("-inf")
        for action in engine.get_legal_actions():
            search_metrics.branches_considered += 1
            new_engine = copy.deepcopy(engine)
            search_metrics.deep_copies += 1
            new_engine.apply_action(action)
            eval_score = alphabeta_search(
                new_engine,
                False,
                search_metrics,
                alpha,
                beta,
                depth=1,
                terminal_evaluator=terminal_evaluator,
            )
            is_immediate_terminal = new_engine.is_game_over()
            if eval_score > best_eval or (
                eval_score == best_eval
                and is_immediate_terminal
                and not best_is_immediate_terminal
            ):
                best_eval = eval_score
                best_action = action
                best_is_immediate_terminal = is_immediate_terminal
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                search_metrics.pruning_cutoffs += 1
                break
    else:
        best_eval = float("inf")
        for action in engine.get_legal_actions():
            search_metrics.branches_considered += 1
            new_engine = copy.deepcopy(engine)
            search_metrics.deep_copies += 1
            new_engine.apply_action(action)
            eval_score = alphabeta_search(
                new_engine,
                True,
                search_metrics,
                alpha,
                beta,
                depth=1,
                terminal_evaluator=terminal_evaluator,
            )
            is_immediate_terminal = new_engine.is_game_over()
            if eval_score < best_eval or (
                eval_score == best_eval
                and is_immediate_terminal
                and not best_is_immediate_terminal
            ):
                best_eval = eval_score
                best_action = action
                best_is_immediate_terminal = is_immediate_terminal
            beta = min(beta, eval_score)
            if beta <= alpha:
                search_metrics.pruning_cutoffs += 1
                break

    return best_action


class AlphaBetaAgent:
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
        return alphabeta_agent(
            game,
            self.maximizing_player,
            self.last_search_metrics,
            self.terminal_evaluator,
        )

    def __call__(self, game: Game) -> Optional[Action]:
        return self.choose_action(game)


def alphabeta_wrapper(engine: Game, decision_metrics: object, maximizing_player: bool) -> Optional[Action]:
    return alphabeta_agent(engine, maximizing_player, decision_metrics.search_metrics)


def alphabeta_x_wrapper(engine: Game, decision_metrics: object) -> Optional[Action]:
    return alphabeta_agent(engine, True, decision_metrics.search_metrics)


def alphabeta_o_wrapper(engine: Game, decision_metrics: object) -> Optional[Action]:
    return alphabeta_agent(engine, False, decision_metrics.search_metrics)
