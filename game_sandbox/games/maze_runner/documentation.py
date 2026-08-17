"""Structured algorithm documentation for Maze Runner search strategies."""

from __future__ import annotations

from dataclasses import dataclass

from game_sandbox.games.maze_runner.search import SearchAlgorithm, normalize_algorithm


@dataclass(frozen=True)
class AlgorithmDocumentation:
    algorithm: SearchAlgorithm
    name: str
    description: str
    core_idea: str
    state_representation: str
    data_structure: str
    pseudocode: tuple[str, ...]
    step_by_step: tuple[str, ...]
    completeness: str
    optimality: str
    time_complexity: str
    space_complexity: str
    implementation_notes: str


ALGORITHM_DOCUMENTATION: dict[SearchAlgorithm, AlgorithmDocumentation] = {
    SearchAlgorithm.BFS: AlgorithmDocumentation(
        algorithm=SearchAlgorithm.BFS,
        name="Breadth-First Search",
        description="Explores the grid outward from the start one depth layer at a time.",
        core_idea="Visit every state at distance d before visiting states at distance d + 1.",
        state_representation="A grid coordinate represented as (row, column).",
        data_structure="FIFO queue.",
        pseudocode=(
            "enqueue start",
            "while queue is not empty:",
            "  dequeue current",
            "  if current is goal: reconstruct path",
            "  enqueue each undiscovered legal neighbor",
        ),
        step_by_step=(
            "The start state is discovered and put in the queue.",
            "The oldest frontier state is expanded.",
            "Undiscovered neighbors are assigned a parent and queued.",
            "When the goal is expanded, parent links reconstruct the path.",
        ),
        completeness="Complete for finite grids with deterministic legal transitions.",
        optimality="Optimal for equal step costs; not guaranteed optimal for weighted terrain.",
        time_complexity="O(V + E), where V is walkable states and E is legal transitions.",
        space_complexity="O(V).",
        implementation_notes="Neighbor order is deterministic: UP, DOWN, LEFT, RIGHT.",
    ),
    SearchAlgorithm.DFS: AlgorithmDocumentation(
        algorithm=SearchAlgorithm.DFS,
        name="Depth-First Search",
        description="Explores one branch as far as possible before backtracking.",
        core_idea="Prefer the most recently discovered frontier state.",
        state_representation="A grid coordinate represented as (row, column).",
        data_structure="LIFO stack.",
        pseudocode=(
            "push start",
            "while stack is not empty:",
            "  pop current",
            "  if current is goal: reconstruct path",
            "  push each undiscovered legal neighbor",
        ),
        step_by_step=(
            "The start state is pushed onto the stack.",
            "The newest frontier state is expanded.",
            "Neighbors are pushed in reverse deterministic order so expansion preference is stable.",
            "The first found goal path is returned.",
        ),
        completeness="Complete for this finite graph-search implementation.",
        optimality="Not optimal.",
        time_complexity="O(V + E).",
        space_complexity="O(V).",
        implementation_notes="Visited states are marked when discovered to avoid cycles.",
    ),
    SearchAlgorithm.DLS: AlgorithmDocumentation(
        algorithm=SearchAlgorithm.DLS,
        name="Depth-Limited Search",
        description="Runs depth-first search with a fixed maximum depth.",
        core_idea="Use DFS but stop expanding states at the configured depth limit.",
        state_representation="A grid coordinate represented as (row, column), with depth metadata.",
        data_structure="LIFO stack with depth and path bookkeeping.",
        pseudocode=(
            "push start at depth 0",
            "while stack is not empty:",
            "  pop current",
            "  if current is goal: reconstruct path",
            "  if depth is limit: record cutoff",
            "  otherwise push legal neighbors",
        ),
        step_by_step=(
            "The search follows DFS behavior.",
            "States at the depth limit are recorded as cut off.",
            "A result distinguishes no solution from a depth cutoff where possible.",
        ),
        completeness="Complete only when the depth limit is at least the solution depth.",
        optimality="Not optimal.",
        time_complexity="O(b^l), where b is branching factor and l is the depth limit.",
        space_complexity="O(V) for graph bookkeeping in this implementation.",
        implementation_notes="The trace records DEPTH_LIMIT_REACHED events for replay and education.",
    ),
    SearchAlgorithm.IDDFS: AlgorithmDocumentation(
        algorithm=SearchAlgorithm.IDDFS,
        name="Iterative Deepening Depth-First Search",
        description="Repeatedly runs depth-limited search with increasing limits.",
        core_idea="Combine DFS memory behavior with BFS-like shallowest-solution discovery.",
        state_representation="A grid coordinate represented as (row, column), with iteration depth.",
        data_structure="Repeated LIFO stack searches.",
        pseudocode=(
            "for limit from 0 to max_depth:",
            "  run depth-limited search with this limit",
            "  if goal found: return path",
        ),
        step_by_step=(
            "Iteration 1 searches depth 0.",
            "Each later iteration increases the depth limit by one.",
            "The trace keeps iteration markers so repeated work can be replayed.",
        ),
        completeness="Complete for finite grids when max_depth reaches a solution depth.",
        optimality="Optimal by number of actions for unweighted grids with deterministic increasing limits.",
        time_complexity="O(b^d), with repeated shallow expansions.",
        space_complexity="O(V) for graph bookkeeping in each iteration.",
        implementation_notes="Cumulative statistics preserve total repeated search effort.",
    ),
    SearchAlgorithm.UCS: AlgorithmDocumentation(
        algorithm=SearchAlgorithm.UCS,
        name="Uniform-Cost Search",
        description="Expands the frontier state with the lowest known path cost.",
        core_idea="Prefer cheapest accumulated movement cost g(n), not the fewest actions.",
        state_representation="A grid coordinate represented as (row, column), with g cost metadata.",
        data_structure="Priority queue ordered by path cost.",
        pseudocode=(
            "push start with priority 0",
            "while priority queue is not empty:",
            "  pop the lowest-cost state",
            "  if current is goal: reconstruct path",
            "  relax each legal neighbor using transition cost",
        ),
        step_by_step=(
            "The start state enters the priority queue with cost 0.",
            "The cheapest frontier state is expanded next.",
            "If a cheaper route to a known state is found, its parent and cost are updated.",
            "The first time the goal is expanded, its path cost is optimal.",
        ),
        completeness="Complete for finite grids with positive transition costs.",
        optimality="Optimal for positive weighted terrain costs.",
        time_complexity="O((V + E) log V) with a binary heap.",
        space_complexity="O(V).",
        implementation_notes="Trace metadata records g and priority values for replay.",
    ),
    SearchAlgorithm.GREEDY_BEST_FIRST: AlgorithmDocumentation(
        algorithm=SearchAlgorithm.GREEDY_BEST_FIRST,
        name="Greedy Best-First Search",
        description="Expands the state that appears closest to the goal according to a heuristic.",
        core_idea="Prefer lowest h(n), ignoring accumulated path cost.",
        state_representation="A grid coordinate represented as (row, column), with h metadata.",
        data_structure="Priority queue ordered by heuristic estimate.",
        pseudocode=(
            "push start with priority h(start)",
            "while priority queue is not empty:",
            "  pop the lowest-heuristic state",
            "  if current is goal: reconstruct path",
            "  push/update legal neighbors using h(neighbor)",
        ),
        step_by_step=(
            "The heuristic estimates distance from each frontier state to the goal.",
            "The state with the smallest estimate is expanded.",
            "This can move quickly toward the goal but may miss cheaper routes.",
        ),
        completeness="Complete for this finite graph-search implementation.",
        optimality="Not optimal.",
        time_complexity="O((V + E) log V) with a binary heap.",
        space_complexity="O(V).",
        implementation_notes="Manhattan distance is the default heuristic for 4-direction grids.",
    ),
    SearchAlgorithm.ASTAR: AlgorithmDocumentation(
        algorithm=SearchAlgorithm.ASTAR,
        name="A* Search",
        description="Balances known path cost and estimated remaining cost.",
        core_idea="Prefer lowest f(n) = g(n) + h(n).",
        state_representation="A grid coordinate represented as (row, column), with g, h, and f metadata.",
        data_structure="Priority queue ordered by f score.",
        pseudocode=(
            "push start with f = h(start)",
            "while priority queue is not empty:",
            "  pop the lowest-f state",
            "  if current is goal: reconstruct path",
            "  relax each legal neighbor using g + h",
        ),
        step_by_step=(
            "g tracks the exact cost paid to reach a state.",
            "h estimates the remaining cost to the goal.",
            "f combines both values to choose the next frontier state.",
            "If a cheaper parent is found, the state is reinserted with a better f score.",
        ),
        completeness="Complete for finite grids with positive transition costs.",
        optimality="Optimal when the heuristic is admissible and consistent.",
        time_complexity="O((V + E) log V) with a binary heap, depending on heuristic quality.",
        space_complexity="O(V).",
        implementation_notes="Trace metadata records g, h, f, and priority values for each state.",
    ),
}


def get_algorithm_documentation(
    algorithm: SearchAlgorithm | str,
) -> AlgorithmDocumentation:
    return ALGORITHM_DOCUMENTATION[normalize_algorithm(algorithm)]
