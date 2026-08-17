import { useMemo } from 'react';
import type { MazeCellResponse, MazeState, SearchEventResponse } from '../../../types/maze';
import type { BoardLayer, CellOverlay } from '../types';
import { statesEqual } from '../mapping';
import { MazeCell } from './MazeCell';
import './MazeBoard.css';

interface MazeBoardProps {
  cells: MazeCellResponse[][];
  rows: number;
  columns: number;
  playerState?: MazeState | null;
  playerTrajectory?: MazeState[];
  searchEvents?: SearchEventResponse[];
  searchPath?: MazeState[] | null;
  currentSearchEventIndex?: number;
  hintTarget?: MazeState | null;
  hintPath?: MazeState[] | null;
  layers: Record<BoardLayer, boolean>;
  onCellClick?: (row: number, col: number) => void;
  disabled?: boolean;
}

/**
 * Grid board renderer. Composes MazeCell components with overlay states
 * derived from player trajectory, search events, and hint data.
 */
export function MazeBoard({
  cells,
  rows,
  columns,
  playerState,
  playerTrajectory = [],
  searchEvents = [],
  searchPath,
  currentSearchEventIndex = -1,
  hintTarget,
  hintPath,
  layers,
  onCellClick,
  disabled = false,
}: MazeBoardProps) {
  // Build lookup sets for search state at current replay index
  const searchState = useMemo(() => {
    const discovered = new Set<string>();
    const expanded = new Set<string>();
    const frontier = new Set<string>();
    const closed = new Set<string>();
    let currentNode: string | null = null;

    const visibleEvents = searchEvents.slice(0, currentSearchEventIndex + 1);
    for (const event of visibleEvents) {
      if (!event.state) continue;
      const key = `${event.state[0]},${event.state[1]}`;

      switch (event.event_type) {
        case 'NODE_DISCOVERED':
          discovered.add(key);
          frontier.add(key);
          break;
        case 'NODE_EXPANDED':
          expanded.add(key);
          frontier.delete(key);
          currentNode = key;
          break;
        case 'NODE_CLOSED':
          closed.add(key);
          frontier.delete(key);
          break;
        case 'FRONTIER_POPPED':
          frontier.delete(key);
          currentNode = key;
          break;
        case 'FRONTIER_PUSHED':
          frontier.add(key);
          break;
      }
    }

    return { discovered, expanded, frontier, closed, currentNode };
  }, [searchEvents, currentSearchEventIndex]);

  // Player path set
  const playerPathSet = useMemo(() => {
    const set = new Set<string>();
    for (const s of playerTrajectory) {
      set.add(`${s[0]},${s[1]}`);
    }
    return set;
  }, [playerTrajectory]);

  // Search path set
  const searchPathSet = useMemo(() => {
    const set = new Set<string>();
    if (searchPath) {
      for (const s of searchPath) {
        set.add(`${s[0]},${s[1]}`);
      }
    }
    return set;
  }, [searchPath]);

  // Hint path set
  const hintPathSet = useMemo(() => {
    const set = new Set<string>();
    if (hintPath) {
      for (const s of hintPath) {
        set.add(`${s[0]},${s[1]}`);
      }
    }
    return set;
  }, [hintPath]);

  // Determine if a cell is adjacent to the player (for click-to-move)
  const isAdjacentToPlayer = (row: number, col: number): boolean => {
    if (!playerState || disabled) return false;
    const dr = Math.abs(row - playerState[0]);
    const dc = Math.abs(col - playerState[1]);
    return (dr === 1 && dc === 0) || (dr === 0 && dc === 1);
  };

  return (
    <div
      className="maze-board-container"
      role="grid"
      aria-label="Maze Runner board"
    >
      <div
        className="maze-board"
        style={{
          gridTemplateColumns: `repeat(${columns}, 1fr)`,
          gridTemplateRows: `repeat(${rows}, 1fr)`,
        }}
      >
        {cells.map((row, rowIdx) =>
          row.map((cell, colIdx) => {
            const key = `${rowIdx},${colIdx}`;
            const overlays: CellOverlay[] = [];

            // Player overlays
            if (playerState && statesEqual(playerState, [rowIdx, colIdx])) {
              overlays.push('player');
            } else if (layers.playerPath && playerPathSet.has(key)) {
              overlays.push('player-path');
            }

            // Search overlays
            if (layers.searchTrace) {
              if (searchState.currentNode === key) {
                overlays.push('search-current');
              }
              if (layers.expanded && searchState.expanded.has(key)) {
                overlays.push('search-expanded');
              }
              if (searchState.discovered.has(key) && !searchState.expanded.has(key)) {
                overlays.push('search-discovered');
              }
              if (layers.frontier && searchState.frontier.has(key)) {
                overlays.push('search-frontier');
              }
              if (searchState.closed.has(key)) {
                overlays.push('search-closed');
              }
            }

            // Algorithm path overlay
            if (layers.algorithmPath && searchPathSet.has(key)) {
              overlays.push('search-path');
            }

            // Hint overlays
            if (hintTarget && statesEqual(hintTarget, [rowIdx, colIdx])) {
              overlays.push('hint-target');
            }
            if (hintPathSet.has(key)) {
              overlays.push('hint-path');
            }

            const clickable = !disabled && onCellClick !== undefined && isAdjacentToPlayer(rowIdx, colIdx);

            return (
              <MazeCell
                key={key}
                row={rowIdx}
                col={colIdx}
                kind={cell.kind}
                terrainCost={cell.terrain_cost}
                overlays={overlays}
                onClick={clickable ? () => onCellClick!(rowIdx, colIdx) : undefined}
                isClickable={clickable}
              />
            );
          }),
        )}
      </div>
    </div>
  );
}
