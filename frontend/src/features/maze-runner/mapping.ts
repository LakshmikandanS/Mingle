/**
 * Mapping helpers between backend API responses and frontend domain types.
 * Prevents raw backend structures from leaking into every UI component.
 */

import type { HintLevel, MazeAction, SearchEventType } from '../../types/maze';

/* ── Algorithm display ─────────────────────────────────────── */

const ALGORITHM_DISPLAY_NAMES: Record<string, string> = {
  bfs: 'BFS',
  dfs: 'DFS',
  dls: 'DLS',
  iddfs: 'IDDFS',
  ucs: 'UCS',
  greedy_best_first: 'Greedy Best-First',
  astar: 'A*',
  ida_star: 'IDA*',
  rbfs: 'RBFS',
  sma_star: 'SMA*',
};

export function formatAlgorithmName(algorithm: string): string {
  return ALGORITHM_DISPLAY_NAMES[algorithm] ?? algorithm;
}

/* ── Category display ──────────────────────────────────────── */

const CATEGORY_LABELS: Record<string, string> = {
  uninformed: 'Uninformed Search',
  cost: 'Cost-Based Search',
  heuristic: 'Heuristic Search',
  memory_bounded: 'Memory-Bounded Search',
};

export function formatCategory(category: string): string {
  return CATEGORY_LABELS[category] ?? category;
}

/* ── Action display ────────────────────────────────────────── */

const ACTION_ARROWS: Record<MazeAction, string> = {
  UP: '↑',
  DOWN: '↓',
  LEFT: '←',
  RIGHT: '→',
};

const ACTION_LABELS: Record<MazeAction, string> = {
  UP: 'Up',
  DOWN: 'Down',
  LEFT: 'Left',
  RIGHT: 'Right',
};

export function formatAction(action: MazeAction): string {
  return ACTION_LABELS[action] ?? action;
}

export function actionArrow(action: MazeAction): string {
  return ACTION_ARROWS[action] ?? action;
}

/* ── Hint level display ────────────────────────────────────── */

const HINT_LEVEL_LABELS: Record<HintLevel, string> = {
  NEXT_ACTION: 'Direction',
  NEXT_STATE: 'Next Cell',
  PARTIAL_ROUTE: 'Partial Route',
  FULL_SOLUTION: 'Full Solution',
};

export function formatHintLevel(level: HintLevel): string {
  return HINT_LEVEL_LABELS[level] ?? level;
}

/* ── Event type display ────────────────────────────────────── */

const EVENT_TYPE_LABELS: Record<SearchEventType, string> = {
  SEARCH_STARTED: 'Search Started',
  ITERATION_STARTED: 'Iteration Started',
  FRONTIER_PUSHED: 'Frontier Push',
  FRONTIER_POPPED: 'Frontier Pop',
  FRONTIER_UPDATED: 'Frontier Update',
  NODE_DISCOVERED: 'Discovered',
  NODE_EXPANDED: 'Expanded',
  NODE_CLOSED: 'Closed',
  PARENT_SET: 'Parent Set',
  DEPTH_LIMIT_REACHED: 'Depth Limit',
  PATH_RECONSTRUCTED: 'Path Reconstructed',
  SEARCH_FINISHED: 'Search Finished',
};

export function formatEventType(eventType: SearchEventType): string {
  return EVENT_TYPE_LABELS[eventType] ?? eventType;
}

/* ── Duration formatting ───────────────────────────────────── */

export function formatDuration(ms: number | null | undefined): string {
  if (ms == null) return '—';
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  const seconds = ms / 1000;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  return `${minutes}m ${remaining.toFixed(0)}s`;
}

/* ── State formatting ──────────────────────────────────────── */

export function formatState(state: [number, number] | null | undefined): string {
  if (!state) return '—';
  return `[${state[0]}, ${state[1]}]`;
}

/* ── Run status helpers ────────────────────────────────────── */

export function isRunFinished(status: string): boolean {
  return status === 'COMPLETED' || status === 'ABANDONED';
}

export function formatRunStatus(status: string): string {
  switch (status) {
    case 'IN_PROGRESS': return 'In Progress';
    case 'COMPLETED': return 'Completed';
    case 'ABANDONED': return 'Abandoned';
    default: return status;
  }
}

/* ── State comparison ──────────────────────────────────────── */

export function statesEqual(
  a: [number, number] | null | undefined,
  b: [number, number] | null | undefined,
): boolean {
  if (!a || !b) return false;
  return a[0] === b[0] && a[1] === b[1];
}

export function stateKey(state: [number, number]): string {
  return `${state[0]},${state[1]}`;
}
