"""Pure Tic-Tac-Toe rule helpers."""

from __future__ import annotations

from game_sandbox.games.tic_tac_toe.state import CellState, status

Board = list[list[CellState]]
TicTacToeAction = tuple[int, int]


def determine_status(board: Board) -> status:
    """Return the current Tic-Tac-Toe status for a board."""

    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != CellState.EMPTY:
            return status.PLAYER_X_WINS if board[i][0] == CellState.X else status.PLAYER_O_WINS
        if board[0][i] == board[1][i] == board[2][i] != CellState.EMPTY:
            return status.PLAYER_X_WINS if board[0][i] == CellState.X else status.PLAYER_O_WINS

    if board[0][0] == board[1][1] == board[2][2] != CellState.EMPTY:
        return status.PLAYER_X_WINS if board[0][0] == CellState.X else status.PLAYER_O_WINS
    if board[0][2] == board[1][1] == board[2][0] != CellState.EMPTY:
        return status.PLAYER_X_WINS if board[0][2] == CellState.X else status.PLAYER_O_WINS

    if all(cell != CellState.EMPTY for row in board for cell in row):
        return status.DRAW

    return status.IN_PROGRESS


def get_legal_actions(board: Board) -> list[TicTacToeAction]:
    legal_actions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == CellState.EMPTY:
                legal_actions.append((i, j))
    return legal_actions

