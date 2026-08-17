/**
 * usePlayerRun — manages player run lifecycle.
 *
 * Creates a run, handles movement, give-up, and tracks elapsed time.
 * All movement is backend-authoritative: UI sends actions and reflects state.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import * as mazeApi from '../../../api/mazeClient';
import type {
  MazeAction,
  MazeState,
  PlayerRunResponse,
} from '../../../types/maze';

export interface UsePlayerRunReturn {
  playerRun: PlayerRunResponse | null;
  isMoving: boolean;
  error: string | null;
  elapsedMs: number;
  startRun: (environmentId: string) => Promise<PlayerRunResponse | null>;
  move: (action: MazeAction) => Promise<void>;
  moveToCell: (fromState: MazeState, row: number, col: number) => Promise<void>;
  giveUp: () => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

export function usePlayerRun(): UsePlayerRunReturn {
  const [playerRun, setPlayerRun] = useState<PlayerRunResponse | null>(null);
  const [isMoving, setIsMoving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [elapsedMs, setElapsedMs] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number | null>(null);

  // Elapsed timer
  useEffect(() => {
    if (playerRun && playerRun.status === 'IN_PROGRESS') {
      startTimeRef.current = Date.now();
      timerRef.current = setInterval(() => {
        if (startTimeRef.current) {
          setElapsedMs(Date.now() - startTimeRef.current);
        }
      }, 100);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [playerRun?.status]);

  const startRun = useCallback(async (environmentId: string): Promise<PlayerRunResponse | null> => {
    setError(null);
    setElapsedMs(0);
    try {
      const run = await mazeApi.createPlayerRun(environmentId);
      setPlayerRun(run);
      return run;
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to start player run';
      setError(msg);
      return null;
    }
  }, []);

  const move = useCallback(async (action: MazeAction) => {
    if (!playerRun || playerRun.status !== 'IN_PROGRESS') return;
    setIsMoving(true);
    setError(null);
    try {
      const result = await mazeApi.movePlayer(playerRun.run_id, action);
      // Update player run with action response data
      setPlayerRun((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          current_state: result.current_state,
          status: result.status,
          completed: result.completed,
          metrics: result.metrics,
          trajectory: result.trajectory,
          legal_actions: prev.legal_actions, // Will be refreshed
        };
      });
      // Refresh full state to get legal_actions
      const refreshed = await mazeApi.getPlayerRun(playerRun.run_id);
      setPlayerRun(refreshed);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Move failed');
    } finally {
      setIsMoving(false);
    }
  }, [playerRun]);

  const moveToCell = useCallback(async (fromState: MazeState, row: number, col: number) => {
    const dr = row - fromState[0];
    const dc = col - fromState[1];
    let action: MazeAction | null = null;
    if (dr === -1 && dc === 0) action = 'UP';
    else if (dr === 1 && dc === 0) action = 'DOWN';
    else if (dr === 0 && dc === -1) action = 'LEFT';
    else if (dr === 0 && dc === 1) action = 'RIGHT';
    if (action) {
      await move(action);
    }
  }, [move]);

  const giveUp = useCallback(async () => {
    if (!playerRun || playerRun.status !== 'IN_PROGRESS') return;
    setError(null);
    try {
      const updated = await mazeApi.giveUpPlayerRun(playerRun.run_id);
      setPlayerRun(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to give up');
    }
  }, [playerRun]);

  const clearError = useCallback(() => setError(null), []);

  const reset = useCallback(() => {
    setPlayerRun(null);
    setError(null);
    setElapsedMs(0);
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  return {
    playerRun,
    isMoving,
    error,
    elapsedMs,
    startRun,
    move,
    moveToCell,
    giveUp,
    clearError,
    reset,
  };
}
