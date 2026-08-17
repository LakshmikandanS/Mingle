import type { ComparisonResponse, IntermediateComparisonResponse } from '../../../types/maze';
import { formatAlgorithmName, formatDuration } from '../mapping';
import './ComparisonView.css';

interface ComparisonViewProps {
  comparison: ComparisonResponse | null;
  intermediateInsight: IntermediateComparisonResponse | null;
  algorithm: string;
  isLoading: boolean;
}

export function ComparisonView({
  comparison,
  intermediateInsight,
  algorithm,
  isLoading,
}: ComparisonViewProps) {
  if (isLoading) {
    return (
      <div className="comparison-view sidebar-section">
        <h3 className="sidebar-section-title">Comparison</h3>
        <div className="comparison-loading">Loading comparison…</div>
      </div>
    );
  }

  return (
    <div className="comparison-view sidebar-section">
      <h3 className="sidebar-section-title">Comparison</h3>

      {/* Intermediate insight */}
      {intermediateInsight && (
        <div className="comparison-insight">
          <span className="insight-label">
            {formatAlgorithmName(algorithm)} at your position:
          </span>
          <div className="insight-grid">
            <InsightBadge
              label="Discovered"
              value={intermediateInsight.insight.discovered}
            />
            <InsightBadge
              label="Expanded"
              value={intermediateInsight.insight.expanded}
            />
            <InsightBadge
              label="Closed"
              value={intermediateInsight.insight.closed}
            />
          </div>
          {intermediateInsight.insight.cost !== null && (
            <div className="insight-costs">
              <span className="insight-cost-item">
                g(n) = {intermediateInsight.insight.cost}
              </span>
              {intermediateInsight.insight.depth !== null && (
                <span className="insight-cost-item">
                  depth = {intermediateInsight.insight.depth}
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Full comparison */}
      {comparison && (
        <div className="comparison-columns">
          <div className="comparison-column">
            <span className="comparison-column-label">Player</span>
            <ComparisonMetric
              label="Path length"
              value={comparison.player_metrics.path_length}
            />
            <ComparisonMetric
              label="Path cost"
              value={comparison.player_metrics.path_cost}
            />
            <ComparisonMetric
              label="Actions"
              value={comparison.player_metrics.total_actions}
            />
            <ComparisonMetric
              label="Invalid"
              value={comparison.player_metrics.invalid_actions}
            />
            <ComparisonMetric
              label="Hints"
              value={comparison.player_metrics.hints_used}
            />
            <ComparisonMetric
              label="Hint pts"
              value={comparison.player_metrics.hint_points_spent}
            />
            <ComparisonMetric
              label="Time"
              value={formatDuration(comparison.player_metrics.total_duration_ms)}
              isText
            />
          </div>
          <div className="comparison-column">
            <span className="comparison-column-label">
              {formatAlgorithmName(algorithm)}
            </span>
            <ComparisonMetric
              label="Path length"
              value={comparison.search_stats.path_length}
            />
            <ComparisonMetric
              label="Path cost"
              value={comparison.search_stats.path_cost}
            />
            <ComparisonMetric
              label="Expanded"
              value={comparison.search_stats.nodes_expanded}
            />
            <ComparisonMetric
              label="Discovered"
              value={comparison.search_stats.nodes_discovered}
            />
            <ComparisonMetric
              label="Time"
              value={formatDuration(comparison.search_stats.execution_time_ms)}
              isText
            />
          </div>
        </div>
      )}

      {/* Deltas */}
      {comparison && (
        <div className="comparison-deltas">
          {comparison.path_length_delta !== null && (
            <DeltaIndicator label="Path length" delta={comparison.path_length_delta} />
          )}
          {comparison.path_cost_delta !== null && (
            <DeltaIndicator label="Path cost" delta={comparison.path_cost_delta} />
          )}
        </div>
      )}

      {!comparison && !intermediateInsight && (
        <p className="comparison-empty">
          Run a search to compare with your play.
        </p>
      )}
    </div>
  );
}

function InsightBadge({ label, value }: { label: string; value: boolean }) {
  return (
    <div className={`insight-badge ${value ? 'yes' : 'no'}`}>
      <span className="insight-badge-indicator">{value ? '✓' : '✗'}</span>
      <span className="insight-badge-label">{label}</span>
    </div>
  );
}

function ComparisonMetric({
  label,
  value,
  isText = false,
}: {
  label: string;
  value: number | string;
  isText?: boolean;
}) {
  return (
    <div className="comparison-metric">
      <span className="comparison-metric-label">{label}</span>
      <span className="comparison-metric-value">
        {isText ? value : typeof value === 'number' ? value.toLocaleString() : value}
      </span>
    </div>
  );
}

function DeltaIndicator({ label, delta }: { label: string; delta: number }) {
  const isWorse = delta > 0;
  const isBetter = delta < 0;
  return (
    <div className="delta-indicator">
      <span className="delta-label">{label}</span>
      <span className={`delta-value ${isBetter ? 'better' : ''} ${isWorse ? 'worse' : ''}`}>
        {delta > 0 ? '+' : ''}{delta}
      </span>
    </div>
  );
}
