import {
  formatAgentName,
  getStatusText,
  mapStatus,
} from '../../features/tic-tac-toe/mapping';
import type { GameStateResponse, MoveRecord } from '../../types/api';
import './GameStatus.css';

interface GameStatusProps {
  gameState: GameStateResponse;
  players: Record<string, string>;
  isSubmitting: boolean;
  isReplayMode: boolean;
  replayMove: MoveRecord | null;
}

export function GameStatus({
  gameState,
  players,
  isSubmitting,
  isReplayMode,
  replayMove,
}: GameStatusProps) {
  const status = mapStatus(gameState.status);

  if (isReplayMode && replayMove) {
    const agentName = players[replayMove.player];
    return (
      <div className="game-status replay-status">
        <span className="status-badge replay-badge">REPLAY</span>
        <span className="status-text">
          Move {replayMove.move_number} · {replayMove.player}
          {agentName && agentName !== 'human' && (
            <span className="status-agent"> · {formatAgentName(agentName)}</span>
          )}
        </span>
      </div>
    );
  }

  const statusText = getStatusText(
    status,
    gameState.current_player,
    players,
    isSubmitting,
  );

  const isOver = status !== 'IN_PROGRESS';

  return (
    <div className={`game-status ${isOver ? 'status-over' : ''}`}>
      {isSubmitting && (
        <span className="status-badge thinking-badge">
          <span className="thinking-dot" />
          <span className="thinking-dot" />
          <span className="thinking-dot" />
        </span>
      )}
      {!isSubmitting && !isOver && (
        <span className="status-indicator" data-player={gameState.current_player}>
          {gameState.current_player}
        </span>
      )}
      {isOver && (
        <span className="status-badge result-badge">GAME OVER</span>
      )}
      <span className="status-text">{statusText}</span>
    </div>
  );
}
