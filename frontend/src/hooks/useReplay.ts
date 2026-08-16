/**
 * useReplay — replay timeline state and decision fetching.
 *
 * Manages move selection, historical board state, and fetching
 * decision telemetry for selected agent moves. Keeps replay
 * state completely separate from the live game.
 */

import { useCallback, useEffect, useState } from 'react';
import * as api from '../api/client';
import type { DecisionResponse, MoveRecord, ReplayResponse } from '../types/api';

export interface UseReplayReturn {
  isReplayMode: boolean;
  selectedMoveIndex: number | null;
  selectedMove: MoveRecord | null;
  selectedBoardState: string[][] | null;
  selectedDecision: DecisionResponse | null;
  isDecisionLoading: boolean;
  moves: MoveRecord[];
  selectMove: (index: number) => void;
  exitReplay: () => void;
  goNext: () => void;
  goPrev: () => void;
}

export function useReplay(
  sessionId: string | undefined,
  replayData: ReplayResponse | null,
): UseReplayReturn {
  const [selectedMoveIndex, setSelectedMoveIndex] = useState<number | null>(
    null,
  );
  const [selectedDecision, setSelectedDecision] =
    useState<DecisionResponse | null>(null);
  const [isDecisionLoading, setIsDecisionLoading] = useState(false);

  const moves = replayData?.moves ?? [];
  const isReplayMode = selectedMoveIndex !== null;

  const selectedMove =
    isReplayMode && replayData
      ? replayData.moves[selectedMoveIndex] ?? null
      : null;

  const selectedBoardState = selectedMove
    ? selectedMove.resulting_state.board
    : null;

  /**
   * When replay data changes (new game or new move), exit replay mode.
   * This prevents stale replay selection after the live game advances.
   */
  useEffect(() => {
    setSelectedMoveIndex(null);
    setSelectedDecision(null);
  }, [replayData]);

  const selectMove = useCallback(
    async (index: number) => {
      if (!replayData || !sessionId) return;
      const move = replayData.moves[index];
      if (!move) return;

      setSelectedMoveIndex(index);

      if (move.decision_id) {
        setIsDecisionLoading(true);
        try {
          const decision = await api.getDecision(sessionId, move.decision_id);
          setSelectedDecision(decision);
        } catch {
          setSelectedDecision(null);
        } finally {
          setIsDecisionLoading(false);
        }
      } else {
        // Human move — no agent decision to fetch
        setSelectedDecision(null);
      }
    },
    [replayData, sessionId],
  );

  const exitReplay = useCallback(() => {
    setSelectedMoveIndex(null);
    setSelectedDecision(null);
  }, []);

  const goNext = useCallback(() => {
    if (selectedMoveIndex !== null && selectedMoveIndex < moves.length - 1) {
      selectMove(selectedMoveIndex + 1);
    }
  }, [selectedMoveIndex, moves.length, selectMove]);

  const goPrev = useCallback(() => {
    if (selectedMoveIndex !== null && selectedMoveIndex > 0) {
      selectMove(selectedMoveIndex - 1);
    }
  }, [selectedMoveIndex, selectMove]);

  return {
    isReplayMode,
    selectedMoveIndex,
    selectedMove,
    selectedBoardState,
    selectedDecision,
    isDecisionLoading,
    moves,
    selectMove,
    exitReplay,
    goNext,
    goPrev,
  };
}
