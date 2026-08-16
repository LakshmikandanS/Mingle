"""Random action-selection agent."""

from __future__ import annotations

import random
from typing import Optional

from game_sandbox.core.game import Action, Game


def random_agent(engine: Game) -> Optional[Action]:
    legal_actions = engine.get_legal_actions()
    if legal_actions:
        return random.choice(legal_actions)
    return None


def random_wrapper(engine: Game, decision_metrics: object) -> Optional[Action]:
    return random_agent(engine)


class RandomAgent:
    def choose_action(self, game: Game) -> Optional[Action]:
        return random_agent(game)

    def __call__(self, game: Game) -> Optional[Action]:
        return self.choose_action(game)

