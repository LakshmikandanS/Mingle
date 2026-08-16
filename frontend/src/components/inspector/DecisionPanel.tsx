import { formatAgentName } from '../../features/tic-tac-toe/mapping';
import type { DecisionResponse, MoveRecord } from '../../types/api';
import './DecisionPanel.css';

interface DecisionPanelProps {
  decision: DecisionResponse | null;
  isLoading: boolean;
  isReplayMode: boolean;
  selectedMove: MoveRecord | null;
}

export function DecisionPanel({
  decision,
  isLoading,
  isReplayMode,
  selectedMove,
}: DecisionPanelProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="decision-panel">
        <h3 className="panel-title">Decision Inspector</h3>
        <div className="panel-loading">
          <span className="loading-text">Loading decision…</span>
        </div>
      </div>
    );
  }

  // Replay: human move selected (no decision)
  if (isReplayMode && selectedMove && !selectedMove.decision_id) {
    return (
      <div className="decision-panel">
        <h3 className="panel-title">Decision Inspector</h3>
        <div className="panel-empty">
          <p className="empty-text">
            Human move — no agent decision to inspect.
          </p>
        </div>
      </div>
    );
  }

  // No decision available
  if (!decision) {
    return (
      <div className="decision-panel">
        <h3 className="panel-title">Decision Inspector</h3>
        <div className="panel-empty">
          <p className="empty-text">No agent decision selected.</p>
          <p className="empty-hint">
            Play a game or select an agent move from the replay timeline
            to inspect its decision.
          </p>
        </div>
      </div>
    );
  }

  // Decision telemetry
  const { metrics } = decision;
  const hasSearchMetrics =
    metrics.nodes_explored > 0 ||
    metrics.max_depth > 0 ||
    metrics.branches_considered > 0;

  return (
    <div className="decision-panel has-decision">
      <h3 className="panel-title">Decision Inspector</h3>

      <div className="decision-header">
        <span className="decision-agent-badge">
          {formatAgentName(decision.agent)}
        </span>
        <span className="decision-player" data-player={decision.player}>
          {decision.player}
        </span>
      </div>

      <div className="decision-metrics">
        <MetricItem
          label="Chosen move"
          value={`[${decision.chosen_action[0]}, ${decision.chosen_action[1]}]`}
          mono
        />
        <MetricItem
          label="Decision time"
          value={`${decision.duration_ms.toFixed(2)} ms`}
        />

        {hasSearchMetrics && (
          <>
            <div className="metrics-divider" />
            <MetricItem
              label="Nodes explored"
              value={metrics.nodes_explored.toLocaleString()}
            />
            <MetricItem
              label="Terminal nodes"
              value={metrics.terminal_nodes.toLocaleString()}
            />
            <MetricItem
              label="Max depth"
              value={metrics.max_depth.toString()}
            />
            <MetricItem
              label="Branches"
              value={metrics.branches_considered.toLocaleString()}
            />
            {metrics.pruning_cutoffs > 0 && (
              <MetricItem
                label="Pruning cutoffs"
                value={metrics.pruning_cutoffs.toLocaleString()}
              />
            )}
            <MetricItem
              label="Deep copies"
              value={metrics.deep_copies.toLocaleString()}
            />
          </>
        )}
      </div>
    </div>
  );
}

function MetricItem({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="metric-item">
      <span className="metric-label">{label}</span>
      <span className={`metric-value ${mono ? 'mono' : ''}`}>{value}</span>
    </div>
  );
}
