import { useState } from 'react';
import { AGENT_LABELS, AGENT_TYPES, type AgentType } from '../../features/tic-tac-toe/types';
import './NewGameForm.css';

interface NewGameFormProps {
  onCreateGame: (players: Record<string, string>) => void;
  isLoading: boolean;
  error?: string | null;
  compact?: boolean;
}

export function NewGameForm({
  onCreateGame,
  isLoading,
  error,
  compact = false,
}: NewGameFormProps) {
  const [playerX, setPlayerX] = useState<AgentType>('human');
  const [playerO, setPlayerO] = useState<AgentType>('alphabeta');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCreateGame({ X: playerX, O: playerO });
  };

  return (
    <form
      className={`new-game-form ${compact ? 'compact' : ''}`}
      onSubmit={handleSubmit}
    >
      {!compact && (
        <div className="form-header">
          <h2 className="form-title">Configure Match</h2>
          <p className="form-subtitle">
            Choose agents for each player and observe how they think.
          </p>
        </div>
      )}

      <div className="player-selectors">
        <PlayerSelector
          label="X"
          value={playerX}
          onChange={setPlayerX}
          id="player-x-select"
        />
        <PlayerSelector
          label="O"
          value={playerO}
          onChange={setPlayerO}
          id="player-o-select"
        />
      </div>

      {error && <p className="form-error">{error}</p>}

      <button
        type="submit"
        className="start-button"
        disabled={isLoading}
      >
        {isLoading ? 'Creating…' : compact ? 'New Game' : 'Start Match'}
      </button>
    </form>
  );
}

function PlayerSelector({
  label,
  value,
  onChange,
  id,
}: {
  label: string;
  value: AgentType;
  onChange: (val: AgentType) => void;
  id: string;
}) {
  return (
    <div className="player-selector">
      <label className="player-label" htmlFor={id}>
        <span className={`player-mark ${label === 'X' ? 'mark-x' : 'mark-o'}`}>
          {label}
        </span>
      </label>
      <select
        id={id}
        className="player-select"
        value={value}
        onChange={(e) => onChange(e.target.value as AgentType)}
      >
        {AGENT_TYPES.map((agent) => (
          <option key={agent} value={agent}>
            {AGENT_LABELS[agent]}
          </option>
        ))}
      </select>
    </div>
  );
}
