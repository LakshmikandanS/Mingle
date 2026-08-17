import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { HintPanel } from '../HintPanel';
import type { HintResponse } from '../../../../types/maze';

describe('HintPanel', () => {
  const defaultProps = {
    currentHint: null,
    hintHistory: [],
    totalPointsSpent: 0,
    hintCosts: {
      astar: { NEXT_ACTION: 10, NEXT_STATE: 15, PARTIAL_ROUTE: 20, FULL_SOLUTION: 50 },
    },
    selectedAlgorithm: 'astar',
    isRequesting: false,
    disabled: false,
    onRequestHint: vi.fn(),
    onClearHint: vi.fn(),
  };

  it('renders correctly with costs', () => {
    render(<HintPanel {...defaultProps} />);
    expect(screen.getByText('Source:')).toBeInTheDocument();
    expect(screen.getByText('A*')).toBeInTheDocument();
    
    // Costs should be displayed
    expect(screen.getByText('−10 pts')).toBeInTheDocument();
    expect(screen.getByText('−50 pts')).toBeInTheDocument();
  });

  it('calls onRequestHint with correct level', () => {
    render(<HintPanel {...defaultProps} />);
    const buttons = screen.getAllByRole('button');
    // First hint level is Next Action
    fireEvent.click(buttons[0]);
    expect(defaultProps.onRequestHint).toHaveBeenCalledWith('NEXT_ACTION');
  });

  it('disables buttons when requesting or disabled', () => {
    const { rerender } = render(<HintPanel {...defaultProps} isRequesting={true} />);
    const buttons = screen.getAllByRole('button');
    buttons.forEach((btn) => {
      // Except history toggle (if history exists, but it doesn't here)
      expect(btn).toBeDisabled();
    });

    rerender(<HintPanel {...defaultProps} isRequesting={false} disabled={true} />);
    screen.getAllByRole('button').forEach((btn) => {
      expect(btn).toBeDisabled();
    });
  });

  it('displays current hint suggestion', () => {
    const hint = {
      available: true,
      suggested_action: 'UP' as const,
      cost: 10,
      level: 'NEXT_ACTION' as const,
      algorithm: 'astar',
    } as Partial<HintResponse> as HintResponse;
    
    render(<HintPanel {...defaultProps} currentHint={hint} />);
    expect(screen.getByText('Suggested move:')).toBeInTheDocument();
    // actionArrow('UP') -> '↑'
    expect(screen.getByText('↑')).toBeInTheDocument();
  });

  it('handles unavailable hints', () => {
    const hint = {
      available: false,
      reason: 'No path found',
      cost: 0,
      level: 'NEXT_ACTION' as const,
      algorithm: 'astar',
    } as Partial<HintResponse> as HintResponse;
    
    render(<HintPanel {...defaultProps} currentHint={hint} />);
    expect(screen.getByText('No path found')).toBeInTheDocument();
  });

  it('shows hint history cumulatively', () => {
    const history = [
      { available: true, cost: 10, level: 'NEXT_ACTION' as const, algorithm: 'astar' },
      { available: true, cost: 20, level: 'PARTIAL_ROUTE' as const, algorithm: 'astar' },
    ] as Partial<HintResponse>[] as HintResponse[];
    
    render(<HintPanel {...defaultProps} hintHistory={history} totalPointsSpent={30} />);
    expect(screen.getByText('Points spent:')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
    
    const toggle = screen.getByText('History (2)');
    fireEvent.click(toggle);
    
    expect(screen.getByText('Direction')).toBeInTheDocument();
    expect(screen.getByText('Partial Route')).toBeInTheDocument();
    expect(screen.getByText('−10')).toBeInTheDocument();
    expect(screen.getByText('−20')).toBeInTheDocument();
  });
});
