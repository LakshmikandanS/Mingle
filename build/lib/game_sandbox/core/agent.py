"""Minimal agent contract."""

from __future__ import annotations

from typing import Optional, Protocol

from game_sandbox.core.game import Action, Game


class Agent(Protocol):
    """An agent chooses an action from the current game state."""

    def choose_action(self, game: Game) -> Optional[Action]:
        """Choose the next action, or None if no action is available."""

