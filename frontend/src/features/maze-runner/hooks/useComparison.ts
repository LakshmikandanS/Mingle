/**
 * useComparison — manages player-vs-search comparison data.
 *
 * All comparison logic is backend-side. This hook just fetches results.
 */

import { useCallback, useState } from 'react';
import * as mazeApi from '../../../api/mazeClient';
import type {
  ComparisonResponse,
  IntermediateComparisonResponse,
  MazeState,
} from '../../../types/maze';

export interface UseComparisonReturn {
  comparison: ComparisonResponse | null;
  intermediateInsight: IntermediateComparisonResponse | null;
  isLoading: boolean;
  error: string | null;
  compare: (playerRunId: string, searchRunId: string) => Promise<void>;
  fetchInsight: (
    playerRunId: string,
    searchRunId: string,
    state?: MazeState,
  ) => Promise<void>;
  reset: () => void;
}

export function useComparison(): UseComparisonReturn {
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [intermediateInsight, setIntermediateInsight] =
    useState<IntermediateComparisonResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const compare = useCallback(async (playerRunId: string, searchRunId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await mazeApi.compareRuns(playerRunId, searchRunId);
      setComparison(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Comparison failed');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchInsight = useCallback(async (
    playerRunId: string,
    searchRunId: string,
    state?: MazeState,
  ) => {
    try {
      const result = await mazeApi.intermediateComparison(
        playerRunId,
        searchRunId,
        state,
      );
      setIntermediateInsight(result);
    } catch {
      // Non-critical — intermediate insight is optional
    }
  }, []);

  const reset = useCallback(() => {
    setComparison(null);
    setIntermediateInsight(null);
    setError(null);
  }, []);

  return {
    comparison,
    intermediateInsight,
    isLoading,
    error,
    compare,
    fetchInsight,
    reset,
  };
}
