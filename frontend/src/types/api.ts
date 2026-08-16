/**
 * TypeScript types corresponding to the actual Mingle backend API.
 *
 * These are derived from:
 *   - game_sandbox/api/schemas.py (Pydantic models)
 *   - game_sandbox/observability/metrics.py (SearchMetrics dataclass)
 *   - game_sandbox/games/tic_tac_toe/game.py (board shape)
 */

/* ── Request types ─────────────────────────────────────────── */

export interface CreateGameRequest {
  game: string;
  players: Record<string, string>;
}

export interface ActionRequest {
  action: [number, number];
}

/* ── Response types ────────────────────────────────────────── */

export interface GameStateResponse {
  session_id: string;
  game: string;
  state: TicTacToeState;
  current_player: string;
  legal_actions: [number, number][];
  status: string;
}

/** Tic-Tac-Toe board state: 3×3 grid where cells are "" | "X" | "O" */
export interface TicTacToeState {
  board: string[][];
}

export interface MoveRecord {
  move_number: number;
  player: string;
  action: [number, number];
  resulting_state: TicTacToeState;
  decision_id: string | null;
}

export interface ReplayResponse {
  session_id: string;
  game: string;
  initial_state: TicTacToeState;
  moves: MoveRecord[];
  final_state: TicTacToeState | null;
}

/**
 * Metrics from the backend SearchMetrics dataclass.
 * All 6 fields are always present (default to 0).
 */
export interface SearchMetrics {
  nodes_explored: number;
  terminal_nodes: number;
  deep_copies: number;
  max_depth: number;
  branches_considered: number;
  pruning_cutoffs: number;
}

export interface DecisionResponse {
  decision_id: string;
  player: string;
  agent: string;
  chosen_action: [number, number];
  duration_ms: number;
  metrics: SearchMetrics;
}
