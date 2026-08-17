import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SearchReplayControls } from '../SearchReplayControls';
import { REPLAY_SPEEDS } from '../../types';

describe('SearchReplayControls', () => {
  const defaultProps = {
    currentIndex: 0,
    totalEvents: 10,
    isPlaying: false,
    speed: 1 as const,
    onPlay: vi.fn(),
    onPause: vi.fn(),
    onStep: vi.fn(),
    onStepBack: vi.fn(),
    onReset: vi.fn(),
    onSetSpeed: vi.fn(),
  };

  it('renders progress correctly', () => {
    render(<SearchReplayControls {...defaultProps} currentIndex={4} />);
    expect(screen.getByText('5 / 10')).toBeInTheDocument();
  });

  it('calls onPlay when play button is clicked', () => {
    render(<SearchReplayControls {...defaultProps} />);
    const playBtn = screen.getByLabelText('Play');
    fireEvent.click(playBtn);
    expect(defaultProps.onPlay).toHaveBeenCalled();
  });

  it('shows pause button when playing and calls onPause when clicked', () => {
    render(<SearchReplayControls {...defaultProps} isPlaying={true} />);
    const pauseBtn = screen.getByLabelText('Pause');
    expect(pauseBtn).toBeInTheDocument();
    expect(screen.queryByLabelText('Play')).not.toBeInTheDocument();
    
    fireEvent.click(pauseBtn);
    expect(defaultProps.onPause).toHaveBeenCalled();
  });

  it('disables play/step forward at end of trace', () => {
    render(<SearchReplayControls {...defaultProps} currentIndex={9} />);
    const playBtn = screen.getByLabelText('Play');
    const stepBtn = screen.getByLabelText('Step forward');
    
    expect(playBtn).toBeDisabled();
    expect(stepBtn).toBeDisabled();
  });

  it('disables reset/step back at start of trace', () => {
    render(<SearchReplayControls {...defaultProps} currentIndex={-1} />);
    const resetBtn = screen.getByLabelText('Reset');
    const backBtn = screen.getByLabelText('Step back');
    
    expect(resetBtn).toBeDisabled();
    expect(backBtn).toBeDisabled();
  });

  it('calls onSetSpeed when speed chip is clicked', () => {
    render(<SearchReplayControls {...defaultProps} />);
    const speedBtn = screen.getByLabelText(`Speed 2x`);
    fireEvent.click(speedBtn);
    expect(defaultProps.onSetSpeed).toHaveBeenCalledWith(2);
  });
});
