/**
 * Frontend domain types for Maze Runner.
 * These separate UI representation from raw API response shapes.
 */

/** Visual cell kinds displayed on the board. */
export type CellKind = 'free' | 'obstacle' | 'start' | 'goal';

/**
 * Composable overlay states that can be applied to any cell.
 * Multiple overlays can be active simultaneously.
 */
export type CellOverlay =
  | 'player'
  | 'player-path'
  | 'hint-target'
  | 'hint-path'
  | 'search-current'
  | 'search-discovered'
  | 'search-expanded'
  | 'search-frontier'
  | 'search-closed'
  | 'search-path';

/** Visualization layers the user can toggle. */
export type BoardLayer =
  | 'playerPath'
  | 'algorithmPath'
  | 'searchTrace'
  | 'frontier'
  | 'expanded';

/** All toggleable layers and their defaults. */
export const DEFAULT_LAYERS: Record<BoardLayer, boolean> = {
  playerPath: true,
  algorithmPath: true,
  searchTrace: false,
  frontier: false,
  expanded: false,
};

/** Maze Runner application modes. */
export type MazeMode = 'config' | 'play' | 'watch' | 'result';

/** Supported replay speeds. */
export const REPLAY_SPEEDS = [0.25, 0.5, 1, 2, 4] as const;
export type ReplaySpeed = (typeof REPLAY_SPEEDS)[number];

/** Generation strategies supported by the backend. */
export const GENERATION_STRATEGIES = [
  { value: 'random', label: 'Random Obstacles' },
  { value: 'empty', label: 'Empty Grid' },
] as const;
export type GenerationStrategy = (typeof GENERATION_STRATEGIES)[number]['value'];

/** Hint level display information. */
export const HINT_LEVEL_INFO = [
  {
    value: 'NEXT_ACTION' as const,
    label: 'Direction',
    description: 'Suggests the next direction to move',
    level: 1,
  },
  {
    value: 'NEXT_STATE' as const,
    label: 'Next Cell',
    description: 'Shows the next cell to visit',
    level: 2,
  },
  {
    value: 'PARTIAL_ROUTE' as const,
    label: 'Partial Route',
    description: 'Shows a few steps of the optimal path',
    level: 3,
  },
  {
    value: 'FULL_SOLUTION' as const,
    label: 'Full Solution',
    description: 'Reveals the complete solution path',
    level: 4,
  },
] as const;
