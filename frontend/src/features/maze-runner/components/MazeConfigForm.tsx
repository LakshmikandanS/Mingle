import { useEffect, useState } from 'react';
import type { AlgorithmSummary } from '../../../types/maze';
import type { MazeEnvironmentRequest } from '../../../types/maze';
import { formatAlgorithmName, formatCategory } from '../mapping';
import type { GenerationStrategy } from '../types';
import { GENERATION_STRATEGIES } from '../types';
import './MazeConfigForm.css';

interface MazeConfigFormProps {
  algorithms: AlgorithmSummary[];
  plannedAlgorithms: AlgorithmSummary[];
  isLoading: boolean;
  error?: string | null;
  onGenerate: (config: MazeEnvironmentRequest, algorithm: string, mode: 'play' | 'watch') => void;
}

export function MazeConfigForm({
  algorithms,
  plannedAlgorithms,
  isLoading,
  error,
  onGenerate,
}: MazeConfigFormProps) {
  const [width, setWidth] = useState(10);
  const [height, setHeight] = useState(10);
  const [strategy, setStrategy] = useState<GenerationStrategy>('random');
  const [obstacleProbability, setObstacleProbability] = useState(0.25);
  const [seed, setSeed] = useState('');
  const [algorithm, setAlgorithm] = useState(algorithms[0]?.algorithm ?? 'astar');
  const [mode, setMode] = useState<'play' | 'watch'>('play');

  useEffect(() => {
    if (algorithms.length > 0 && !algorithms.some((alg) => alg.algorithm === algorithm)) {
      setAlgorithm(algorithms[0].algorithm);
    }
  }, [algorithms, algorithm]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const config: MazeEnvironmentRequest = {
      width,
      height,
      generation_strategy: strategy,
      obstacle_probability: strategy === 'random' ? obstacleProbability : undefined,
      seed: seed ? Number(seed) : undefined,
      ensure_solvable: true,
    };
    onGenerate(config, algorithm, mode);
  };

  // Group algorithms by category
  const categories = algorithms.reduce<Record<string, AlgorithmSummary[]>>((acc, alg) => {
    const cat = alg.category;
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(alg);
    return acc;
  }, {});

  return (
    <form className="maze-config-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <h2 className="form-title">Maze Runner</h2>
        <p className="form-subtitle">
          Configure a grid environment, then solve it yourself or watch an AI algorithm.
        </p>
      </div>

      {/* Grid size */}
      <div className="config-group">
        <span className="config-group-label">Grid Size</span>
        <div className="config-row-inputs">
          <label className="config-field">
            <span className="config-field-label">Width</span>
            <input
              type="number"
              className="config-input"
              value={width}
              onChange={(e) => setWidth(Math.max(2, Math.min(30, Number(e.target.value))))}
              min={2}
              max={30}
              id="maze-config-width"
            />
          </label>
          <span className="config-separator">×</span>
          <label className="config-field">
            <span className="config-field-label">Height</span>
            <input
              type="number"
              className="config-input"
              value={height}
              onChange={(e) => setHeight(Math.max(2, Math.min(30, Number(e.target.value))))}
              min={2}
              max={30}
              id="maze-config-height"
            />
          </label>
        </div>
      </div>

      {/* Generation strategy */}
      <div className="config-group">
        <label className="config-group-label" htmlFor="maze-config-strategy">
          Generation
        </label>
        <select
          id="maze-config-strategy"
          className="config-select"
          value={strategy}
          onChange={(e) => setStrategy(e.target.value as GenerationStrategy)}
        >
          {GENERATION_STRATEGIES.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      </div>

      {/* Obstacle probability (random only) */}
      {strategy === 'random' && (
        <div className="config-group">
          <label className="config-group-label" htmlFor="maze-config-obstacles">
            Obstacle Density — {Math.round(obstacleProbability * 100)}%
          </label>
          <input
            type="range"
            id="maze-config-obstacles"
            className="config-slider"
            min={0}
            max={0.5}
            step={0.05}
            value={obstacleProbability}
            onChange={(e) => setObstacleProbability(Number(e.target.value))}
          />
        </div>
      )}

      {/* Seed */}
      <div className="config-group">
        <label className="config-group-label" htmlFor="maze-config-seed">
          Seed <span className="config-optional">(optional)</span>
        </label>
        <input
          type="number"
          id="maze-config-seed"
          className="config-input"
          value={seed}
          onChange={(e) => setSeed(e.target.value)}
          placeholder="Random"
        />
      </div>

      {/* Algorithm selection */}
      <div className="config-group">
        <span className="config-group-label">Algorithm</span>
        <div className="algorithm-grid">
          {Object.entries(categories).map(([cat, algs]) => (
            <div key={cat} className="algorithm-category">
              <span className="algorithm-category-label">{formatCategory(cat)}</span>
              {algs.map((alg) => (
                <button
                  key={alg.algorithm}
                  type="button"
                  className={`algorithm-chip ${algorithm === alg.algorithm ? 'selected' : ''}`}
                  onClick={() => setAlgorithm(alg.algorithm)}
                >
                  {formatAlgorithmName(alg.algorithm)}
                </button>
              ))}
            </div>
          ))}
          {plannedAlgorithms.length > 0 && (
            <div className="algorithm-category">
              <span className="algorithm-category-label">Coming Soon</span>
              {plannedAlgorithms.map((alg) => (
                <span key={alg.algorithm} className="algorithm-chip disabled">
                  {alg.name}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Mode selection */}
      <div className="config-group">
        <span className="config-group-label">Mode</span>
        <div className="mode-selector">
          <button
            type="button"
            className={`mode-btn ${mode === 'play' ? 'active' : ''}`}
            onClick={() => setMode('play')}
          >
            <span className="mode-icon">🎮</span>
            <span className="mode-label">Play</span>
            <span className="mode-desc">Solve it yourself</span>
          </button>
          <button
            type="button"
            className={`mode-btn ${mode === 'watch' ? 'active' : ''}`}
            onClick={() => setMode('watch')}
          >
            <span className="mode-icon">👁</span>
            <span className="mode-label">Watch Agent</span>
            <span className="mode-desc">Observe the algorithm</span>
          </button>
        </div>
      </div>

      {error && <p className="form-error">{error}</p>}

      <button type="submit" className="start-button" disabled={isLoading}>
        {isLoading ? 'Generating…' : 'Generate Environment'}
      </button>
    </form>
  );
}
