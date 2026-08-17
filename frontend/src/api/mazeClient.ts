/**
 * API client for the Maze Runner backend.
 *
 * All Maze Runner HTTP communication lives here.
 * Reuses the shared handleResponse / API_BASE from client.ts.
 */

import { API_BASE, handleResponse } from './client';
import type {
  AlgorithmDocumentationResponse,
  AlgorithmsListResponse,
  ComparisonResponse,
  HintCostsResponse,
  HintHistoryResponse,
  HintLevel,
  HintResponse,
  IntermediateComparisonResponse,
  MazeAction,
  MazeEnvironmentRequest,
  MazeEnvironmentResponse,
  MazeState,
  PlayerActionResponse,
  PlayerHistoryResponse,
  PlayerRunResponse,
  SearchRunResponse,
  SearchTraceResponse,
} from '../types/maze';

/* ── Environment ───────────────────────────────────────────── */

export async function createEnvironment(
  request: MazeEnvironmentRequest,
): Promise<MazeEnvironmentResponse> {
  const response = await fetch(`${API_BASE}/maze/environments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse<MazeEnvironmentResponse>(response);
}

export async function getEnvironment(
  environmentId: string,
): Promise<MazeEnvironmentResponse> {
  const response = await fetch(`${API_BASE}/maze/environments/${environmentId}`);
  return handleResponse<MazeEnvironmentResponse>(response);
}

/* ── Player run ────────────────────────────────────────────── */

export async function createPlayerRun(
  environmentId: string,
): Promise<PlayerRunResponse> {
  const response = await fetch(`${API_BASE}/maze/runs/player`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ environment_id: environmentId }),
  });
  return handleResponse<PlayerRunResponse>(response);
}

export async function getPlayerRun(
  runId: string,
): Promise<PlayerRunResponse> {
  const response = await fetch(`${API_BASE}/maze/runs/player/${runId}`);
  return handleResponse<PlayerRunResponse>(response);
}

export async function movePlayer(
  runId: string,
  action: MazeAction,
): Promise<PlayerActionResponse> {
  const response = await fetch(`${API_BASE}/maze/runs/player/${runId}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  });
  return handleResponse<PlayerActionResponse>(response);
}

export async function giveUpPlayerRun(
  runId: string,
): Promise<PlayerRunResponse> {
  const response = await fetch(`${API_BASE}/maze/runs/player/${runId}/give-up`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  return handleResponse<PlayerRunResponse>(response);
}

export async function getPlayerHistory(
  runId: string,
): Promise<PlayerHistoryResponse> {
  const response = await fetch(`${API_BASE}/maze/runs/player/${runId}/history`);
  return handleResponse<PlayerHistoryResponse>(response);
}

/* ── Hints ─────────────────────────────────────────────────── */

export async function getHintHistory(
  runId: string,
): Promise<HintHistoryResponse> {
  const response = await fetch(`${API_BASE}/maze/runs/player/${runId}/hints`);
  return handleResponse<HintHistoryResponse>(response);
}

export async function requestHint(
  runId: string,
  hintLevel: HintLevel,
  algorithm?: string,
  searchRunId?: string,
): Promise<HintResponse> {
  const body: Record<string, unknown> = { hint_level: hintLevel };
  if (algorithm) body.algorithm = algorithm;
  if (searchRunId) body.search_run_id = searchRunId;
  const response = await fetch(`${API_BASE}/maze/runs/player/${runId}/hints`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return handleResponse<HintResponse>(response);
}

export async function getHintCosts(): Promise<HintCostsResponse> {
  const response = await fetch(`${API_BASE}/maze/hints/costs`);
  return handleResponse<HintCostsResponse>(response);
}

/* ── Search run ────────────────────────────────────────────── */

export async function createSearchRun(
  environmentId: string,
  algorithm: string,
  configuration: Record<string, unknown> = {},
): Promise<SearchRunResponse> {
  const response = await fetch(`${API_BASE}/maze/runs/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      environment_id: environmentId,
      algorithm,
      configuration,
    }),
  });
  return handleResponse<SearchRunResponse>(response);
}

export async function getSearchRun(
  runId: string,
): Promise<SearchRunResponse> {
  const response = await fetch(`${API_BASE}/maze/runs/search/${runId}`);
  return handleResponse<SearchRunResponse>(response);
}

export async function getSearchTrace(
  runId: string,
  fromIndex = 0,
  limit?: number,
): Promise<SearchTraceResponse> {
  const params = new URLSearchParams({ from_index: String(fromIndex) });
  if (limit !== undefined) params.set('limit', String(limit));
  const response = await fetch(
    `${API_BASE}/maze/runs/search/${runId}/trace?${params}`,
  );
  return handleResponse<SearchTraceResponse>(response);
}

/* ── Algorithms ────────────────────────────────────────────── */

export async function listAlgorithms(): Promise<AlgorithmsListResponse> {
  const response = await fetch(`${API_BASE}/maze/algorithms`);
  return handleResponse<AlgorithmsListResponse>(response);
}

export async function getAlgorithmDocumentation(
  algorithm: string,
): Promise<AlgorithmDocumentationResponse> {
  const response = await fetch(`${API_BASE}/maze/algorithms/${algorithm}`);
  return handleResponse<AlgorithmDocumentationResponse>(response);
}

/* ── Comparison ────────────────────────────────────────────── */

export async function compareRuns(
  playerRunId: string,
  searchRunId: string,
): Promise<ComparisonResponse> {
  const response = await fetch(`${API_BASE}/maze/comparisons`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      player_run_id: playerRunId,
      search_run_id: searchRunId,
    }),
  });
  return handleResponse<ComparisonResponse>(response);
}

export async function intermediateComparison(
  playerRunId: string,
  searchRunId: string,
  state?: MazeState,
): Promise<IntermediateComparisonResponse> {
  const body: Record<string, unknown> = {
    player_run_id: playerRunId,
    search_run_id: searchRunId,
  };
  if (state) body.state = state;
  const response = await fetch(`${API_BASE}/maze/comparisons/intermediate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return handleResponse<IntermediateComparisonResponse>(response);
}
