import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MazeBoard } from '../MazeBoard';
import type { MazeCellResponse } from '../../../../types/maze';

const createCell = (row: number, col: number, kind: string = 'FREE', terrain_cost: number = 1): MazeCellResponse => ({
  row,
  col,
  kind,
  terrain_cost,
});

describe('MazeBoard', () => {
  const defaultLayers = {
    playerPath: true,
    algorithmPath: true,
    searchTrace: true,
    frontier: true,
    expanded: true,
  };

  const simpleGrid = [
    [createCell(0, 0, 'START'), createCell(0, 1)],
    [createCell(1, 0, 'OBSTACLE'), createCell(1, 1, 'GOAL')],
  ];

  it('renders grid with correct dimensions', () => {
    const { container } = render(
      <MazeBoard
        cells={simpleGrid}
        rows={2}
        columns={2}
        layers={defaultLayers}
      />
    );
    const grid = container.querySelector('.maze-board') as HTMLElement;
    expect(grid).toBeInTheDocument();
    expect(grid.style.gridTemplateColumns).toBe('repeat(2, 1fr)');
    expect(grid.style.gridTemplateRows).toBe('repeat(2, 1fr)');
  });

  it('renders start and goal cells', () => {
    const { container } = render(
      <MazeBoard
        cells={simpleGrid}
        rows={2}
        columns={2}
        layers={defaultLayers}
      />
    );
    expect(container.querySelector('.kind-START')).toBeInTheDocument();
    expect(container.querySelector('.kind-GOAL')).toBeInTheDocument();
    expect(container.querySelector('.kind-OBSTACLE')).toBeInTheDocument();
  });

  it('renders player overlay correctly', () => {
    const { container } = render(
      <MazeBoard
        cells={simpleGrid}
        rows={2}
        columns={2}
        layers={defaultLayers}
        playerState={[0, 1]}
      />
    );
    const playerCell = container.querySelector('.overlay-player');
    expect(playerCell).toBeInTheDocument();
  });

  it('handles click-to-move for adjacent cells', () => {
    const onClick = vi.fn();
    const { container } = render(
      <MazeBoard
        cells={simpleGrid}
        rows={2}
        columns={2}
        layers={defaultLayers}
        playerState={[0, 0]}
        onCellClick={onClick}
      />
    );
    
    // [0, 1] is adjacent to player at [0, 0]
    const cells = container.querySelectorAll('.maze-cell');
    fireEvent.click(cells[1]); // The cell at (0,1)
    
    expect(onClick).toHaveBeenCalledWith(0, 1);
  });

  it('ignores clicks on non-adjacent cells', () => {
    const onClick = vi.fn();
    const { container } = render(
      <MazeBoard
        cells={simpleGrid}
        rows={2}
        columns={2}
        layers={defaultLayers}
        playerState={[0, 0]}
        onCellClick={onClick}
      />
    );
    
    const cells = container.querySelectorAll('.maze-cell');
    fireEvent.click(cells[3]); // The cell at (1,1) is diagonal (not adjacent)
    
    // onClick logic is in MazeBoard which sets isClickable.
    // Wait, isClickable adds onClick only if true. Let's check if the mock was called.
    expect(onClick).not.toHaveBeenCalled();
  });

  it('renders search trace overlays when enabled', () => {
    const events: any[] = [
      { event_type: 'NODE_DISCOVERED', state: [0, 1] },
      { event_type: 'NODE_EXPANDED', state: [0, 1] },
    ];
    
    const { container, rerender } = render(
      <MazeBoard
        cells={simpleGrid}
        rows={2}
        columns={2}
        layers={defaultLayers}
        searchEvents={events}
        currentSearchEventIndex={1}
      />
    );
    expect(container.querySelector('.overlay-search-expanded')).toBeInTheDocument();
    expect(container.querySelector('.overlay-search-current')).toBeInTheDocument(); // Node expanded is current
    
    // Disable expanded layer
    rerender(
      <MazeBoard
        cells={simpleGrid}
        rows={2}
        columns={2}
        layers={{ ...defaultLayers, expanded: false }}
        searchEvents={events}
        currentSearchEventIndex={1}
      />
    );
    expect(container.querySelector('.overlay-search-expanded')).not.toBeInTheDocument();
  });
});
