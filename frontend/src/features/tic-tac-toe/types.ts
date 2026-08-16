/**
 * Frontend domain types for Tic-Tac-Toe.
 * These separate the UI representation from raw API response shapes.
 */

export type CellValue = '' | 'X' | 'O';
export type Board = CellValue[][];
export type Position = [number, number];

export type GameStatus =
  | 'IN_PROGRESS'
  | 'PLAYER_X_WINS'
  | 'PLAYER_O_WINS'
  | 'DRAW';

/**
 * Agent types from the backend agent registry.
 * See: game_sandbox/agents/registry.py → AGENT_REGISTRY
 */
export const AGENT_TYPES = ['human', 'random', 'minimax', 'alphabeta'] as const;
export type AgentType = (typeof AGENT_TYPES)[number];

export const AGENT_LABELS: Record<AgentType, string> = {
  human: 'Human',
  random: 'Random',
  minimax: 'Minimax',
  alphabeta: 'Alpha-Beta',
};
