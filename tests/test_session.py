import unittest

from game_sandbox.games.tic_tac_toe import status
from game_sandbox.session import create_session


class GameSessionTests(unittest.TestCase):
    def test_session_can_be_created_with_human_and_agent_players(self):
        session = create_session("tic_tac_toe", {"X": "human", "O": "alphabeta"})
        state = session.state()

        self.assertEqual(state["game"], "tic_tac_toe")
        self.assertEqual(state["current_player"], "X")
        self.assertEqual(state["status"], "IN_PROGRESS")
        self.assertEqual(len(state["legal_actions"]), 9)

    def test_human_action_is_applied_and_agent_response_is_recorded(self):
        session = create_session("tic_tac_toe", {"X": "human", "O": "alphabeta"})

        state = session.submit_action([0, 0])
        replay = session.get_replay()

        self.assertEqual(state["current_player"], "X")
        self.assertEqual(len(replay["moves"]), 2)
        self.assertEqual(replay["moves"][0]["player"], "X")
        self.assertEqual(replay["moves"][0]["action"], [0, 0])
        self.assertEqual(replay["moves"][1]["player"], "O")
        self.assertIsNotNone(replay["moves"][1]["decision_id"])
        self.assertIn(replay["moves"][1]["decision_id"], session.decisions)

    def test_agent_vs_agent_session_runs_to_game_over(self):
        session = create_session("tic_tac_toe", {"X": "minimax", "O": "alphabeta"})

        self.assertEqual(session.state()["status"], "DRAW")
        self.assertEqual(len(session.get_replay()["moves"]), 9)
        self.assertEqual(len(session.decisions), 9)

    def test_game_over_stops_further_human_play(self):
        session = create_session("tic_tac_toe", {"X": "human", "O": "human"})
        for action in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
            session.submit_action(action)

        self.assertEqual(session.game.get_status(), status.PLAYER_X_WINS)
        with self.assertRaises(ValueError):
            session.submit_action([2, 2])


if __name__ == "__main__":
    unittest.main()
