import type { ReplaySpeed } from '../types';
import { REPLAY_SPEEDS } from '../types';
import './SearchReplayControls.css';

interface SearchReplayControlsProps {
  currentIndex: number;
  totalEvents: number;
  isPlaying: boolean;
  speed: ReplaySpeed;
  onPlay: () => void;
  onPause: () => void;
  onStep: () => void;
  onStepBack: () => void;
  onReset: () => void;
  onSetSpeed: (speed: ReplaySpeed) => void;
}

export function SearchReplayControls({
  currentIndex,
  totalEvents,
  isPlaying,
  speed,
  onPlay,
  onPause,
  onStep,
  onStepBack,
  onReset,
  onSetSpeed,
}: SearchReplayControlsProps) {
  const progress = totalEvents > 0
    ? `${Math.max(0, currentIndex + 1)} / ${totalEvents}`
    : '0 / 0';

  const atStart = currentIndex <= -1;
  const atEnd = currentIndex >= totalEvents - 1;

  return (
    <div className="search-replay-controls">
      <div className="replay-transport">
        <button
          className="replay-btn"
          onClick={onReset}
          disabled={atStart}
          aria-label="Reset"
          title="Reset"
        >
          ⏮
        </button>
        <button
          className="replay-btn"
          onClick={onStepBack}
          disabled={atStart}
          aria-label="Step back"
          title="Step back"
        >
          ⏪
        </button>
        {isPlaying ? (
          <button
            className="replay-btn replay-btn-primary"
            onClick={onPause}
            aria-label="Pause"
            title="Pause"
          >
            ⏸
          </button>
        ) : (
          <button
            className="replay-btn replay-btn-primary"
            onClick={onPlay}
            disabled={atEnd && totalEvents > 0}
            aria-label="Play"
            title="Play"
          >
            ▶
          </button>
        )}
        <button
          className="replay-btn"
          onClick={onStep}
          disabled={atEnd}
          aria-label="Step forward"
          title="Step forward"
        >
          ⏩
        </button>
      </div>

      <div className="replay-progress">
        <span className="replay-progress-text">{progress}</span>
        {totalEvents > 0 && (
          <div className="replay-progress-bar">
            <div
              className="replay-progress-fill"
              style={{
                width: `${((currentIndex + 1) / totalEvents) * 100}%`,
              }}
            />
          </div>
        )}
      </div>

      <div className="replay-speed-selector">
        {REPLAY_SPEEDS.map((s) => (
          <button
            key={s}
            className={`speed-chip ${speed === s ? 'active' : ''}`}
            onClick={() => onSetSpeed(s)}
            aria-label={`Speed ${s}x`}
          >
            {s}×
          </button>
        ))}
      </div>
    </div>
  );
}
