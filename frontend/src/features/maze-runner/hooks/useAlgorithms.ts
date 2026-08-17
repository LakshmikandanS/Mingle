/**
 * useAlgorithms — fetches and caches the algorithm list from the backend.
 *
 * Provides available + planned algorithms, and a function
 * to lazily fetch documentation for a specific algorithm.
 */

import { useCallback, useEffect, useState } from 'react';
import * as mazeApi from '../../../api/mazeClient';
import type {
  AlgorithmDocumentationResponse,
  AlgorithmSummary,
} from '../../../types/maze';

export interface UseAlgorithmsReturn {
  available: AlgorithmSummary[];
  planned: AlgorithmSummary[];
  all: AlgorithmSummary[];
  isLoading: boolean;
  error: string | null;
  documentation: AlgorithmDocumentationResponse | null;
  isDocLoading: boolean;
  fetchDocumentation: (algorithm: string) => Promise<void>;
  clearDocumentation: () => void;
}

export function useAlgorithms(): UseAlgorithmsReturn {
  const [available, setAvailable] = useState<AlgorithmSummary[]>([]);
  const [planned, setPlanned] = useState<AlgorithmSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [documentation, setDocumentation] =
    useState<AlgorithmDocumentationResponse | null>(null);
  const [isDocLoading, setIsDocLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const result = await mazeApi.listAlgorithms();
        if (!cancelled) {
          setAvailable(result.available);
          setPlanned(result.planned);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Failed to load algorithms');
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const fetchDocumentation = useCallback(async (algorithm: string) => {
    setIsDocLoading(true);
    try {
      const docs = await mazeApi.getAlgorithmDocumentation(algorithm);
      setDocumentation(docs);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load documentation');
    } finally {
      setIsDocLoading(false);
    }
  }, []);

  const clearDocumentation = useCallback(() => {
    setDocumentation(null);
  }, []);

  const all = [...available, ...planned];

  return {
    available,
    planned,
    all,
    isLoading,
    error,
    documentation,
    isDocLoading,
    fetchDocumentation,
    clearDocumentation,
  };
}
