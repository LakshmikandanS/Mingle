"""Run a Tic-Tac-Toe matchup demo from the refactored package."""

from game_sandbox.agents import minimax_x_wrapper, random_wrapper
from game_sandbox.games.tic_tac_toe import rule_engine
from game_sandbox.observability import print_match_metrics
from game_sandbox.runner import matchup


def main() -> None:
    metrics = matchup(
        rule_engine(),
        minimax_x_wrapper,
        random_wrapper,
        "Minimax",
        "Random",
    )
    print_match_metrics(metrics)


if __name__ == "__main__":
    main()

