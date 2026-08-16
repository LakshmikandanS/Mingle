import unittest
from unittest.mock import patch

from game_sandbox.agents.alphabeta import AlphaBetaAgent
from game_sandbox.agents.human import human_agent
from game_sandbox.agents.minimax import MinimaxAgent
from game_sandbox.agents.random_agent import RandomAgent
from game_sandbox.games.tic_tac_toe import TicTacToeGame


def game_after(actions):
    game = TicTacToeGame()
    for action in actions:
        game.apply_action(action)
    return game


class AgentTests(unittest.TestCase):
    def test_random_agent_returns_legal_action(self):
        game = TicTacToeGame()
        action = RandomAgent().choose_action(game)

        self.assertIn(action, game.get_legal_actions())

    def test_human_agent_uses_input_action(self):
        game = TicTacToeGame()

        with patch("builtins.input", side_effect=["not,a,move", "1,1"]):
            action = human_agent(game)

        self.assertEqual(action, (1, 1))

    def test_minimax_takes_immediate_x_win(self):
        game = game_after([(0, 0), (1, 0), (0, 1), (1, 1)])

        action = MinimaxAgent(maximizing_player=True).choose_action(game)

        self.assertEqual(action, (0, 2))

    def test_alphabeta_takes_immediate_x_win_and_records_metrics(self):
        game = game_after([(0, 0), (1, 0), (0, 1), (1, 1)])
        agent = AlphaBetaAgent(maximizing_player=True)

        action = agent.choose_action(game)

        self.assertEqual(action, (0, 2))
        self.assertGreater(agent.last_search_metrics.nodes_explored, 0)
        self.assertGreater(agent.last_search_metrics.branches_considered, 0)
        self.assertGreaterEqual(agent.last_search_metrics.pruning_cutoffs, 0)

    def test_alphabeta_takes_immediate_o_win(self):
        game = game_after([(0, 0), (1, 0), (0, 1), (1, 1), (2, 2)])

        action = AlphaBetaAgent(maximizing_player=False).choose_action(game)

        self.assertEqual(action, (1, 2))


if __name__ == "__main__":
    unittest.main()
