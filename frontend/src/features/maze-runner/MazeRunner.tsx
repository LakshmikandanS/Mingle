/**
 * MazeRunner — top-level orchestrator component.
 *
 * Manages mode transitions: config → play|watch → result.
 * Composes all sub-components and hooks.
 * Keeps Environment, PlayerRun, SearchRun, Hint, and Comparison state separate.
 */

import { useCallback, useEffect, useState } from 'react';
import type { MazeAction, MazeEnvironmentRequest, HintLevel } from '../../types/maze';
import type { BoardLayer, MazeMode } from './types';
import { DEFAULT_LAYERS } from './types';
import { formatAlgorithmName } from './mapping';

import { useAlgorithms } from './hooks/useAlgorithms';
import { useMazeEnvironment } from './hooks/useMazeEnvironment';
import { usePlayerRun } from './hooks/usePlayerRun';
import { useSearchReplay } from './hooks/useSearchReplay';
import { useHints } from './hooks/useHints';
import { useComparison } from './hooks/useComparison';

import { MazeConfigForm } from './components/MazeConfigForm';
import { MazeBoard } from './components/MazeBoard';
import { MazeStatus } from './components/MazeStatus';
import { PlayerControls } from './components/PlayerControls';
import { SearchReplayControls } from './components/SearchReplayControls';
import { AlgorithmSelector } from './components/AlgorithmSelector';
import { AlgorithmDocs } from './components/AlgorithmDocs';
import { LayerToggles } from './components/LayerToggles';
import { HintPanel } from './components/HintPanel';
import { MazeInspector } from './components/MazeInspector';
import { ComparisonView } from './components/ComparisonView';
import { ResultScreen } from './components/ResultScreen';

import './MazeRunner.css';

interface MazeRunnerProps {
  onBack: () => void;
}

export function MazeRunner({ onBack }: MazeRunnerProps) {
  const [mode, setMode] = useState<MazeMode>('config');
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('astar');
  const [layers, setLayers] = useState<Record<BoardLayer, boolean>>(DEFAULT_LAYERS);
  const [showGiveUpConfirm, setShowGiveUpConfirm] = useState(false);
  const [showDocs, setShowDocs] = useState(false);
  const [showHintPanel, setShowHintPanel] = useState(false);
  const [sidebarTab, setSidebarTab] = useState<'inspector' | 'hints' | 'comparison'>('inspector');

  const algorithms = useAlgorithms();
  const environment = useMazeEnvironment();
  const playerRun = usePlayerRun();
  const searchReplay = useSearchReplay();
  const hints = useHints();
  const comparison = useComparison();

  // Set default algorithm when list loads
  useEffect(() => {
    if (algorithms.available.length > 0 && !algorithms.available.find((a) => a.algorithm === selectedAlgorithm)) {
      setSelectedAlgorithm(algorithms.available[0].algorithm);
    }
  }, [algorithms.available, selectedAlgorithm]);

  // Keyboard controls for player mode
  useEffect(() => {
    if (mode !== 'play' || !playerRun.playerRun || playerRun.playerRun.status !== 'IN_PROGRESS') return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const actionMap: Record<string, MazeAction> = {
        ArrowUp: 'UP',
        ArrowDown: 'DOWN',
        ArrowLeft: 'LEFT',
        ArrowRight: 'RIGHT',
        w: 'UP',
        s: 'DOWN',
        a: 'LEFT',
        d: 'RIGHT',
      };
      const action = actionMap[e.key];
      if (action && !playerRun.isMoving) {
        e.preventDefault();
        playerRun.move(action);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mode, playerRun]);

  // Transition to result when player run finishes
  useEffect(() => {
    if (
      mode === 'play' &&
      playerRun.playerRun &&
      (playerRun.playerRun.status === 'COMPLETED' || playerRun.playerRun.status === 'ABANDONED')
    ) {
      setMode('result');
    }
  }, [mode, playerRun.playerRun?.status]);

  // Fetch intermediate comparison when player moves
  useEffect(() => {
    if (
      mode === 'play' &&
      playerRun.playerRun &&
      searchReplay.searchRun &&
      playerRun.playerRun.status === 'IN_PROGRESS'
    ) {
      comparison.fetchInsight(
        playerRun.playerRun.run_id,
        searchReplay.searchRun.run_id,
      );
    }
  }, [mode, playerRun.playerRun?.current_state, searchReplay.searchRun?.run_id]);

  // Handle environment generation
  const handleGenerate = useCallback(async (
    config: MazeEnvironmentRequest,
    algorithm: string,
    selectedMode: 'play' | 'watch',
  ) => {
    const env = await environment.createEnvironment(config);
    if (!env) return;

    setSelectedAlgorithm(algorithm);

    if (selectedMode === 'play') {
      const run = await playerRun.startRun(env.environment_id);
      if (!run) return;
      // Also run search for comparison/hints
      await searchReplay.startSearch(env.environment_id, algorithm);
      setLayers({ ...DEFAULT_LAYERS, searchTrace: false, frontier: false, expanded: false });
      setMode('play');
    } else {
      const searchRun = await searchReplay.startSearch(env.environment_id, algorithm);
      if (!searchRun) return;
      setLayers({ ...DEFAULT_LAYERS, searchTrace: true, frontier: true, expanded: true });
      setMode('watch');
    }
  }, [environment, playerRun, searchReplay]);

  // Give up flow
  const handleRequestGiveUp = useCallback(() => setShowGiveUpConfirm(true), []);
  const handleCancelGiveUp = useCallback(() => setShowGiveUpConfirm(false), []);
  const handleConfirmGiveUp = useCallback(async () => {
    setShowGiveUpConfirm(false);
    await playerRun.giveUp();
  }, [playerRun]);

  // Hint request
  const handleRequestHint = useCallback(async (level: HintLevel) => {
    if (!playerRun.playerRun) return;
    await hints.requestHint(
      playerRun.playerRun.run_id,
      level,
      selectedAlgorithm,
      searchReplay.searchRun?.run_id,
    );
  }, [playerRun.playerRun, selectedAlgorithm, searchReplay.searchRun, hints]);

  // Cell click (move to adjacent cell)
  const handleCellClick = useCallback((row: number, col: number) => {
    if (mode !== 'play' || !playerRun.playerRun) return;
    playerRun.moveToCell(playerRun.playerRun.current_state, row, col);
  }, [mode, playerRun]);

  // Layer toggle
  const handleLayerToggle = useCallback((layer: BoardLayer) => {
    setLayers((prev) => ({ ...prev, [layer]: !prev[layer] }));
  }, []);

  // Algorithm info
  const handleShowDocs = useCallback(async () => {
    await algorithms.fetchDocumentation(selectedAlgorithm);
    setShowDocs(true);
  }, [selectedAlgorithm, algorithms]);

  // View replay from result
  const handleViewReplay = useCallback(() => {
    setLayers({ ...DEFAULT_LAYERS, searchTrace: true, frontier: true, expanded: true });
    searchReplay.resetReplay();
    setMode('watch');
  }, [searchReplay]);

  // Compare from result
  const handleCompare = useCallback(async () => {
    if (playerRun.playerRun && searchReplay.searchRun) {
      await comparison.compare(
        playerRun.playerRun.run_id,
        searchReplay.searchRun.run_id,
      );
      setSidebarTab('comparison');
    }
  }, [playerRun.playerRun, searchReplay.searchRun, comparison]);

  // Try again
  const handleTryAgain = useCallback(() => {
    playerRun.reset();
    searchReplay.reset();
    hints.reset();
    comparison.reset();
    environment.reset();
    setMode('config');
    setShowGiveUpConfirm(false);
    setShowDocs(false);
    setShowHintPanel(false);
  }, [playerRun, searchReplay, hints, comparison, environment]);

  // Switch algorithm in watch mode
  const handleAlgorithmSwitch = useCallback(async (alg: string) => {
    setSelectedAlgorithm(alg);
    if (mode === 'watch' && environment.environment) {
      searchReplay.reset();
      await searchReplay.startSearch(environment.environment.environment_id, alg);
    }
  }, [mode, environment.environment, searchReplay]);

  // ── Render ──────────────────────────────────────────────

  if (mode === 'config') {
    return (
      <div className="maze-runner-config">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <MazeConfigForm
          algorithms={algorithms.available}
          plannedAlgorithms={algorithms.planned}
          isLoading={environment.isLoading || algorithms.isLoading}
          error={environment.error || algorithms.error}
          onGenerate={handleGenerate}
        />
      </div>
    );
  }

  const env = environment.environment;
  if (!env) return null;

  const isRunFinished = playerRun.playerRun
    ? playerRun.playerRun.status === 'COMPLETED' || playerRun.playerRun.status === 'ABANDONED'
    : false;

  // Derive hint visualization data
  const hintTarget = hints.currentHint?.suggested_state ?? null;
  const hintPath = hints.currentHint?.route ?? hints.currentHint?.partial_path ?? null;
  const shouldShowHints = mode === 'play' && showHintPanel;

  return (
    <div className="maze-runner-layout">
      {/* Algorithm docs overlay */}
      {showDocs && (
        <AlgorithmDocs
          documentation={algorithms.documentation}
          isLoading={algorithms.isDocLoading}
          onClose={() => { setShowDocs(false); algorithms.clearDocumentation(); }}
        />
      )}

      {/* Main area */}
      <div className="maze-main">
        <div className="maze-main-header">
          <button className="back-btn" onClick={mode === 'result' ? handleTryAgain : onBack}>
            ← {mode === 'result' ? 'New Game' : 'Back'}
          </button>
          <MazeStatus
            mode={mode}
            playerRun={playerRun.playerRun}
            elapsedMs={playerRun.elapsedMs}
            searchAlgorithm={formatAlgorithmName(selectedAlgorithm)}
            replayProgress={
              mode === 'watch'
                ? `${Math.max(0, searchReplay.currentEventIndex + 1)} / ${searchReplay.totalEvents}`
                : undefined
            }
          />
          <button className="algo-info-btn" onClick={handleShowDocs} title="Algorithm info">
            ?
          </button>
        </div>

        <MazeBoard
          cells={env.cells}
          rows={env.rows}
          columns={env.columns}
          playerState={playerRun.playerRun?.current_state}
          playerTrajectory={playerRun.playerRun?.trajectory}
          searchEvents={searchReplay.events}
          searchPath={searchReplay.searchRun?.path}
          currentSearchEventIndex={searchReplay.currentEventIndex}
          hintTarget={hintTarget}
          hintPath={hintPath}
          layers={layers}
          onCellClick={mode === 'play' ? handleCellClick : undefined}
          disabled={mode !== 'play' || isRunFinished}
        />

        <LayerToggles layers={layers} onToggle={handleLayerToggle} />

        {/* Player controls */}
        {mode === 'play' && !isRunFinished && (
          <PlayerControls
            onMove={playerRun.move}
            onGiveUp={playerRun.giveUp}
            disabled={playerRun.isMoving || isRunFinished}
            showGiveUpConfirm={showGiveUpConfirm}
            onConfirmGiveUp={handleConfirmGiveUp}
            onCancelGiveUp={handleCancelGiveUp}
            onRequestGiveUp={handleRequestGiveUp}
            onHint={() => { setShowHintPanel(true); setSidebarTab('hints'); }}
          />
        )}

        {/* Watch mode controls */}
        {mode === 'watch' && (
          <SearchReplayControls
            currentIndex={searchReplay.currentEventIndex}
            totalEvents={searchReplay.totalEvents}
            isPlaying={searchReplay.isPlaying}
            speed={searchReplay.speed}
            onPlay={searchReplay.play}
            onPause={searchReplay.pause}
            onStep={searchReplay.step}
            onStepBack={searchReplay.stepBack}
            onReset={searchReplay.resetReplay}
            onSetSpeed={searchReplay.setSpeed}
          />
        )}

        {/* Errors */}
        {(playerRun.error || searchReplay.error || hints.error) && (
          <div className="maze-error">
            {playerRun.error || searchReplay.error || hints.error}
          </div>
        )}
      </div>

      {/* Sidebar */}
      <div className="maze-sidebar">
        {/* Sidebar tabs */}
        <div className="sidebar-tabs">
          <button
            className={`sidebar-tab ${sidebarTab === 'inspector' ? 'active' : ''}`}
            onClick={() => setSidebarTab('inspector')}
          >
            Inspector
          </button>
          {shouldShowHints && (
            <button
              className={`sidebar-tab ${sidebarTab === 'hints' ? 'active' : ''}`}
              onClick={() => setSidebarTab('hints')}
            >
              Hints
            </button>
          )}
          <button
            className={`sidebar-tab ${sidebarTab === 'comparison' ? 'active' : ''}`}
            onClick={() => {
              setSidebarTab('comparison');
              if (!comparison.comparison && playerRun.playerRun && searchReplay.searchRun) {
                comparison.compare(playerRun.playerRun.run_id, searchReplay.searchRun.run_id);
              }
            }}
          >
            Compare
          </button>
        </div>

        {/* Watch mode: algorithm selector */}
        {mode === 'watch' && (
          <AlgorithmSelector
            available={algorithms.available}
            planned={algorithms.planned}
            selected={selectedAlgorithm}
            onSelect={handleAlgorithmSwitch}
            disabled={searchReplay.isLoading}
          />
        )}

        {/* Sidebar content */}
        <div className="sidebar-content">
          {sidebarTab === 'inspector' && (
            <MazeInspector
              playerRun={playerRun.playerRun}
              searchRun={searchReplay.searchRun}
              elapsedMs={playerRun.elapsedMs}
            />
          )}

          {sidebarTab === 'hints' && shouldShowHints && (
            <HintPanel
              currentHint={hints.currentHint}
              hintHistory={hints.hintHistory}
              totalPointsSpent={hints.totalPointsSpent}
              hintCosts={hints.hintCosts?.costs ?? null}
              selectedAlgorithm={selectedAlgorithm}
              isRequesting={hints.isRequesting}
              disabled={isRunFinished}
              onRequestHint={handleRequestHint}
              onClearHint={hints.clearHint}
            />
          )}

          {sidebarTab === 'comparison' && (
            <ComparisonView
              comparison={comparison.comparison}
              intermediateInsight={comparison.intermediateInsight}
              algorithm={selectedAlgorithm}
              isLoading={comparison.isLoading}
            />
          )}
        </div>

        {/* Result screen */}
        {mode === 'result' && playerRun.playerRun && (
          <ResultScreen
            playerRun={playerRun.playerRun}
            searchRun={searchReplay.searchRun}
            algorithm={selectedAlgorithm}
            onViewReplay={handleViewReplay}
            onCompare={handleCompare}
            onAlgorithmInfo={handleShowDocs}
            onTryAgain={handleTryAgain}
          />
        )}
      </div>
    </div>
  );
}
