import type { MoveRecord } from '../../types/api';
import './ReplayTimeline.css';

interface ReplayTimelineProps {
  moves: MoveRecord[];
  selectedIndex: number | null;
  onSelectMove: (index: number) => void;
  onExitReplay: () => void;
  isReplayMode: boolean;
  onNext: () => void;
  onPrev: () => void;
  players: Record<string, string>;
}

export function ReplayTimeline({
  moves,
  selectedIndex,
  onSelectMove,
  onExitReplay,
  isReplayMode,
  onNext,
  onPrev,
  players,
}: ReplayTimelineProps) {
  if (moves.length === 0) return null;

  return (
    <div className="replay-timeline">
      <div className="timeline-header">
        <span className="timeline-label">Replay</span>
        <div className="timeline-controls">
          <button
            className="timeline-btn"
            onClick={onPrev}
            disabled={!isReplayMode || selectedIndex === 0}
            aria-label="Previous move"
          >
            ‹
          </button>
          <button
            className="timeline-btn"
            onClick={onNext}
            disabled={
              !isReplayMode || selectedIndex === moves.length - 1
            }
            aria-label="Next move"
          >
            ›
          </button>
          {isReplayMode && (
            <button
              className="timeline-btn exit-btn"
              onClick={onExitReplay}
              aria-label="Exit replay"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      <div className="timeline-track" role="listbox" aria-label="Move history">
        {moves.map((move, index) => {
          const isAgent = players[move.player] !== 'human';
          const isSelected = selectedIndex === index;

          return (
            <div key={move.move_number} className="timeline-segment">
              {index > 0 && <div className="timeline-connector" />}
              <button
                className={[
                  'timeline-dot',
                  isSelected ? 'selected' : '',
                  isAgent ? 'agent-move' : '',
                ]
                  .filter(Boolean)
                  .join(' ')}
                onClick={() => onSelectMove(index)}
                role="option"
                aria-selected={isSelected}
                aria-label={`Move ${move.move_number}: ${move.player} at ${move.action[0]},${move.action[1]}${isAgent ? ' (agent)' : ''}`}
              >
                <span className="dot-player">{move.player}</span>
                <span className="dot-number">{move.move_number}</span>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
