/**
 * useSearchReplay — manages search trace replay state.
 *
 * Fetches trace from backend, then replays events step-by-step.
 * NEVER reproduces search logic — purely replays backend SearchTrace.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import * as mazeApi from '../../../api/mazeClient';
import type {
  SearchEventResponse,
  SearchRunResponse,
} from '../../../types/maze';
import type { ReplaySpeed } from '../types';

export interface UseSearchReplayReturn {
  searchRun: SearchRunResponse | null;
  events: SearchEventResponse[];
  currentEventIndex: number;
  totalEvents: number;
  isPlaying: boolean;
  speed: ReplaySpeed;
  isLoading: boolean;
  error: string | null;
  startSearch: (environmentId: string, algorithm: string) => Promise<SearchRunResponse | null>;
  loadExistingSearch: (searchRun: SearchRunResponse) => Promise<void>;
  play: () => void;
  pause: () => void;
  step: () => void;
  stepBack: () => void;
  resetReplay: () => void;
  setSpeed: (speed: ReplaySpeed) => void;
  jumpTo: (index: number) => void;
  reset: () => void;
}

export function useSearchReplay(): UseSearchReplayReturn {
  const [searchRun, setSearchRun] = useState<SearchRunResponse | null>(null);
  const [events, setEvents] = useState<SearchEventResponse[]>([]);
  const [currentEventIndex, setCurrentEventIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeedState] = useState<ReplaySpeed>(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const playIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const totalEvents = events.length;

  // Auto-play timer
  useEffect(() => {
    if (playIntervalRef.current) {
      clearInterval(playIntervalRef.current);
      playIntervalRef.current = null;
    }

    if (isPlaying && totalEvents > 0) {
      const intervalMs = Math.max(50, 300 / speed);
      playIntervalRef.current = setInterval(() => {
        setCurrentEventIndex((prev) => {
          if (prev >= totalEvents - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, intervalMs);
    }

    return () => {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
    };
  }, [isPlaying, speed, totalEvents]);

  const fetchTrace = useCallback(async (runId: string) => {
    setIsLoading(true);
    try {
      const trace = await mazeApi.getSearchTrace(runId);
      setEvents(trace.events);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch trace');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const startSearch = useCallback(async (
    environmentId: string,
    algorithm: string,
  ): Promise<SearchRunResponse | null> => {
    setIsLoading(true);
    setError(null);
    setCurrentEventIndex(-1);
    setIsPlaying(false);
    try {
      const run = await mazeApi.createSearchRun(environmentId, algorithm);
      setSearchRun(run);
      await fetchTrace(run.run_id);
      return run;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to run search');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [fetchTrace]);

  const loadExistingSearch = useCallback(async (run: SearchRunResponse) => {
    setSearchRun(run);
    setCurrentEventIndex(-1);
    setIsPlaying(false);
    await fetchTrace(run.run_id);
  }, [fetchTrace]);

  const play = useCallback(() => {
    if (currentEventIndex >= totalEvents - 1) {
      setCurrentEventIndex(-1);
    }
    setIsPlaying(true);
  }, [currentEventIndex, totalEvents]);

  const pause = useCallback(() => {
    setIsPlaying(false);
  }, []);

  const step = useCallback(() => {
    setIsPlaying(false);
    setCurrentEventIndex((prev) => Math.min(prev + 1, totalEvents - 1));
  }, [totalEvents]);

  const stepBack = useCallback(() => {
    setIsPlaying(false);
    setCurrentEventIndex((prev) => Math.max(prev - 1, -1));
  }, []);

  const resetReplay = useCallback(() => {
    setIsPlaying(false);
    setCurrentEventIndex(-1);
  }, []);

  const setSpeed = useCallback((s: ReplaySpeed) => {
    setSpeedState(s);
  }, []);

  const jumpTo = useCallback((index: number) => {
    setIsPlaying(false);
    setCurrentEventIndex(Math.max(-1, Math.min(index, totalEvents - 1)));
  }, [totalEvents]);

  const reset = useCallback(() => {
    setSearchRun(null);
    setEvents([]);
    setCurrentEventIndex(-1);
    setIsPlaying(false);
    setError(null);
    if (playIntervalRef.current) {
      clearInterval(playIntervalRef.current);
      playIntervalRef.current = null;
    }
  }, []);

  return {
    searchRun,
    events,
    currentEventIndex,
    totalEvents,
    isPlaying,
    speed,
    isLoading,
    error,
    startSearch,
    loadExistingSearch,
    play,
    pause,
    step,
    stepBack,
    resetReplay,
    setSpeed,
    jumpTo,
    reset,
  };
}
