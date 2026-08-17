import unittest

from game_sandbox.games.maze_runner import (
    Action,
    HintLevel,
    HintProvider,
    MazeEnvironment,
    PlayerRun,
    PlayerRunStatus,
    SearchAlgorithm,
    SearchEventType,
    SearchRun,
    SearchStatus,
    a_star_search,
    breadth_first_search,
    compare_player_to_search,
    depth_first_search,
    depth_limited_search,
    greedy_best_first_search,
    get_algorithm_documentation,
    intermediate_search_insight,
    iterative_deepening_search,
    manhattan_distance,
    uniform_cost_search,
    zero_heuristic,
)


def simple_environment():
    return MazeEnvironment.from_strings(
        [
            "S..",
            ".#.",
            "..G",
        ]
    )


def weighted_environment():
    return MazeEnvironment.from_strings(
        [
            "S9G",
            "...",
        ]
    )


class MazeEnvironmentTests(unittest.TestCase):
    def test_environment_validates_dimensions_start_goal_and_obstacles(self):
        environment = simple_environment()
        validation = environment.validate(check_solvable=True)

        self.assertTrue(validation.valid)
        self.assertTrue(validation.solvable)
        self.assertEqual(environment.rows, 3)
        self.assertEqual(environment.columns, 3)
        self.assertEqual(environment.start, (0, 0))
        self.assertEqual(environment.goal, (2, 2))
        self.assertIn((1, 1), environment.obstacles)

    def test_transitions_neighbors_and_illegal_actions_use_environment_rules(self):
        environment = simple_environment()

        right = environment.transition((0, 0), Action.RIGHT)
        left = environment.transition((0, 0), Action.LEFT)
        blocked = environment.transition((1, 0), Action.RIGHT)

        self.assertTrue(right.valid)
        self.assertEqual(right.to_state, (0, 1))
        self.assertEqual(right.cost, 1)
        self.assertFalse(left.valid)
        self.assertEqual(left.to_state, (0, 0))
        self.assertFalse(blocked.valid)
        self.assertEqual(environment.get_legal_actions((0, 0)), [Action.DOWN, Action.RIGHT])
        self.assertEqual(
            [transition.to_state for transition in environment.neighbors((0, 0))],
            [(1, 0), (0, 1)],
        )

    def test_weighted_transition_cost_enters_destination_cell(self):
        environment = MazeEnvironment.from_strings(
            [
                "S2G",
            ]
        )

        self.assertEqual(environment.transition((0, 0), Action.RIGHT).cost, 2)
        self.assertEqual(environment.transition((0, 1), Action.RIGHT).cost, 1)

    def test_deterministic_random_generation_can_be_recreated(self):
        first = MazeEnvironment.random_obstacles(5, 5, seed=42, obstacle_probability=0.2)
        second = MazeEnvironment.random_obstacles(5, 5, seed=42, obstacle_probability=0.2)

        self.assertEqual(first.obstacles, second.obstacles)
        self.assertEqual(first.environment_id, second.environment_id)
        self.assertTrue(first.validate(check_solvable=True).solvable)

    def test_unsolvable_environment_validation_reports_no_solution(self):
        environment = MazeEnvironment.from_strings(
            [
                "S#G",
            ]
        )

        self.assertTrue(environment.validate().valid)
        self.assertFalse(environment.validate(check_solvable=True).solvable)


class MazeSearchTests(unittest.TestCase):
    def test_bfs_finds_shortest_equal_cost_path_with_trace_and_stats(self):
        environment = simple_environment()

        result = breadth_first_search(environment)

        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertEqual(result.path[0], environment.start)
        self.assertEqual(result.path[-1], environment.goal)
        self.assertEqual(result.stats.path_length, 5)
        self.assertEqual(result.stats.path_cost, 4)
        self.assertTrue(result.stats.path_found)
        self.assertGreater(result.stats.nodes_expanded, 0)
        self.assertGreater(result.stats.nodes_discovered, 0)
        self.assertGreaterEqual(result.stats.max_frontier_size, 1)
        self.assertEqual(result.trace.expanded_order()[:3], [(0, 0), (1, 0), (0, 1)])
        self.assertIn(
            SearchEventType.NODE_DISCOVERED,
            [event.event_type for event in result.trace.events_for_state((0, 1))],
        )

    def test_bfs_reports_no_path(self):
        environment = MazeEnvironment.from_strings(["S#G"])

        result = breadth_first_search(environment)

        self.assertEqual(result.status, SearchStatus.NOT_FOUND)
        self.assertIsNone(result.path)
        self.assertFalse(result.stats.path_found)

    def test_dfs_finds_path_with_deterministic_expansion_trace(self):
        environment = simple_environment()

        result = depth_first_search(environment)

        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertEqual(result.path[0], environment.start)
        self.assertEqual(result.path[-1], environment.goal)
        self.assertEqual(result.trace.expanded_order()[:3], [(0, 0), (1, 0), (2, 0)])

    def test_dls_distinguishes_solution_inside_and_outside_limit(self):
        environment = simple_environment()

        too_shallow = depth_limited_search(environment, depth_limit=2)
        deep_enough = depth_limited_search(environment, depth_limit=4)

        self.assertEqual(too_shallow.status, SearchStatus.CUTOFF)
        self.assertIsNone(too_shallow.path)
        self.assertTrue(too_shallow.stats.cutoff_reached)
        self.assertEqual(deep_enough.status, SearchStatus.FOUND)
        self.assertEqual(deep_enough.stats.depth_limit, 4)
        self.assertEqual(deep_enough.path[-1], environment.goal)

    def test_iddfs_records_iterations_and_cumulative_stats(self):
        environment = simple_environment()

        result = iterative_deepening_search(environment, max_depth=4)

        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertEqual(result.stats.iterations, 5)
        self.assertGreater(result.stats.total_nodes_expanded, 0)
        self.assertGreater(result.stats.total_nodes_discovered, 0)
        self.assertIn(
            SearchEventType.ITERATION_STARTED,
            [event.event_type for event in result.trace.replay()],
        )

    def test_search_run_keeps_environment_algorithm_path_stats_and_trace(self):
        environment = simple_environment()

        run = SearchRun.run(environment, SearchAlgorithm.BFS)
        again = SearchRun.run(environment, "bfs")

        self.assertEqual(run.environment_id, environment.environment_id)
        self.assertEqual(run.algorithm, SearchAlgorithm.BFS)
        self.assertEqual(run.path, again.path)
        self.assertEqual(run.trace.expanded_order(), again.trace.expanded_order())

    def test_ucs_finds_lowest_cost_path_on_weighted_terrain(self):
        environment = weighted_environment()

        bfs = breadth_first_search(environment)
        ucs = uniform_cost_search(environment)

        self.assertEqual(bfs.path, [(0, 0), (0, 1), (0, 2)])
        self.assertEqual(bfs.stats.path_cost, 10)
        self.assertEqual(ucs.status, SearchStatus.FOUND)
        self.assertEqual(ucs.path, [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2)])
        self.assertEqual(ucs.stats.path_cost, 4)
        self.assertGreater(bfs.stats.path_cost, ucs.stats.path_cost)
        self.assertIn("g", ucs.trace.insight_for_state((1, 1)).metadata)

    def test_a_star_matches_uniform_cost_with_zero_heuristic(self):
        environment = weighted_environment()

        ucs = uniform_cost_search(environment)
        astar = a_star_search(environment, heuristic=zero_heuristic)

        self.assertEqual(astar.status, SearchStatus.FOUND)
        self.assertEqual(astar.path, ucs.path)
        self.assertEqual(astar.stats.path_cost, ucs.stats.path_cost)
        self.assertEqual(astar.stats.heuristic_name, "zero_heuristic")

    def test_a_star_records_g_h_f_metadata_with_manhattan_heuristic(self):
        environment = simple_environment()

        result = a_star_search(environment)
        insight = result.trace.insight_for_state((0, 1))

        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertEqual(result.stats.heuristic_name, "manhattan_distance")
        self.assertEqual(insight.metadata["g"], 1)
        self.assertEqual(insight.metadata["h"], manhattan_distance((0, 1), environment.goal))
        self.assertEqual(insight.metadata["f"], insight.metadata["g"] + insight.metadata["h"])

    def test_greedy_best_first_uses_heuristic_metadata(self):
        environment = simple_environment()

        result = greedy_best_first_search(environment)
        first_neighbor_insight = result.trace.insight_for_state((1, 0))

        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertEqual(result.stats.heuristic_name, "manhattan_distance")
        self.assertIn("h", first_neighbor_insight.metadata)
        self.assertNotIn("f", first_neighbor_insight.metadata)

    def test_run_search_dispatches_phase_two_algorithms(self):
        environment = weighted_environment()

        self.assertEqual(SearchRun.run(environment, "ucs").algorithm, SearchAlgorithm.UCS)
        self.assertEqual(
            SearchRun.run(environment, "greedy").algorithm,
            SearchAlgorithm.GREEDY_BEST_FIRST,
        )
        self.assertEqual(SearchRun.run(environment, "a*").algorithm, SearchAlgorithm.ASTAR)


class PlayerRunAndHintTests(unittest.TestCase):
    def test_player_run_records_valid_invalid_trajectory_and_completion(self):
        environment = simple_environment()
        player = PlayerRun(environment)

        invalid = player.move(Action.LEFT)
        first = player.move(Action.RIGHT)
        player.move(Action.RIGHT)
        player.move(Action.DOWN)
        final = player.move(Action.DOWN)

        self.assertFalse(invalid.valid)
        self.assertTrue(first.valid)
        self.assertEqual(player.current_state, environment.goal)
        self.assertEqual(player.status, PlayerRunStatus.COMPLETED)
        self.assertEqual(player.trajectory, [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)])
        self.assertEqual(final.to_state, environment.goal)
        metrics = player.metrics()
        self.assertEqual(metrics.total_actions, 5)
        self.assertEqual(metrics.valid_actions, 4)
        self.assertEqual(metrics.invalid_actions, 1)
        self.assertEqual(metrics.path_length, 4)
        self.assertEqual(metrics.path_cost, 4)

        with self.assertRaises(ValueError):
            player.move(Action.UP)

    def test_player_run_can_be_abandoned_without_deleting_history(self):
        player = PlayerRun(simple_environment())
        player.move(Action.RIGHT)

        player.give_up()

        self.assertEqual(player.status, PlayerRunStatus.ABANDONED)
        self.assertEqual(player.trajectory, [(0, 0), (0, 1)])
        with self.assertRaises(ValueError):
            player.move(Action.RIGHT)

    def test_hint_provider_uses_search_run_and_does_not_move_player(self):
        environment = simple_environment()
        player = PlayerRun(environment)
        search_run = SearchRun.run(environment, SearchAlgorithm.BFS)

        hint = HintProvider().generate_hint(player, search_run, HintLevel.NEXT_ACTION)

        self.assertTrue(hint.available)
        self.assertEqual(hint.suggested_action, Action.DOWN)
        self.assertEqual(hint.requested_state, environment.start)
        self.assertEqual(player.current_state, environment.start)
        self.assertEqual(len(player.hint_history), 1)
        self.assertEqual(player.metrics().hint_points_spent, hint.cost)

    def test_partial_and_full_hints_record_routes(self):
        environment = simple_environment()
        player = PlayerRun(environment)
        search_run = SearchRun.run(environment, SearchAlgorithm.BFS)
        provider = HintProvider(partial_route_length=2)

        partial = provider.generate_hint(player, search_run, HintLevel.PARTIAL_ROUTE)
        full = provider.generate_hint(player, search_run, HintLevel.FULL_SOLUTION)

        self.assertEqual(partial.route, search_run.path[:3])
        self.assertEqual(full.route, search_run.path)
        self.assertEqual(player.metrics().hints_used, 2)


class ComparisonAndDocumentationTests(unittest.TestCase):
    def test_compare_player_and_algorithm_on_same_environment(self):
        environment = simple_environment()
        player = PlayerRun(environment)
        for action in [Action.RIGHT, Action.RIGHT, Action.DOWN, Action.DOWN]:
            player.move(action)
        search_run = SearchRun.run(environment, SearchAlgorithm.BFS)

        comparison = compare_player_to_search(player, search_run)

        self.assertTrue(comparison.same_environment)
        self.assertTrue(comparison.player_completed)
        self.assertTrue(comparison.search_found_path)
        self.assertEqual(comparison.path_length_delta, 0)
        self.assertEqual(comparison.path_cost_delta, 0)

    def test_intermediate_search_insight_uses_trace_for_player_state(self):
        environment = simple_environment()
        player = PlayerRun(environment)
        player.move(Action.RIGHT)
        search_run = SearchRun.run(environment, SearchAlgorithm.BFS)

        insight = intermediate_search_insight(player, search_run)

        self.assertEqual(insight.state, player.current_state)
        self.assertTrue(insight.discovered)
        self.assertTrue(insight.expanded)
        self.assertEqual(insight.parent, (0, 0))

    def test_algorithm_documentation_exists_for_each_implemented_algorithm(self):
        for algorithm in SearchAlgorithm:
            docs = get_algorithm_documentation(algorithm)
            self.assertEqual(docs.algorithm, algorithm)
            self.assertTrue(docs.name)
            self.assertTrue(docs.pseudocode)
            self.assertTrue(docs.completeness)
            self.assertTrue(docs.implementation_notes)


if __name__ == "__main__":
    unittest.main()
