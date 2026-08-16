import unittest

from game_sandbox.games.tic_tac_toe import CellState, TicTacToeGame, currentPlayer, status


class TicTacToeGameTests(unittest.TestCase):
    def test_new_game_starts_empty_with_x_to_move(self):
        game = TicTacToeGame()

        self.assertEqual(game.get_current_player(), currentPlayer.PLAYER_X)
        self.assertEqual(game.get_status(), status.IN_PROGRESS)
        self.assertFalse(game.is_game_over())
        self.assertEqual(len(game.get_legal_actions()), 9)
        self.assertEqual(
            game.get_state(),
            {"board": [["", "", ""], ["", "", ""], ["", "", ""]]},
        )

    def test_valid_action_changes_board_and_alternates_player(self):
        game = TicTacToeGame()

        game.apply_action((1, 1))

        self.assertEqual(game.board[1][1], CellState.X)
        self.assertEqual(game.get_current_player(), currentPlayer.PLAYER_O)
        self.assertNotIn((1, 1), game.get_legal_actions())
        self.assertEqual(game.get_state()["board"][1][1], "X")

    def test_invalid_actions_are_rejected(self):
        game = TicTacToeGame()
        game.apply_action((0, 0))

        with self.assertRaises(Exception):
            game.apply_action((0, 0))
        with self.assertRaises(Exception):
            game.apply_action((3, 3))

    def test_x_win_and_game_over_are_detected(self):
        game = TicTacToeGame()
        for action in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
            game.apply_action(action)

        self.assertEqual(game.get_status(), status.PLAYER_X_WINS)
        self.assertTrue(game.is_game_over())
        with self.assertRaises(Exception):
            game.apply_action((2, 2))

    def test_o_win_is_detected(self):
        game = TicTacToeGame()
        for action in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2), (1, 2)]:
            game.apply_action(action)

        self.assertEqual(game.get_status(), status.PLAYER_O_WINS)
        self.assertTrue(game.is_game_over())

    def test_draw_is_detected(self):
        game = TicTacToeGame()
        for action in [
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 1),
            (1, 0),
            (1, 2),
            (2, 1),
            (2, 0),
            (2, 2),
        ]:
            game.apply_action(action)

        self.assertEqual(game.get_status(), status.DRAW)
        self.assertTrue(game.is_game_over())


if __name__ == "__main__":
    unittest.main()
