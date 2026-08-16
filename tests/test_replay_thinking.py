import unittest

from game_sandbox.session import create_session
from game_sandbox.session.game_session import decision_to_dict


class ReplayThinkingTests(unittest.TestCase):
    def test_replay_records_known_human_sequence(self):
        session = create_session("tic_tac_toe", {"X": "human", "O": "human"})
        actions = [[0, 0], [1, 1], [0, 1]]

        for action in actions:
            session.submit_action(action)
        replay = session.get_replay()

        self.assertEqual(replay["initial_state"], {"board": [["", "", ""], ["", "", ""], ["", "", ""]]})
        self.assertIsNone(replay["final_state"])
        self.assertEqual([move["move_number"] for move in replay["moves"]], [1, 2, 3])
        self.assertEqual([move["player"] for move in replay["moves"]], ["X", "O", "X"])
        self.assertEqual([move["action"] for move in replay["moves"]], actions)
        self.assertEqual(replay["moves"][-1]["resulting_state"]["board"][0][1], "X")

    def test_agent_move_links_replay_to_thinking_record(self):
        session = create_session("tic_tac_toe", {"X": "human", "O": "alphabeta"})

        session.submit_action([0, 0])
        agent_move = session.get_replay()["moves"][1]
        decision = decision_to_dict(session.get_decision(agent_move["decision_id"]))

        self.assertEqual(decision["decision_id"], agent_move["decision_id"])
        self.assertEqual(decision["player"], agent_move["player"])
        self.assertEqual(decision["agent"], "alphabeta")
        self.assertEqual(decision["chosen_action"], agent_move["action"])
        self.assertGreaterEqual(decision["duration_ms"], 0)
        self.assertIn("nodes_explored", decision["metrics"])
        self.assertIn("pruning_cutoffs", decision["metrics"])

    def test_final_state_matches_actual_game_when_complete(self):
        session = create_session("tic_tac_toe", {"X": "human", "O": "human"})
        for action in [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2]]:
            session.submit_action(action)

        replay = session.get_replay()

        self.assertEqual(replay["final_state"], session.game.get_state())
        self.assertEqual(replay["moves"][-1]["resulting_state"], session.game.get_state())


if __name__ == "__main__":
    unittest.main()
