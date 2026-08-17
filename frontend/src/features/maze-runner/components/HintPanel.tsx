import { useState } from 'react';
import type { HintLevel, HintResponse } from '../../../types/maze';
import { formatAlgorithmName, formatHintLevel, actionArrow } from '../mapping';
import { HINT_LEVEL_INFO } from '../types';
import './HintPanel.css';

interface HintPanelProps {
  currentHint: HintResponse | null;
  hintHistory: HintResponse[];
  totalPointsSpent: number;
  hintCosts: Record<string, Partial<Record<HintLevel, number>>> | null;
  selectedAlgorithm: string;
  isRequesting: boolean;
  disabled: boolean;
  onRequestHint: (level: HintLevel) => void;
  onClearHint: () => void;
}

export function HintPanel({
  currentHint,
  hintHistory,
  totalPointsSpent,
  hintCosts,
  selectedAlgorithm,
  isRequesting,
  disabled,
  onRequestHint,
  onClearHint,
}: HintPanelProps) {
  const [showHistory, setShowHistory] = useState(false);

  const algCosts = hintCosts?.[selectedAlgorithm];

  return (
    <div className="hint-panel sidebar-section">
      <h3 className="sidebar-section-title">Hints</h3>

      <div className="hint-algo-info">
        <span className="hint-algo-label">Source:</span>
        <span className="hint-algo-name">{formatAlgorithmName(selectedAlgorithm)}</span>
      </div>

      <div className="hint-points">
        <span className="hint-points-label">Points spent:</span>
        <span className="hint-points-value">{totalPointsSpent}</span>
      </div>

      {/* Hint level buttons */}
      <div className="hint-levels">
        {HINT_LEVEL_INFO.map((info) => {
          const cost = algCosts?.[info.value];
          return (
            <button
              key={info.value}
              className="hint-level-btn"
              onClick={() => onRequestHint(info.value)}
              disabled={disabled || isRequesting}
            >
              <span className="hint-level-name">
                Lv.{info.level} — {info.label}
              </span>
              <span className="hint-level-desc">{info.description}</span>
              {cost !== undefined && (
                <span className="hint-level-cost">−{cost} pts</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Current hint display */}
      {currentHint && (
        <div className="hint-result">
          {currentHint.available ? (
            <>
              {currentHint.suggested_action && (
                <div className="hint-suggestion">
                  <span className="hint-suggestion-label">Suggested move:</span>
                  <span className="hint-suggestion-arrow">
                    {actionArrow(currentHint.suggested_action)}
                  </span>
                </div>
              )}
              {currentHint.suggested_state && !currentHint.suggested_action && (
                <div className="hint-suggestion">
                  <span className="hint-suggestion-label">Go to:</span>
                  <span className="hint-suggestion-state">
                    [{currentHint.suggested_state[0]}, {currentHint.suggested_state[1]}]
                  </span>
                </div>
              )}
              {currentHint.route && currentHint.route.length > 0 && (
                <div className="hint-suggestion">
                  <span className="hint-suggestion-label">Route shown on board</span>
                  <span className="hint-route-length">{currentHint.route.length} cells</span>
                </div>
              )}
            </>
          ) : (
            <div className="hint-unavailable">
              <span className="hint-unavailable-text">{currentHint.reason || 'Hint unavailable'}</span>
            </div>
          )}
          <button className="hint-dismiss-btn" onClick={onClearHint}>Dismiss</button>
        </div>
      )}

      {/* Hint history toggle */}
      {hintHistory.length > 0 && (
        <div className="hint-history-section">
          <button
            className="hint-history-toggle"
            onClick={() => setShowHistory(!showHistory)}
          >
            History ({hintHistory.length})
            <span className="hint-history-arrow">{showHistory ? '▾' : '▸'}</span>
          </button>
          {showHistory && (
            <div className="hint-history-list">
              {hintHistory.map((hint, i) => (
                <div key={hint.hint_id || i} className="hint-history-item">
                  <span className="hint-history-algo">
                    {formatAlgorithmName(hint.algorithm)}
                  </span>
                  <span className="hint-history-level">
                    {formatHintLevel(hint.level)}
                  </span>
                  <span className="hint-history-cost">−{hint.cost}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
