import { formatDuration, formatState, formatRunStatus } from '../mapping';
import type { PlayerRunResponse } from '../../../types/maze';
import type { MazeMode } from '../types';
import './MazeStatus.css';

interface MazeStatusProps {
  mode: MazeMode;
  playerRun?: PlayerRunResponse | null;
  elapsedMs?: number;
  searchAlgorithm?: string;
  searchStatus?: string;
  replayProgress?: string;
}

export function MazeStatus({
  mode,
  playerRun,
  elapsedMs,
  searchAlgorithm,
  replayProgress,
}: MazeStatusProps) {
  const modeBadge = {
    config: 'CONFIG',
    play: 'PLAY',
    watch: 'WATCH',
    result: 'RESULT',
  }[mode];

  const modeClass = `mode-${mode}`;

  return (
    <div className="maze-status">
      <span className={`status-badge maze-mode-badge ${modeClass}`}>{modeBadge}</span>

      {mode === 'play' && playerRun && (
        <>
          <span className="maze-status-text">
            {formatState(playerRun.current_state)}
          </span>
          <span className="maze-status-divider">·</span>
          <span className="maze-status-text">
            {playerRun.metrics.total_actions} moves
          </span>
          {playerRun.metrics.invalid_actions > 0 && (
            <>
              <span className="maze-status-divider">·</span>
              <span className="maze-status-text maze-status-warn">
                {playerRun.metrics.invalid_actions} invalid
              </span>
            </>
          )}
          <span className="maze-status-divider">·</span>
          <span className="maze-status-text">
            cost {playerRun.metrics.path_cost}
          </span>
          <span className="maze-status-divider">·</span>
          <span className="maze-status-text maze-status-time">
            {formatDuration(elapsedMs ?? null)}
          </span>
        </>
      )}

      {mode === 'watch' && searchAlgorithm && (
        <>
          <span className="maze-status-algo-badge">{searchAlgorithm}</span>
          {replayProgress && (
            <>
              <span className="maze-status-divider">·</span>
              <span className="maze-status-text maze-status-mono">{replayProgress}</span>
            </>
          )}
        </>
      )}

      {mode === 'result' && playerRun && (
        <>
          <span className={`status-badge result-status-badge ${playerRun.status === 'COMPLETED' ? 'completed' : 'abandoned'}`}>
            {formatRunStatus(playerRun.status)}
          </span>
          <span className="maze-status-divider">·</span>
          <span className="maze-status-text">
            {playerRun.metrics.path_length} steps · cost {playerRun.metrics.path_cost}
          </span>
        </>
      )}
    </div>
  );
}
