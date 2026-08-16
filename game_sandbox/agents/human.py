"""Human input agent helpers."""

from __future__ import annotations

from typing import Optional

from game_sandbox.core.game import Action, Game
from game_sandbox.games.tic_tac_toe.game import print_board


def human_agent(engine: Game) -> Optional[Action]:
    legal_actions = engine.get_legal_actions()
    if not legal_actions:
        return None

    print("Legal actions:", legal_actions)
    if hasattr(engine, "board"):
        print_board(engine.board)

    while True:
        try:
            action = input("Enter your move as 'row,col': ")
            i, j = map(int, action.split(","))
            if (i, j) in legal_actions:
                return (i, j)
            print("Invalid move. Try again.")
        except Exception as exc:
            print(f"Error: {exc}. Please enter a valid move.")


class HumanAgent:
    def choose_action(self, game: Game) -> Optional[Action]:
        return human_agent(game)

    def __call__(self, game: Game) -> Optional[Action]:
        return self.choose_action(game)

