/**
 * TypeScript types for the Maze Runner backend API.
 *
 * Derived from:
 *   - game_sandbox/api/maze_runner.py (serialization helpers)
 *   - game_sandbox/api/schemas.py (Pydantic request models)
 *   - game_sandbox/games/maze_runner/search_models.py
 *   - game_sandbox/games/maze_runner/runs.py
 *   - game_sandbox/games/maze_runner/hints.py
 */

/* ── Primitives ────────────────────────────────────────────── */

/** [row, column] coordinate pair. */
export type MazeState = [number, number];

export type MazeAction = 'UP' | 'DOWN' | 'LEFT' | 'RIGHT';

/* ── Environment ───────────────────────────────────────────── */

export interface MazeCellResponse {
  row: number;
  column: number;
  kind: 'free' | 'obstacle' | 'start' | 'goal';
  terrain_cost: number | null;
}

export interface MazeEnvironmentMetadata {
  environment_id: string;
  seed: number | null;
  generation_strategy: string;
}

export interface MazeEnvironmentResponse {
  environment_id: string;
  rows: number;
  columns: number;
  width: number;
  height: number;
  start: MazeState;
  goal: MazeState;
  obstacles: MazeState[];
  terrain_costs: Record<string, number>;
  metadata: MazeEnvironmentMetadata;
  cells: MazeCellResponse[][];
}

/* ── Environment creation request ──────────────────────────── */

export interface MazeEnvironmentRequest {
  width?: number;
  height?: number;
  generation_strategy?: string;
  seed?: number | null;
  obstacle_probability?: number;
  ensure_solvable?: boolean;
  start?: MazeState;
  goal?: MazeState;
  obstacles?: MazeState[];
  terrain_costs?: Record<string, number>;
}

/* ── Player run ────────────────────────────────────────────── */

export interface PlayerMetricsResponse {
  total_actions: number;
  valid_actions: number;
  invalid_actions: number;
  path_length: number;
  path_cost: number;
  unique_states: number;
  revisited_states: number;
  hints_used: number;
  hint_points_spent: number;
  total_duration_ms: number | null;
}

export interface PlayerRunResponse {
  run_id: string;
  player_run_id: string;
  environment_id: string;
  current_state: MazeState;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED';
  trajectory: MazeState[];
  movement_cost: number;
  started_at: string;
  completed_at: string | null;
  completed: boolean;
  metrics: PlayerMetricsResponse;
  legal_actions: MazeAction[];
}

export interface PlayerActionRecordResponse {
  action: MazeAction;
  from_state: MazeState;
  to_state: MazeState;
  valid: boolean;
  cost: number;
  transition_cost: number;
  timestamp: string;
  reason: string | null;
}

export interface PlayerActionResponse extends PlayerActionRecordResponse {
  player_run_id: string;
  environment_id: string;
  current_state: MazeState;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED';
  completed: boolean;
  metrics: PlayerMetricsResponse;
  trajectory: MazeState[];
}

export interface PlayerHistoryResponse {
  player_run_id: string;
  environment_id: string;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED';
  actions: PlayerActionRecordResponse[];
  trajectory: MazeState[];
  metrics: PlayerMetricsResponse;
}

/* ── Search run ────────────────────────────────────────────── */

export interface SearchStatsResponse {
  nodes_expanded: number;
  nodes_discovered: number;
  max_frontier_size: number;
  path_length: number;
  path_cost: number;
  execution_time_ms: number;
  path_found: boolean;
  iterations: number;
  depth_limit: number | null;
  cutoff_reached: boolean;
  total_nodes_expanded: number;
  total_nodes_discovered: number;
  heuristic_name: string | null;
}

export interface SearchTraceMetadata {
  event_count: number;
  first_step: number | null;
  last_step: number | null;
}

export interface SearchRunResponse {
  search_run_id: string;
  run_id: string;
  environment_id: string;
  algorithm: string;
  status: string;
  search_status: 'FOUND' | 'NOT_FOUND' | 'CUTOFF';
  path: MazeState[] | null;
  path_length: number;
  path_cost: number;
  statistics: SearchStatsResponse;
  trace_metadata: SearchTraceMetadata;
}

/* ── Search trace events ───────────────────────────────────── */

export type SearchEventType =
  | 'SEARCH_STARTED'
  | 'ITERATION_STARTED'
  | 'FRONTIER_PUSHED'
  | 'FRONTIER_POPPED'
  | 'FRONTIER_UPDATED'
  | 'NODE_DISCOVERED'
  | 'NODE_EXPANDED'
  | 'NODE_CLOSED'
  | 'PARENT_SET'
  | 'DEPTH_LIMIT_REACHED'
  | 'PATH_RECONSTRUCTED'
  | 'SEARCH_FINISHED';

export interface SearchEventResponse {
  step: number;
  event_type: SearchEventType;
  state: MazeState | null;
  action: MazeAction | null;
  parent: MazeState | null;
  depth: number | null;
  cost: number | null;
  frontier_size: number | null;
  iteration: number | null;
  metadata: Record<string, unknown>;
}

export interface SearchTraceResponse {
  search_run_id: string;
  environment_id: string;
  algorithm: string;
  from_index: number;
  count: number;
  total_events: number;
  events: SearchEventResponse[];
}

/* ── Hints ─────────────────────────────────────────────────── */

export type HintLevel = 'NEXT_ACTION' | 'NEXT_STATE' | 'PARTIAL_ROUTE' | 'FULL_SOLUTION';

export interface HintResponse {
  hint_id: string;
  player_run_id: string;
  environment_id: string;
  algorithm: string;
  hint_level: HintLevel;
  level: HintLevel;
  state_when_requested: MazeState;
  requested_state: MazeState;
  timestamp: string;
  points_spent: number;
  cost: number;
  available: boolean;
  suggested_action: MazeAction | null;
  suggested_state: MazeState | null;
  partial_path: MazeState[] | null;
  route: MazeState[] | null;
  reason: string | null;
  search_run_id?: string;
}

export interface HintHistoryResponse {
  player_run_id: string;
  environment_id: string;
  hints: HintResponse[];
  metrics: PlayerMetricsResponse;
}

export interface HintCostEntry {
  NEXT_ACTION: number;
  NEXT_STATE: number;
  PARTIAL_ROUTE: number;
  FULL_SOLUTION: number;
}

export interface HintCostsResponse {
  costs: Record<string, HintCostEntry>;
}

export interface HintRequest {
  hint_level: HintLevel;
  algorithm?: string;
  search_run_id?: string;
}

/* ── Algorithms ────────────────────────────────────────────── */

export interface AlgorithmSummary {
  algorithm: string;
  name: string;
  category: string;
  available: boolean;
  description?: string;
  status?: string;
}

export interface AlgorithmsListResponse {
  available: AlgorithmSummary[];
  planned: AlgorithmSummary[];
}

export interface AlgorithmDocumentationResponse {
  algorithm: string;
  name: string;
  category: string;
  description: string;
  core_idea: string;
  state_representation: string;
  pseudocode: string[];
  step_by_step: string[];
  data_structure: string;
  completeness: string;
  optimality: string;
  time_complexity: string;
  space_complexity: string;
  heuristic_requirements: string;
  weighted_cost_requirements: string;
  mingle_specific_notes: string;
  implementation_notes: string;
  available: boolean;
}

/* ── Comparison ────────────────────────────────────────────── */

export interface ComparisonResponse {
  environment_id: string;
  same_environment: boolean;
  player_run_id: string;
  search_run_id: string;
  player_completed: boolean;
  search_found_path: boolean;
  player_metrics: PlayerMetricsResponse;
  search_metrics: SearchStatsResponse;
  search_stats: SearchStatsResponse;
  path_length_delta: number | null;
  path_cost_delta: number | null;
}

export interface StateSearchInsightResponse {
  state: MazeState;
  discovered: boolean;
  expanded: boolean;
  closed: boolean;
  discovered_step: number | null;
  expanded_step: number | null;
  closed_step: number | null;
  parent: MazeState | null;
  depth: number | null;
  cost: number | null;
  metadata: Record<string, unknown>;
}

export interface IntermediateComparisonResponse {
  player_run_id: string;
  search_run_id: string;
  environment_id: string;
  player_state: MazeState;
  insight: StateSearchInsightResponse;
}
