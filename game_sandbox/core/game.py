"""Minimal generic game contract for sandbox experiments."""

from __future__ import annotations

from typing import Any, Protocol, TypeAlias

Action: TypeAlias = Any


class Game(Protocol):
    """Small interface expected by reusable agents and match runners."""

    def get_legal_actions(self) -> list[Action]:
        """Return legal actions for the current state."""

    def apply_action(self, action: Action) -> None:
        """Apply one legal action to the current state."""

    def is_game_over(self) -> bool:
        """Return whether the game has reached a terminal state."""

    def get_status(self) -> Any:
        """Return the game-specific status object."""

    def get_current_player(self) -> Any:
        """Return the game-specific current-player object."""

    def get_state(self) -> Any:
        """Return a JSON-safe representation of the current game state."""
