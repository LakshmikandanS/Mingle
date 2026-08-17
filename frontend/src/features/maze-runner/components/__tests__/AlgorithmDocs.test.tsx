import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AlgorithmDocs } from '../AlgorithmDocs';
import type { AlgorithmDocumentationResponse } from '../../../../types/maze';

describe('AlgorithmDocs', () => {
  const mockDoc: AlgorithmDocumentationResponse = {
    algorithm: 'astar',
    name: 'A* Search',
    category: 'INFORMED',
    description: 'A* finds the shortest path using a heuristic.',
    core_idea: 'f(n) = g(n) + h(n)',
    pseudocode: ['while frontier is not empty:', '  pop node with lowest f'],
    data_structure: 'Priority Queue',
    completeness: 'Yes, if branching factor is finite.',
    optimality: 'Yes, if heuristic is admissible.',
    time_complexity: 'O(b^d)',
    space_complexity: 'O(b^d)',
    heuristic_requirements: 'Must be admissible.',
    weighted_cost_requirements: 'Handles non-negative weights.',
    step_by_step: ['Start at root', 'Evaluate neighbors'],
    implementation_notes: 'Implemented in maze_runner.py'
  };

  it('renders loading state', () => {
    const { container } = render(
      <AlgorithmDocs documentation={null} isLoading={true} onClose={vi.fn()} />
    );
    expect(screen.getByText('Loading documentation…')).toBeInTheDocument();
  });

  it('returns null if no doc and not loading', () => {
    const { container } = render(
      <AlgorithmDocs documentation={null} isLoading={false} onClose={vi.fn()} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders documentation completely', () => {
    render(<AlgorithmDocs documentation={mockDoc} isLoading={false} onClose={vi.fn()} />);
    
    expect(screen.getByText('A* Search')).toBeInTheDocument();
    expect(screen.getByText('INFORMED')).toBeInTheDocument(); // category formatted
    expect(screen.getByText('A* finds the shortest path using a heuristic.')).toBeInTheDocument();
    
    // Properties
    expect(screen.getByText('Priority Queue')).toBeInTheDocument();
    expect(screen.getByText('Yes, if heuristic is admissible.')).toBeInTheDocument();
    expect(screen.getAllByText('O(b^d)')).toHaveLength(2);
    
    // Pseudocode
    expect(screen.getByText(/while frontier is not empty:/)).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    render(<AlgorithmDocs documentation={mockDoc} isLoading={false} onClose={onClose} />);
    
    const closeBtn = screen.getByLabelText('Close');
    fireEvent.click(closeBtn);
    expect(onClose).toHaveBeenCalled();
  });

  it('calls onClose when overlay background is clicked', () => {
    const onClose = vi.fn();
    const { container } = render(<AlgorithmDocs documentation={mockDoc} isLoading={false} onClose={onClose} />);
    
    // The overlay is the first element
    fireEvent.click(container.firstChild as Element);
    expect(onClose).toHaveBeenCalled();
  });

  it('does not call onClose when panel content is clicked', () => {
    const onClose = vi.fn();
    const { container } = render(<AlgorithmDocs documentation={mockDoc} isLoading={false} onClose={onClose} />);
    
    const panel = container.querySelector('.algo-docs-panel');
    fireEvent.click(panel as Element);
    expect(onClose).not.toHaveBeenCalled();
  });
});
