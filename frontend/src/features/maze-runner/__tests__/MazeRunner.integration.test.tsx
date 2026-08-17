import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { MazeRunner } from '../MazeRunner';
import * as mazeApi from '../../../api/mazeClient';
import type { MazeEnvironmentResponse } from '../../../types/maze';

// Mock the API calls
vi.mock('../../../api/mazeClient', () => ({
  getHintCosts: vi.fn().mockResolvedValue({ costs: {} }),
  listAlgorithms: vi.fn().mockResolvedValue({ available: [{ algorithm: 'bfs', name: 'BFS', category: 'UNINFORMED' }], planned: [] }),
  createEnvironment: vi.fn(),
  createPlayerRun: vi.fn(),
  createSearchRun: vi.fn(),
  getSearchTrace: vi.fn().mockResolvedValue({ events: [] }),
}));

describe('MazeRunner Integration', () => {
  const onBack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('starts in config mode and loads algorithms', async () => {
    await act(async () => {
      render(<MazeRunner onBack={onBack} />);
    });
    
    // Should show config form
    expect(screen.getByText('Maze Runner')).toBeInTheDocument();
    expect(screen.getByText('Configure a grid environment, then solve it yourself or watch an AI algorithm.')).toBeInTheDocument();
    
    // Should fetch algorithms
    await waitFor(() => {
      expect(mazeApi.listAlgorithms).toHaveBeenCalled();
    });
  });

  it('transitions to play mode when generated with manual solve', async () => {
    const mockEnv: MazeEnvironmentResponse = {
      environment_id: 'env-1',
      rows: 5,
      columns: 5,
      cells: [],
    };
    
    const mockPlayerRun = {
      run_id: 'run-1',
      environment_id: 'env-1',
      status: 'IN_PROGRESS',
      current_state: [0, 0],
      legal_actions: ['RIGHT', 'DOWN'],
      trajectory: [[0, 0]],
      metrics: { total_actions: 0 },
    };

    const mockSearchRun = {
      run_id: 'search-1',
      environment_id: 'env-1',
      algorithm: 'bfs',
      search_status: 'COMPLETED',
      path: [],
      statistics: {
        nodes_expanded: 0,
        nodes_discovered: 0,
        path_length: 0,
        path_cost: 0,
        execution_time_ms: 0,
        max_frontier_size: 0,
      },
      trace_metadata: {},
    };

    vi.mocked(mazeApi.createEnvironment).mockResolvedValue(mockEnv as any);
    vi.mocked(mazeApi.createPlayerRun).mockResolvedValue(mockPlayerRun as any);
    vi.mocked(mazeApi.createSearchRun).mockResolvedValue(mockSearchRun as any);

    await act(async () => {
      render(<MazeRunner onBack={onBack} />);
    });
    
    // Select Play mode (should be active by default but we click anyway just to be sure)
    const playBtn = screen.getByText('Play');
    await act(async () => {
      fireEvent.click(playBtn);
    });

    // Click generate
    const generateBtn = screen.getByText('Generate Environment');
    await act(async () => {
      fireEvent.click(generateBtn);
    });

    await waitFor(() => {
      expect(mazeApi.createEnvironment).toHaveBeenCalled();
      expect(mazeApi.createPlayerRun).toHaveBeenCalledWith('env-1');
      expect(mazeApi.createSearchRun).toHaveBeenCalledWith('env-1', 'bfs');
    });
    
    // Should show play mode UI
    expect(screen.getByText('PLAY')).toBeInTheDocument(); // Mode badge
    expect(screen.getByText('Give Up')).toBeInTheDocument();
  });

  it('transitions to watch mode when generated with watch agent', async () => {
    const mockEnv: MazeEnvironmentResponse = {
      environment_id: 'env-2',
      rows: 5,
      columns: 5,
      cells: [],
    };

    const mockSearchRun = {
      run_id: 'search-2',
      environment_id: 'env-2',
      algorithm: 'bfs',
      search_status: 'COMPLETED',
      path: [],
      statistics: {
        nodes_expanded: 0,
        nodes_discovered: 0,
        path_length: 0,
        path_cost: 0,
        execution_time_ms: 0,
        max_frontier_size: 0,
      },
      trace_metadata: {},
    };

    vi.mocked(mazeApi.createEnvironment).mockResolvedValue(mockEnv as any);
    vi.mocked(mazeApi.createSearchRun).mockResolvedValue(mockSearchRun as any);

    await act(async () => {
      render(<MazeRunner onBack={onBack} />);
    });
    
    // Select watch mode
    const watchBtn = screen.getByText('Watch Agent');
    await act(async () => {
      fireEvent.click(watchBtn);
    });

    // Click generate
    const generateBtn = screen.getByText('Generate Environment');
    await act(async () => {
      fireEvent.click(generateBtn);
    });

    await waitFor(() => {
      expect(mazeApi.createEnvironment).toHaveBeenCalled();
      expect(mazeApi.createSearchRun).toHaveBeenCalledWith('env-2', 'bfs');
      expect(mazeApi.createPlayerRun).not.toHaveBeenCalled();
    });
      
    // Should show watch mode UI
    expect(screen.getByText('WATCH')).toBeInTheDocument(); // Mode badge
  });
});
