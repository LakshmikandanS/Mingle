import unittest

from fastapi.testclient import TestClient

from game_sandbox.agents.registry import create_agent
from game_sandbox.api.app import app
from game_sandbox.api import games as games_api
from game_sandbox.games.registry import create_game
from game_sandbox.observability.history import GameHistory
from game_sandbox.session.game_session import GameSession, PlayerConfig


class ApiTests(unittest.TestCase):
    def setUp(self):
        games_api._sessions.clear()
        self.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_home_describes_available_backend_surfaces(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["name"], "Mingle API")
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["endpoints"]["health"], "/health")
        self.assertEqual(body["endpoints"]["tic_tac_toe"], "/games")
        self.assertEqual(body["endpoints"]["maze_runner"], "/maze")

    def test_create_get_action_replay_and_decision_endpoints(self):
        create_response = self.client.post(
            "/games",
            json={"game": "tic_tac_toe", "players": {"X": "human", "O": "alphabeta"}},
        )
        self.assertEqual(create_response.status_code, 200)
        session_id = create_response.json()["session_id"]

        get_response = self.client.get(f"/games/{session_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["current_player"], "X")

        action_response = self.client.post(f"/games/{session_id}/actions", json={"action": [0, 0]})
        self.assertEqual(action_response.status_code, 200)
        self.assertEqual(action_response.json()["current_player"], "X")

        replay_response = self.client.get(f"/games/{session_id}/replay")
        self.assertEqual(replay_response.status_code, 200)
        replay = replay_response.json()
        self.assertEqual(len(replay["moves"]), 2)
        agent_move = replay["moves"][1]
        self.assertIsNotNone(agent_move["decision_id"])

        decision_response = self.client.get(
            f"/games/{session_id}/decisions/{agent_move['decision_id']}"
        )
        self.assertEqual(decision_response.status_code, 200)
        decision = decision_response.json()
        self.assertEqual(decision["chosen_action"], agent_move["action"])
        self.assertEqual(decision["agent"], "alphabeta")
        self.assertIn("nodes_explored", decision["metrics"])

    def test_invalid_action_shape_and_values_return_errors(self):
        session_id = self._create_human_human_session()

        malformed_shape = self.client.post(f"/games/{session_id}/actions", json={"action": [0]})
        invalid_value = self.client.post(f"/games/{session_id}/actions", json={"action": [9, 9]})
        malformed_body = self.client.post(f"/games/{session_id}/actions", json={"move": [0, 0]})

        self.assertEqual(malformed_shape.status_code, 400)
        self.assertEqual(invalid_value.status_code, 400)
        self.assertEqual(malformed_body.status_code, 422)

    def test_invalid_tic_tac_toe_move_returns_error(self):
        session_id = self._create_human_human_session()

        first = self.client.post(f"/games/{session_id}/actions", json={"action": [0, 0]})
        duplicate = self.client.post(f"/games/{session_id}/actions", json={"action": [0, 0]})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn("detail", duplicate.json())

    def test_action_after_game_over_returns_error(self):
        session_id = self._create_human_human_session()
        for action in [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2]]:
            response = self.client.post(f"/games/{session_id}/actions", json={"action": action})
            self.assertEqual(response.status_code, 200)

        response = self.client.post(f"/games/{session_id}/actions", json={"action": [2, 2]})

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_action_when_not_human_turn_returns_error(self):
        game = create_game("tic_tac_toe")
        x_player = game.get_current_player()
        agent = create_agent("alphabeta", maximizing_player=True)
        session = GameSession(
            session_id="agent-turn",
            game_name="tic_tac_toe",
            game=game,
            players={
                x_player: PlayerConfig(
                    player=x_player,
                    agent_name="alphabeta",
                    agent=agent,
                )
            },
            history=GameHistory(initial_state=game.get_state()),
        )
        games_api._sessions[session.session_id] = session

        response = self.client.post("/games/agent-turn/actions", json={"action": [0, 0]})

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_not_found_and_invalid_configuration_errors(self):
        self.assertEqual(self.client.get("/games/missing").status_code, 404)
        self.assertEqual(self.client.get("/games/missing/replay").status_code, 404)
        self.assertEqual(
            self.client.get("/games/missing/decisions/decision-id").status_code,
            404,
        )

        invalid_game = self.client.post(
            "/games",
            json={"game": "chess", "players": {"X": "human", "O": "alphabeta"}},
        )
        invalid_agent = self.client.post(
            "/games",
            json={"game": "tic_tac_toe", "players": {"X": "human", "O": "mystery"}},
        )

        self.assertEqual(invalid_game.status_code, 400)
        self.assertEqual(invalid_agent.status_code, 400)

    def test_nonexistent_decision_for_existing_session_returns_404(self):
        session_id = self._create_human_human_session()

        response = self.client.get(f"/games/{session_id}/decisions/missing")

        self.assertEqual(response.status_code, 404)

    def test_multiple_sessions_are_independent(self):
        session_a = self._create_human_human_session()
        session_b = self._create_human_human_session()

        self.client.post(f"/games/{session_a}/actions", json={"action": [0, 0]})
        self.client.post(f"/games/{session_b}/actions", json={"action": [1, 1]})

        replay_a = self.client.get(f"/games/{session_a}/replay").json()
        replay_b = self.client.get(f"/games/{session_b}/replay").json()

        self.assertEqual(replay_a["moves"][0]["action"], [0, 0])
        self.assertEqual(replay_b["moves"][0]["action"], [1, 1])
        self.assertEqual(replay_a["moves"][0]["resulting_state"]["board"][0][0], "X")
        self.assertEqual(replay_b["moves"][0]["resulting_state"]["board"][1][1], "X")

    def test_complete_mingle_flow(self):
        create_response = self.client.post(
            "/games",
            json={"game": "tic_tac_toe", "players": {"X": "human", "O": "alphabeta"}},
        )
        session_id = create_response.json()["session_id"]
        self.assertEqual(self.client.get(f"/games/{session_id}").json()["current_player"], "X")

        while self.client.get(f"/games/{session_id}").json()["status"] == "IN_PROGRESS":
            current = self.client.get(f"/games/{session_id}").json()
            action = current["legal_actions"][0]
            response = self.client.post(f"/games/{session_id}/actions", json={"action": action})
            self.assertEqual(response.status_code, 200)

        final_state = self.client.get(f"/games/{session_id}").json()
        replay = self.client.get(f"/games/{session_id}/replay").json()
        agent_moves = [move for move in replay["moves"] if move["decision_id"] is not None]
        decision = self.client.get(
            f"/games/{session_id}/decisions/{agent_moves[0]['decision_id']}"
        ).json()

        self.assertNotEqual(final_state["status"], "IN_PROGRESS")
        self.assertEqual(replay["final_state"], final_state["state"])
        self.assertEqual(decision["chosen_action"], agent_moves[0]["action"])

    def _create_human_human_session(self):
        response = self.client.post(
            "/games",
            json={"game": "tic_tac_toe", "players": {"X": "human", "O": "human"}},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["session_id"]


if __name__ == "__main__":
    unittest.main()
