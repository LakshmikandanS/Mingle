"""Tic-Tac-Toe game implementation."""

from __future__ import annotations

from game_sandbox.games.tic_tac_toe.rules import Board, TicTacToeAction, determine_status
from game_sandbox.games.tic_tac_toe.rules import get_legal_actions as legal_actions_for_board
from game_sandbox.games.tic_tac_toe.state import CellState, currentPlayer, status


class TicTacToeGame:
    """Mutable Tic-Tac-Toe game state and rule engine."""

    def __init__(self) -> None:
        self.board: Board = [[CellState.EMPTY for _ in range(3)] for _ in range(3)]
        self.current_player = currentPlayer.PLAYER_X
        self.status = status.IN_PROGRESS

    def get_current_player(self) -> currentPlayer:
        return self.current_player

    def get_status(self) -> status:
        return self.status

    def update_status(self) -> None:
        self.status = determine_status(self.board)

    def get_legal_actions(self) -> list[TicTacToeAction]:
        return legal_actions_for_board(self.board)

    def apply_action(self, action: TicTacToeAction) -> None:
        if self.status != status.IN_PROGRESS:
            raise Exception("Game is already over.")
        if action not in self.get_legal_actions():
            raise Exception("Invalid action.")
        i, j = action
        self.board[i][j] = self.current_player.value
        self.update_status()
        self.current_player = (
            currentPlayer.PLAYER_O
            if self.current_player == currentPlayer.PLAYER_X
            else currentPlayer.PLAYER_X
        )

    def is_game_over(self) -> bool:
        return self.status != status.IN_PROGRESS


def print_board(board: Board) -> None:
    for row in board:
        print(" | ".join(cell.value for cell in row))
        print("-" * 5)


rule_engine = TicTacToeGame

