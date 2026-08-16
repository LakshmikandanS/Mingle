"""Lightweight registry for built-in game implementations."""

from __future__ import annotations

from typing import Callable

from game_sandbox.core.game import Game
from game_sandbox.games.tic_tac_toe import TicTacToeGame

GameFactory = Callable[[], Game]

GAME_REGISTRY: dict[str, GameFactory] = {
    "tic_tac_toe": TicTacToeGame,
}


def create_game(name: str) -> Game:
    try:
        return GAME_REGISTRY[name]()
    except KeyError as exc:
        known_games = ", ".join(sorted(GAME_REGISTRY))
        raise ValueError(f"Unknown game '{name}'. Known games: {known_games}.") from exc
