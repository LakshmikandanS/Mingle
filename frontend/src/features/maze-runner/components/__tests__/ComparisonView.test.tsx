import '@testing-library/jest-dom/vitest';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ComparisonView } from '../ComparisonView';

describe('ComparisonView', () => {
  const mockComparison = {
    player_metrics: {
      total_actions: 10,
      valid_actions: 10,
      invalid_actions: 0,
      path_length: 10,
      path_cost: 10,
      unique_states: 11,
      revisited_states: 0,
      hints_used: 0,
      hint_points_spent: 0,
      total_duration_ms: 5000,
    },
    search_stats: {
      path_found: true,
      path_length: 8,
      path_cost: 8,
      nodes_expanded: 20,
      nodes_discovered: 30,
      max_frontier_size: 5,
      execution_time_ms: 10,
    },
    path_length_delta: 2,
    path_cost_delta: 2,
  };

  const mockInsight = {
    state: [0, 1] as [number, number],
    insight: {
      discovered: true,
      expanded: false,
      closed: false,
      cost: 5,
      depth: 5,
    },
  };

  it('renders loading state', () => {
    render(
      <ComparisonView comparison={null} intermediateInsight={null} algorithm="astar" isLoading={true} />
    );
    expect(screen.getByText('Loading comparison…')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(
      <ComparisonView comparison={null} intermediateInsight={null} algorithm="astar" isLoading={false} />
    );
    expect(screen.getByText('Run a search to compare with your play.')).toBeInTheDocument();
  });

  it('renders full comparison with metrics and deltas', () => {
    render(
      <ComparisonView comparison={mockComparison as any} intermediateInsight={null} algorithm="astar" isLoading={false} />
    );
    
    expect(screen.getByText('Player')).toBeInTheDocument();
    expect(screen.getByText('A*')).toBeInTheDocument(); // mapped from 'astar'
    
    // Check deltas
    expect(screen.getAllByText('+2')).toHaveLength(2);
  });

  it('renders intermediate insight correctly', () => {
    render(
      <ComparisonView comparison={null} intermediateInsight={mockInsight as any} algorithm="bfs" isLoading={false} />
    );
    
    expect(screen.getByText('BFS at your position:')).toBeInTheDocument();
    expect(screen.getByText('Discovered')).toBeInTheDocument();
    expect(screen.getByText('Expanded')).toBeInTheDocument();
    expect(screen.getByText('g(n) = 5')).toBeInTheDocument();
  });
});
