/**
 * useGame — game lifecycle state machine.
 *
 * Manages: game creation, state, action submission, replay data,
 * and the latest agent decision (for live play display).
 *
 * After each state change (create or submit), automatically fetches
 * the replay to find and display the most recent agent decision.
 */

import { useCallback, useState } from 'react';
import * as api from '../api/client';
import type {
  DecisionResponse,
  GameStateResponse,
  ReplayResponse,
} from '../types/api';

export interface UseGameReturn {
  gameState: GameStateResponse | null;
  players: Record<string, string>;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  replayData: ReplayResponse | null;
  latestDecision: DecisionResponse | null;
  createGame: (players: Record<string, string>) => Promise<void>;
  submitAction: (action: [number, number]) => Promise<void>;
  resetGame: () => void;
  clearError: () => void;
}

export function useGame(): UseGameReturn {
  const [gameState, setGameState] = useState<GameStateResponse | null>(null);
  const [players, setPlayers] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [replayData, setReplayData] = useState<ReplayResponse | null>(null);
  const [latestDecision, setLatestDecision] =
    useState<DecisionResponse | null>(null);

  /**
   * After any game state change, fetch the replay and find the
   * most recent agent decision to display in the inspector.
   */
  const refreshReplayAndDecision = useCallback(
    async (sessionId: string) => {
      try {
        const replay = await api.getReplay(sessionId);
        setReplayData(replay);

        // Find the latest move with a decision_id (agent move)
        const latestAgentMove = [...replay.moves]
          .reverse()
          .find((m) => m.decision_id !== null);

        if (latestAgentMove?.decision_id) {
          const decision = await api.getDecision(
            sessionId,
            latestAgentMove.decision_id,
          );
          setLatestDecision(decision);
        } else {
          setLatestDecision(null);
        }
      } catch {
        // Replay/decision fetch failure is non-critical.
        // Game remains playable even if telemetry is unavailable.
      }
    },
    [],
  );

  const createGame = useCallback(
    async (playerConfig: Record<string, string>) => {
      setIsLoading(true);
      setError(null);
      setLatestDecision(null);
      setReplayData(null);

      try {
        const state = await api.createGame(playerConfig);
        setGameState(state);
        setPlayers(playerConfig);
        await refreshReplayAndDecision(state.session_id);
      } catch (e) {
        setError(
          e instanceof Error ? e.message : 'Failed to create game',
        );
      } finally {
        setIsLoading(false);
      }
    },
    [refreshReplayAndDecision],
  );

  const submitAction = useCallback(
    async (action: [number, number]) => {
      if (!gameState) return;
      setIsSubmitting(true);
      setError(null);

      try {
        const state = await api.submitAction(gameState.session_id, action);
        setGameState(state);
        await refreshReplayAndDecision(state.session_id);
      } catch (e) {
        setError(
          e instanceof Error ? e.message : 'Invalid action',
        );
      } finally {
        setIsSubmitting(false);
      }
    },
    [gameState, refreshReplayAndDecision],
  );

  const resetGame = useCallback(() => {
    setGameState(null);
    setPlayers({});
    setReplayData(null);
    setLatestDecision(null);
    setError(null);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return {
    gameState,
    players,
    isLoading,
    isSubmitting,
    error,
    replayData,
    latestDecision,
    createGame,
    submitAction,
    resetGame,
    clearError,
  };
}
