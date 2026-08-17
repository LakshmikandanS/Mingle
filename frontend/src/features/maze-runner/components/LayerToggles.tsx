import type { BoardLayer } from '../types';
import './LayerToggles.css';

interface LayerTogglesProps {
  layers: Record<BoardLayer, boolean>;
  onToggle: (layer: BoardLayer) => void;
}

const LAYER_INFO: { key: BoardLayer; label: string; icon: string }[] = [
  { key: 'playerPath', label: 'Player Path', icon: '●' },
  { key: 'algorithmPath', label: 'Algorithm Path', icon: '◆' },
  { key: 'searchTrace', label: 'Search Trace', icon: '◇' },
  { key: 'frontier', label: 'Frontier', icon: '◎' },
  { key: 'expanded', label: 'Expanded', icon: '◈' },
];

export function LayerToggles({ layers, onToggle }: LayerTogglesProps) {
  return (
    <div className="layer-toggles">
      <span className="layer-toggles-label">Layers</span>
      <div className="layer-chips">
        {LAYER_INFO.map(({ key, label, icon }) => (
          <button
            key={key}
            className={`layer-chip ${layers[key] ? 'active' : ''}`}
            onClick={() => onToggle(key)}
            aria-pressed={layers[key]}
            aria-label={`Toggle ${label}`}
          >
            <span className="layer-chip-icon">{icon}</span>
            <span className="layer-chip-label">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
