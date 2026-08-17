import type { MazeAction } from '../../../types/maze';
import './PlayerControls.css';

interface PlayerControlsProps {
  onMove: (action: MazeAction) => void;
  onGiveUp: () => void;
  onHint?: () => void;
  disabled: boolean;
  showGiveUpConfirm: boolean;
  onConfirmGiveUp: () => void;
  onCancelGiveUp: () => void;
  onRequestGiveUp: () => void;
}

export function PlayerControls({
  onMove,
  disabled,
  showGiveUpConfirm,
  onConfirmGiveUp,
  onCancelGiveUp,
  onRequestGiveUp,
  onHint,
}: PlayerControlsProps) {
  return (
    <div className="player-controls">
      {/* Direction pad */}
      <div className="dpad">
        <button
          className="dpad-btn dpad-up"
          onClick={() => onMove('UP')}
          disabled={disabled}
          aria-label="Move up"
        >
          ▲
        </button>
        <div className="dpad-middle">
          <button
            className="dpad-btn dpad-left"
            onClick={() => onMove('LEFT')}
            disabled={disabled}
            aria-label="Move left"
          >
            ◄
          </button>
          <div className="dpad-center" />
          <button
            className="dpad-btn dpad-right"
            onClick={() => onMove('RIGHT')}
            disabled={disabled}
            aria-label="Move right"
          >
            ►
          </button>
        </div>
        <button
          className="dpad-btn dpad-down"
          onClick={() => onMove('DOWN')}
          disabled={disabled}
          aria-label="Move down"
        >
          ▼
        </button>
      </div>

      {/* Action buttons */}
      <div className="player-actions">
        {onHint && (
          <button
            className="player-action-btn hint-btn"
            onClick={onHint}
            disabled={disabled}
          >
            💡 Hint
          </button>
        )}
        {!showGiveUpConfirm ? (
          <button
            className="player-action-btn giveup-btn"
            onClick={onRequestGiveUp}
            disabled={disabled}
          >
            Give Up
          </button>
        ) : (
          <div className="giveup-confirm">
            <span className="giveup-confirm-text">Are you sure?</span>
            <button className="giveup-confirm-yes" onClick={onConfirmGiveUp}>
              Yes
            </button>
            <button className="giveup-confirm-no" onClick={onCancelGiveUp}>
              No
            </button>
          </div>
        )}
      </div>

      <p className="controls-hint">
        Use <kbd>↑</kbd> <kbd>↓</kbd> <kbd>←</kbd> <kbd>→</kbd> or click adjacent cells
      </p>
    </div>
  );
}
