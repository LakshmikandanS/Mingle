/**
 * useMazeEnvironment — manages maze environment creation and state.
 */

import { useCallback, useState } from 'react';
import * as mazeApi from '../../../api/mazeClient';
import type {
  MazeEnvironmentRequest,
  MazeEnvironmentResponse,
} from '../../../types/maze';

export interface UseMazeEnvironmentReturn {
  environment: MazeEnvironmentResponse | null;
  isLoading: boolean;
  error: string | null;
  createEnvironment: (config: MazeEnvironmentRequest) => Promise<MazeEnvironmentResponse | null>;
  reset: () => void;
  clearError: () => void;
}

export function useMazeEnvironment(): UseMazeEnvironmentReturn {
  const [environment, setEnvironment] =
    useState<MazeEnvironmentResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createEnvironment = useCallback(
    async (config: MazeEnvironmentRequest): Promise<MazeEnvironmentResponse | null> => {
      setIsLoading(true);
      setError(null);
      try {
        const env = await mazeApi.createEnvironment(config);
        setEnvironment(env);
        return env;
      } catch (e) {
        const msg = e instanceof Error ? e.message : 'Failed to create environment';
        setError(msg);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const reset = useCallback(() => {
    setEnvironment(null);
    setError(null);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return {
    environment,
    isLoading,
    error,
    createEnvironment,
    reset,
    clearError,
  };
}
