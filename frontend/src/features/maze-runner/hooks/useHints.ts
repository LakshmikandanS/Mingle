/**
 * useHints — manages hint requests and history.
 *
 * Backend is authoritative for hint accounting.
 * No frontend-created hint budget.
 */

import { useCallback, useEffect, useState } from 'react';
import * as mazeApi from '../../../api/mazeClient';
import type {
  HintCostsResponse,
  HintLevel,
  HintResponse,
} from '../../../types/maze';

export interface UseHintsReturn {
  currentHint: HintResponse | null;
  hintHistory: HintResponse[];
  hintCosts: HintCostsResponse | null;
  totalPointsSpent: number;
  isRequesting: boolean;
  error: string | null;
  requestHint: (
    runId: string,
    level: HintLevel,
    algorithm: string,
    searchRunId?: string,
  ) => Promise<void>;
  clearHint: () => void;
  reset: () => void;
}

export function useHints(): UseHintsReturn {
  const [currentHint, setCurrentHint] = useState<HintResponse | null>(null);
  const [hintHistory, setHintHistory] = useState<HintResponse[]>([]);
  const [hintCosts, setHintCosts] = useState<HintCostsResponse | null>(null);
  const [isRequesting, setIsRequesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch hint costs on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const costs = await mazeApi.getHintCosts();
        if (!cancelled) setHintCosts(costs);
      } catch {
        // Non-critical — hints still work without cost preview
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const totalPointsSpent = hintHistory.reduce((sum, h) => sum + h.cost, 0);

  const requestHint = useCallback(async (
    runId: string,
    level: HintLevel,
    algorithm: string,
    searchRunId?: string,
  ) => {
    setIsRequesting(true);
    setError(null);
    try {
      const hint = await mazeApi.requestHint(runId, level, algorithm, searchRunId);
      setCurrentHint(hint);
      setHintHistory((prev) => [...prev, hint]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Hint request failed');
    } finally {
      setIsRequesting(false);
    }
  }, []);

  const clearHint = useCallback(() => {
    setCurrentHint(null);
  }, []);

  const reset = useCallback(() => {
    setCurrentHint(null);
    setHintHistory([]);
    setError(null);
  }, []);

  return {
    currentHint,
    hintHistory,
    hintCosts,
    totalPointsSpent,
    isRequesting,
    error,
    requestHint,
    clearHint,
    reset,
  };
}
