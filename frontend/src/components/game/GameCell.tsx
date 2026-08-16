import type { Position } from '../../features/tic-tac-toe/types';
import './GameCell.css';

interface GameCellProps {
  value: '' | 'X' | 'O';
  position: Position;
  isClickable: boolean;
  isLastMove: boolean;
  isWinning: boolean;
  onClick: (position: Position) => void;
}

export function GameCell({
  value,
  position,
  isClickable,
  isLastMove,
  isWinning,
  onClick,
}: GameCellProps) {
  const handleClick = () => {
    if (isClickable) onClick(position);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && isClickable) {
      e.preventDefault();
      onClick(position);
    }
  };

  const cellClasses = [
    'game-cell',
    value ? 'occupied' : '',
    value === 'X' ? 'cell-x' : '',
    value === 'O' ? 'cell-o' : '',
    isClickable ? 'clickable' : '',
    isLastMove ? 'last-move' : '',
    isWinning ? 'winning' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      className={cellClasses}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={!isClickable}
      aria-label={`Cell ${position[0]},${position[1]}${value ? `: ${value}` : ': empty'}`}
      tabIndex={isClickable ? 0 : -1}
    >
      {value && <CellMark value={value} />}
    </button>
  );
}

function CellMark({ value }: { value: 'X' | 'O' }) {
  if (value === 'X') {
    return (
      <svg className="cell-mark mark-x" viewBox="0 0 24 24" aria-hidden="true">
        <line x1="5" y1="5" x2="19" y2="19" />
        <line x1="19" y1="5" x2="5" y2="19" />
      </svg>
    );
  }
  return (
    <svg className="cell-mark mark-o" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="7.5" />
    </svg>
  );
}
