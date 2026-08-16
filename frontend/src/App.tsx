import { useGame } from './hooks/useGame';
import { useReplay } from './hooks/useReplay';
import {
  formatAgentName,
  isHumanTurn,
  mapStatus,
  isGameOver as checkGameOver,
} from './features/tic-tac-toe/mapping';
import { BackgroundGrid } from './components/layout/BackgroundGrid';
import { Header } from './components/layout/Header';
import { GameBoard } from './components/game/GameBoard';
import { GameStatus } from './components/game/GameStatus';
import { NewGameForm } from './components/config/NewGameForm';
import { DecisionPanel } from './components/inspector/DecisionPanel';
import { ReplayTimeline } from './components/replay/ReplayTimeline';
import './App.css';

export default function App() {
  const game = useGame();
  const replay = useReplay(game.gameState?.session_id, game.replayData);

  const hasGame = game.gameState !== null;
  const status = hasGame ? mapStatus(game.gameState!.status) : null;
  const gameOver = status ? checkGameOver(status) : false;

  // Determine which board/state to display
  const displayBoard = replay.isReplayMode
    ? replay.selectedBoardState!
    : game.gameState?.state.board;

  // Determine if board should be interactive
  const boardDisabled =
    !hasGame ||
    replay.isReplayMode ||
    game.isSubmitting ||
    gameOver ||
    !isHumanTurn(game.gameState!, game.players);

  // Determine the last move for highlighting
  const lastMove = replay.isReplayMode
    ? replay.selectedMove
    : game.replayData && game.replayData.moves.length > 0
      ? game.replayData.moves[game.replayData.moves.length - 1]
      : null;

  // Decision to show: replay-selected or latest live decision
  const activeDecision = replay.isReplayMode
    ? replay.selectedDecision
    : game.latestDecision;

  return (
    <div className="app">
      <BackgroundGrid />
      <Header hasGame={hasGame} onLogoClick={game.resetGame} />

      {!hasGame ? (
        /* ── Welcome / New game screen ── */
        <main className="welcome-screen">
          <div className="welcome-brand">
            <h1 className="welcome-title">mingle</h1>
            <p className="welcome-subtitle">
              Play against agents. Observe how they think.
            </p>
          </div>
          <NewGameForm
            onCreateGame={game.createGame}
            isLoading={game.isLoading}
            error={game.error}
          />
        </main>
      ) : (
        /* ── Active game layout ── */
        <main className="game-layout">
          <div className="game-area">
            <GameStatus
              gameState={game.gameState!}
              players={game.players}
              isSubmitting={game.isSubmitting}
              isReplayMode={replay.isReplayMode}
              replayMove={replay.selectedMove}
            />

            {displayBoard && (
              <GameBoard
                board={displayBoard}
                legalActions={game.gameState!.legal_actions}
                onCellClick={game.submitAction}
                disabled={boardDisabled}
                lastMove={lastMove}
                isGameOver={gameOver}
              />
            )}

            <ReplayTimeline
              moves={replay.moves}
              selectedIndex={replay.selectedMoveIndex}
              onSelectMove={replay.selectMove}
              onExitReplay={replay.exitReplay}
              isReplayMode={replay.isReplayMode}
              onNext={replay.goNext}
              onPrev={replay.goPrev}
              players={game.players}
            />
          </div>

          <aside className="sidebar">
            <DecisionPanel
              decision={activeDecision}
              isLoading={replay.isDecisionLoading}
              isReplayMode={replay.isReplayMode}
              selectedMove={replay.selectedMove}
            />

            <div className="sidebar-section">
              <h3 className="sidebar-section-title">Match Config</h3>
              <div className="config-summary">
                <div className="config-row">
                  <span className="config-player-mark mark-x">X</span>
                  <span className="config-agent-name">
                    {formatAgentName(game.players['X'] || 'human')}
                  </span>
                </div>
                <div className="config-row">
                  <span className="config-player-mark mark-o">O</span>
                  <span className="config-agent-name">
                    {formatAgentName(game.players['O'] || 'alphabeta')}
                  </span>
                </div>
              </div>
              <button
                className="config-new-game-btn"
                onClick={game.resetGame}
              >
                New Game
              </button>
            </div>
          </aside>
        </main>
      )}

      {game.error && hasGame && (
        <div className="error-toast">
          {game.error}
          <button className="error-toast-dismiss" onClick={game.clearError}>
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
