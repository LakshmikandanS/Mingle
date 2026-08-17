import type { AlgorithmSummary } from '../../../types/maze';
import { formatAlgorithmName, formatCategory } from '../mapping';
import './AlgorithmSelector.css';

interface AlgorithmSelectorProps {
  available: AlgorithmSummary[];
  planned: AlgorithmSummary[];
  selected: string;
  onSelect: (algorithm: string) => void;
  disabled?: boolean;
}

export function AlgorithmSelector({
  available,
  planned,
  selected,
  onSelect,
  disabled = false,
}: AlgorithmSelectorProps) {
  const categories = available.reduce<Record<string, AlgorithmSummary[]>>((acc, alg) => {
    const cat = alg.category;
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(alg);
    return acc;
  }, {});

  return (
    <div className="algorithm-selector">
      <h4 className="algo-selector-title">Algorithm</h4>
      <div className="algo-groups">
        {Object.entries(categories).map(([cat, algs]) => (
          <div key={cat} className="algo-group">
            <span className="algo-group-label">{formatCategory(cat)}</span>
            <div className="algo-chips">
              {algs.map((alg) => (
                <button
                  key={alg.algorithm}
                  className={`algo-chip ${selected === alg.algorithm ? 'selected' : ''}`}
                  onClick={() => onSelect(alg.algorithm)}
                  disabled={disabled}
                >
                  {formatAlgorithmName(alg.algorithm)}
                </button>
              ))}
            </div>
          </div>
        ))}
        {planned.length > 0 && (
          <div className="algo-group">
            <span className="algo-group-label">Coming Soon</span>
            <div className="algo-chips">
              {planned.map((alg) => (
                <span key={alg.algorithm} className="algo-chip planned">
                  {alg.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
