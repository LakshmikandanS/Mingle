import type { PlayerRunResponse, SearchRunResponse } from '../../../types/maze';
import { formatAlgorithmName, formatDuration, formatRunStatus } from '../mapping';
import './ResultScreen.css';

interface ResultScreenProps {
  playerRun: PlayerRunResponse;
  searchRun: SearchRunResponse | null;
  algorithm: string;
  onViewReplay: () => void;
  onCompare: () => void;
  onAlgorithmInfo: () => void;
  onTryAgain: () => void;
}

export function ResultScreen({
  playerRun,
  searchRun,
  algorithm,
  onViewReplay,
  onCompare,
  onAlgorithmInfo,
  onTryAgain,
}: ResultScreenProps) {
  const isCompleted = playerRun.status === 'COMPLETED';
  const m = playerRun.metrics;

  return (
    <div className="result-screen">
      {/* Result badge */}
      <div className="result-badge-container">
        <span className={`result-main-badge ${isCompleted ? 'completed' : 'abandoned'}`}>
          {formatRunStatus(playerRun.status)}
        </span>
      </div>

      {/* Player performance */}
      <div className="result-section">
        <h3 className="result-section-title">Player Performance</h3>
        <div className="result-metrics">
          <ResultMetric label="Path length" value={String(m.path_length)} />
          <ResultMetric label="Path cost" value={String(m.path_cost)} />
          <ResultMetric label="Actions" value={String(m.total_actions)} />
          <ResultMetric label="Invalid moves" value={String(m.invalid_actions)} />
          <ResultMetric label="Time" value={formatDuration(m.total_duration_ms)} />
          <ResultMetric label="Hints used" value={String(m.hints_used)} />
          <ResultMetric label="Hint points" value={String(m.hint_points_spent)} />
        </div>
      </div>

      {/* Algorithm performance */}
      {searchRun && (
        <div className="result-section">
          <h3 className="result-section-title">
            {formatAlgorithmName(algorithm)} Performance
          </h3>
          <div className="result-metrics">
            <ResultMetric label="Path length" value={String(searchRun.statistics.path_length)} />
            <ResultMetric label="Path cost" value={String(searchRun.statistics.path_cost)} />
            <ResultMetric label="Nodes expanded" value={searchRun.statistics.nodes_expanded.toLocaleString()} />
            <ResultMetric label="Nodes discovered" value={searchRun.statistics.nodes_discovered.toLocaleString()} />
            <ResultMetric label="Execution time" value={formatDuration(searchRun.statistics.execution_time_ms)} />
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="result-actions">
        {searchRun && (
          <button className="result-action-btn" onClick={onViewReplay}>
            ▶ View Replay
          </button>
        )}
        {searchRun && (
          <button className="result-action-btn" onClick={onCompare}>
            ⚖ Compare
          </button>
        )}
        <button className="result-action-btn" onClick={onAlgorithmInfo}>
          ? Algorithm Info
        </button>
        <button className="result-action-btn result-action-primary" onClick={onTryAgain}>
          ↻ Try Again
        </button>
      </div>
    </div>
  );
}

function ResultMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="result-metric">
      <span className="result-metric-label">{label}</span>
      <span className="result-metric-value">{value}</span>
    </div>
  );
}
