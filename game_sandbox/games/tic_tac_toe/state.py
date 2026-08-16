"""Tic-Tac-Toe state enums.

The lower-case enum names are kept as compatibility aliases for the original
notebook implementation.
"""

from enum import Enum


class CellState(Enum):
    EMPTY = " "
    X = "X"
    O = "O"


class currentPlayer(Enum):
    PLAYER_X = CellState.X
    PLAYER_O = CellState.O


class status(Enum):
    IN_PROGRESS = 0
    PLAYER_X_WINS = 1
    PLAYER_O_WINS = 2
    DRAW = 3


CurrentPlayer = currentPlayer
GameStatus = status

