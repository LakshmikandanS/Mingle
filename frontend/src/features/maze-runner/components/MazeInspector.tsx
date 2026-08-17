import type { PlayerRunResponse, SearchRunResponse } from '../../../types/maze';
import { formatDuration, formatState, formatAlgorithmName } from '../mapping';
import './MazeInspector.css';

interface MazeInspectorProps {
  playerRun: PlayerRunResponse | null;
  searchRun: SearchRunResponse | null;
  elapsedMs?: number;
}

export function MazeInspector({ playerRun, searchRun, elapsedMs }: MazeInspectorProps) {
  return (
    <div className="maze-inspector sidebar-section">
      <h3 className="sidebar-section-title">Inspector</h3>

      {/* Run info */}
      {playerRun && (
        <div className="inspector-group">
          <span className="inspector-group-label">Run</span>
          <InspectorItem label="Run ID" value={playerRun.run_id.slice(0, 8)} mono />
          <InspectorItem label="Environment" value={playerRun.environment_id.slice(0, 8)} mono />
          <InspectorItem label="Status" value={playerRun.status} />
          <InspectorItem label="Duration" value={formatDuration(elapsedMs ?? playerRun.metrics.total_duration_ms)} />
        </div>
      )}

      {/* Player telemetry */}
      {playerRun && (
        <div className="inspector-group">
          <span className="inspector-group-label">Player</span>
          <InspectorItem label="Position" value={formatState(playerRun.current_state)} mono />
          <InspectorItem label="Total actions" value={String(playerRun.metrics.total_actions)} />
          <InspectorItem label="Valid" value={String(playerRun.metrics.valid_actions)} />
          <InspectorItem label="Invalid" value={String(playerRun.metrics.invalid_actions)} />
          <InspectorItem label="Path length" value={String(playerRun.metrics.path_length)} />
          <InspectorItem label="Path cost" value={String(playerRun.metrics.path_cost)} />
          <InspectorItem label="Unique states" value={String(playerRun.metrics.unique_states)} />
          <InspectorItem label="Revisited" value={String(playerRun.metrics.revisited_states)} />
          <InspectorItem label="Hints used" value={String(playerRun.metrics.hints_used)} />
          <InspectorItem label="Hint points" value={String(playerRun.metrics.hint_points_spent)} />
        </div>
      )}

      {/* Search telemetry */}
      {searchRun && (
        <div className="inspector-group">
          <span className="inspector-group-label">Search</span>
          <InspectorItem label="Algorithm" value={formatAlgorithmName(searchRun.algorithm)} />
          <InspectorItem label="Status" value={searchRun.search_status} />
          <InspectorItem label="Path found" value={searchRun.statistics.path_found ? 'Yes' : 'No'} />
          <InspectorItem label="Path length" value={String(searchRun.statistics.path_length)} />
          <InspectorItem label="Path cost" value={String(searchRun.statistics.path_cost)} />
          <InspectorItem label="Nodes expanded" value={searchRun.statistics.nodes_expanded?.toLocaleString() ?? '0'} />
          <InspectorItem label="Nodes discovered" value={searchRun.statistics.nodes_discovered?.toLocaleString() ?? '0'} />
          <InspectorItem label="Max frontier" value={String(searchRun.statistics.max_frontier_size)} />
          <InspectorItem label="Execution time" value={formatDuration(searchRun.statistics.execution_time_ms)} />
          <InspectorItem label="Trace events" value={String(searchRun.trace_metadata.event_count)} />
        </div>
      )}

      {/* Empty state */}
      {!playerRun && !searchRun && (
        <div className="inspector-empty">
          <p className="inspector-empty-text">Start a run to see telemetry.</p>
        </div>
      )}
    </div>
  );
}

function InspectorItem({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="inspector-item">
      <span className="inspector-item-label">{label}</span>
      <span className={`inspector-item-value ${mono ? 'mono' : ''}`}>{value}</span>
    </div>
  );
}
