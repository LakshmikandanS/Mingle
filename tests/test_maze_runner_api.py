import unittest

from fastapi.testclient import TestClient

from game_sandbox.api.app import app
from game_sandbox.api import maze_runner as maze_api


class MazeRunnerApiTests(unittest.TestCase):
    def setUp(self):
        maze_api._environments.clear()
        maze_api._player_runs.clear()
        maze_api._search_runs.clear()
        self.client = TestClient(app)

    def test_environment_creation_retrieval_and_invalid_configuration(self):
        environment = self._create_environment()

        self.assertEqual(environment["height"], 3)
        self.assertEqual(environment["width"], 3)
        self.assertEqual(environment["start"], [0, 0])
        self.assertEqual(environment["goal"], [2, 2])
        self.assertEqual(environment["cells"][1][1]["kind"], "obstacle")

        retrieved = self.client.get(f"/maze/environments/{environment['environment_id']}")
        self.assertEqual(retrieved.status_code, 200)
        self.assertEqual(retrieved.json()["environment_id"], environment["environment_id"])

        invalid = self.client.post(
            "/maze/environments",
            json={
                "height": 1,
                "width": 2,
                "start": [0, 0],
                "goal": [0, 1],
                "obstacles": [[0, 0]],
            },
        )
        self.assertEqual(invalid.status_code, 400)

    def test_player_run_valid_invalid_obstacle_completion_and_lifecycle_errors(self):
        environment = self._create_environment()
        player = self._create_player_run(environment["environment_id"])

        invalid_boundary = self.client.post(
            f"/maze/runs/player/{player['player_run_id']}/action",
            json={"action": "LEFT"},
        )
        self.assertEqual(invalid_boundary.status_code, 200)
        self.assertFalse(invalid_boundary.json()["valid"])
        self.assertEqual(invalid_boundary.json()["current_state"], [0, 0])

        self.client.post(f"/maze/runs/player/{player['player_run_id']}/action", json={"action": "DOWN"})
        blocked = self.client.post(
            f"/maze/runs/player/{player['player_run_id']}/action",
            json={"action": "RIGHT"},
        )
        self.assertEqual(blocked.status_code, 200)
        self.assertFalse(blocked.json()["valid"])
        self.assertEqual(blocked.json()["reason"], "Destination is blocked.")

        finishing_actions = ["DOWN", "RIGHT", "RIGHT"]
        for action in finishing_actions:
            response = self.client.post(
                f"/maze/runs/player/{player['player_run_id']}/action",
                json={"action": action},
            )
            self.assertEqual(response.status_code, 200)

        final_state = self.client.get(f"/maze/runs/player/{player['player_run_id']}").json()
        self.assertEqual(final_state["status"], "COMPLETED")
        self.assertEqual(final_state["current_state"], [2, 2])
        self.assertEqual(final_state["metrics"]["invalid_actions"], 2)

        rejected = self.client.post(
            f"/maze/runs/player/{player['player_run_id']}/action",
            json={"action": "UP"},
        )
        self.assertEqual(rejected.status_code, 400)

        history = self.client.get(f"/maze/runs/player/{player['player_run_id']}/history")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.json()["actions"]), 6)
        self.assertEqual(history.json()["trajectory"][-1], [2, 2])

    def test_player_run_can_be_abandoned_without_deleting_history(self):
        environment = self._create_environment()
        player = self._create_player_run(environment["environment_id"])

        self.client.post(f"/maze/runs/player/{player['player_run_id']}/action", json={"action": "RIGHT"})
        abandoned = self.client.post(f"/maze/runs/player/{player['player_run_id']}/give-up")

        self.assertEqual(abandoned.status_code, 200)
        self.assertEqual(abandoned.json()["status"], "ABANDONED")
        self.assertEqual(abandoned.json()["trajectory"], [[0, 0], [0, 1]])

        rejected = self.client.post(
            f"/maze/runs/player/{player['player_run_id']}/action",
            json={"action": "RIGHT"},
        )
        self.assertEqual(rejected.status_code, 400)

    def test_search_run_statistics_trace_replay_and_algorithm_errors(self):
        environment = self._create_environment()

        search = self.client.post(
            "/maze/runs/search",
            json={"environment_id": environment["environment_id"], "algorithm": "bfs"},
        )
        self.assertEqual(search.status_code, 200)
        search_body = search.json()
        self.assertEqual(search_body["algorithm"], "bfs")
        self.assertEqual(search_body["status"], "COMPLETED")
        self.assertEqual(search_body["search_status"], "FOUND")
        self.assertTrue(search_body["statistics"]["path_found"])
        self.assertGreater(search_body["trace_metadata"]["event_count"], 0)

        trace = self.client.get(f"/maze/runs/search/{search_body['search_run_id']}/trace")
        self.assertEqual(trace.status_code, 200)
        self.assertEqual(trace.json()["events"][0]["step"], 1)
        self.assertIn("event_type", trace.json()["events"][0])

        replay = self.client.get(
            f"/maze/runs/search/{search_body['search_run_id']}/replay",
            params={"from_index": 1, "limit": 2},
        )
        self.assertEqual(replay.status_code, 200)
        self.assertEqual(replay.json()["count"], 2)

        step = self.client.get(f"/maze/runs/search/{search_body['search_run_id']}/trace/1")
        self.assertEqual(step.status_code, 200)
        self.assertEqual(step.json()["step"], 1)

        astar = self.client.post(
            "/maze/runs/search",
            json={"environment_id": environment["environment_id"], "algorithm": "a*"},
        )
        self.assertEqual(astar.status_code, 200)
        self.assertEqual(astar.json()["algorithm"], "astar")

        planned = self.client.post(
            "/maze/runs/search",
            json={"environment_id": environment["environment_id"], "algorithm": "ida_star"},
        )
        self.assertEqual(planned.status_code, 501)

    def test_hints_have_cost_history_and_do_not_move_player(self):
        environment = self._create_environment()
        player = self._create_player_run(environment["environment_id"])
        search = self._create_search_run(environment["environment_id"], "bfs")

        hint = self.client.post(
            f"/maze/runs/player/{player['player_run_id']}/hints",
            json={"search_run_id": search["search_run_id"], "hint_level": "NEXT_ACTION"},
        )
        self.assertEqual(hint.status_code, 200)
        hint_body = hint.json()
        self.assertTrue(hint_body["available"])
        self.assertEqual(hint_body["state_when_requested"], [0, 0])
        self.assertEqual(hint_body["suggested_action"], "DOWN")
        self.assertEqual(hint_body["points_spent"], 1)

        after_hint = self.client.get(f"/maze/runs/player/{player['player_run_id']}").json()
        self.assertEqual(after_hint["current_state"], [0, 0])
        self.assertEqual(after_hint["metrics"]["hints_used"], 1)

        history = self.client.get(f"/maze/runs/player/{player['player_run_id']}/hints")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.json()["hints"]), 1)

        costs = self.client.get("/maze/hints/costs")
        self.assertEqual(costs.status_code, 200)
        self.assertEqual(costs.json()["costs"]["bfs"]["NEXT_ACTION"], 1)

        invalid = self.client.post(
            f"/maze/runs/player/{player['player_run_id']}/hints",
            json={"search_run_id": search["search_run_id"], "hint_level": "MYSTERY"},
        )
        self.assertEqual(invalid.status_code, 400)

    def test_algorithm_documentation_is_structured_and_discoverable(self):
        listing = self.client.get("/maze/algorithms")
        self.assertEqual(listing.status_code, 200)
        self.assertIn("available", listing.json())
        self.assertIn("planned", listing.json())
        self.assertIn("bfs", [item["algorithm"] for item in listing.json()["available"]])

        docs = self.client.get("/maze/algorithms/astar")
        self.assertEqual(docs.status_code, 200)
        docs_body = docs.json()
        self.assertEqual(docs_body["algorithm"], "astar")
        self.assertTrue(docs_body["pseudocode"])
        self.assertIn("heuristic_requirements", docs_body)
        self.assertIn("mingle_specific_notes", docs_body)

        unknown = self.client.get("/maze/algorithms/not_real")
        self.assertEqual(unknown.status_code, 400)

    def test_comparison_same_environment_and_intermediate_lookup(self):
        environment = self._create_environment()
        player = self._create_player_run(environment["environment_id"])
        self.client.post(f"/maze/runs/player/{player['player_run_id']}/action", json={"action": "RIGHT"})
        search = self._create_search_run(environment["environment_id"], "bfs")

        comparison = self.client.post(
            "/maze/comparisons",
            json={
                "player_run_id": player["player_run_id"],
                "search_run_id": search["search_run_id"],
            },
        )
        self.assertEqual(comparison.status_code, 200)
        self.assertTrue(comparison.json()["same_environment"])
        self.assertIn("player_metrics", comparison.json())
        self.assertIn("search_metrics", comparison.json())

        insight = self.client.post(
            "/maze/comparisons/intermediate",
            json={
                "player_run_id": player["player_run_id"],
                "search_run_id": search["search_run_id"],
            },
        )
        self.assertEqual(insight.status_code, 200)
        self.assertEqual(insight.json()["player_state"], [0, 1])
        self.assertTrue(insight.json()["insight"]["discovered"])

        other_environment = self.client.post("/maze/environments", json={"rows": ["SG"]}).json()
        other_search = self._create_search_run(other_environment["environment_id"], "bfs")
        mismatch = self.client.post(
            "/maze/comparisons",
            json={
                "player_run_id": player["player_run_id"],
                "search_run_id": other_search["search_run_id"],
            },
        )
        self.assertEqual(mismatch.status_code, 400)

    def _create_environment(self):
        response = self.client.post(
            "/maze/environments",
            json={"rows": ["S..", ".#.", "..G"]},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()

    def _create_player_run(self, environment_id):
        response = self.client.post(
            "/maze/runs/player",
            json={"environment_id": environment_id},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()

    def _create_search_run(self, environment_id, algorithm):
        response = self.client.post(
            "/maze/runs/search",
            json={"environment_id": environment_id, "algorithm": algorithm},
        )
        self.assertEqual(response.status_code, 200)
        return response.json()


if __name__ == "__main__":
    unittest.main()
