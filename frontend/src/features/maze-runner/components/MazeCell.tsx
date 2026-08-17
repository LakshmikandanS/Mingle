import { memo } from 'react';
import type { CellKind, CellOverlay } from '../types';
import './MazeCell.css';

interface MazeCellProps {
  row: number;
  col: number;
  kind: CellKind;
  terrainCost: number | null;
  overlays: CellOverlay[];
  onClick?: () => void;
  isClickable: boolean;
}

/**
 * Individual maze cell with composable visual states.
 * Uses icons + patterns + borders (not color-only) for accessibility.
 */
export const MazeCell = memo(function MazeCell({
  row,
  col,
  kind,
  terrainCost,
  overlays,
  onClick,
  isClickable,
}: MazeCellProps) {
  const classes = [
    'maze-cell',
    `kind-${kind}`,
    ...overlays.map((o) => `overlay-${o}`),
    isClickable ? 'clickable' : '',
  ]
    .filter(Boolean)
    .join(' ');

  const handleClick = () => {
    if (isClickable && onClick) onClick();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && isClickable && onClick) {
      e.preventDefault();
      onClick();
    }
  };

  const showCost = terrainCost !== null && terrainCost > 1 && kind !== 'obstacle';

  return (
    <button
      className={classes}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={!isClickable}
      tabIndex={isClickable ? 0 : -1}
      aria-label={cellAriaLabel(row, col, kind, overlays, terrainCost)}
      data-row={row}
      data-col={col}
    >
      {/* Cell kind icons */}
      {kind === 'obstacle' && <span className="cell-icon obstacle-icon" aria-hidden="true">╳</span>}
      {kind === 'start' && !overlays.includes('player') && (
        <span className="cell-icon start-icon" aria-hidden="true">◆</span>
      )}
      {kind === 'goal' && !overlays.includes('player') && (
        <span className="cell-icon goal-icon" aria-hidden="true">★</span>
      )}

      {/* Overlay icons */}
      {overlays.includes('player') && (
        <span className="cell-icon player-icon" aria-hidden="true">●</span>
      )}
      {overlays.includes('search-current') && (
        <span className="cell-icon search-current-icon" aria-hidden="true">◎</span>
      )}
      {overlays.includes('search-discovered') && !overlays.includes('search-expanded') && !overlays.includes('search-current') && (
        <span className="cell-icon search-discovered-icon" aria-hidden="true">◇</span>
      )}
      {overlays.includes('search-expanded') && !overlays.includes('search-current') && (
        <span className="cell-icon search-expanded-icon" aria-hidden="true">◈</span>
      )}
      {overlays.includes('hint-target') && (
        <span className="cell-icon hint-icon" aria-hidden="true">✦</span>
      )}

      {/* Terrain cost label */}
      {showCost && (
        <span className="terrain-cost-label" aria-hidden="true">{terrainCost}</span>
      )}
    </button>
  );
});

function cellAriaLabel(
  row: number,
  col: number,
  kind: CellKind,
  overlays: CellOverlay[],
  terrainCost: number | null,
): string {
  const parts = [`Cell ${row},${col}`];
  if (kind !== 'free') parts.push(kind);
  if (overlays.includes('player')) parts.push('player');
  if (overlays.includes('search-current')) parts.push('current search node');
  if (overlays.includes('search-expanded')) parts.push('expanded');
  if (overlays.includes('search-discovered')) parts.push('discovered');
  if (overlays.includes('search-frontier')) parts.push('frontier');
  if (terrainCost !== null && terrainCost > 1) parts.push(`cost ${terrainCost}`);
  return parts.join(', ');
}
