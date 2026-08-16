/**
 * API client for the Mingle backend.
 *
 * This layer handles ONLY HTTP communication.
 * No game orchestration or state management logic belongs here.
 */

import type {
  CreateGameRequest,
  DecisionResponse,
  GameStateResponse,
  ReplayResponse,
} from '../types/api';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const message =
      body.detail || `Request failed with status ${response.status}`;
    throw new Error(message);
  }
  return response.json();
}

export async function createGame(
  players: Record<string, string>,
): Promise<GameStateResponse> {
  const request: CreateGameRequest = { game: 'tic_tac_toe', players };
  const response = await fetch(`${API_BASE}/games`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return handleResponse<GameStateResponse>(response);
}

export async function getGame(
  sessionId: string,
): Promise<GameStateResponse> {
  const response = await fetch(`${API_BASE}/games/${sessionId}`);
  return handleResponse<GameStateResponse>(response);
}

export async function submitAction(
  sessionId: string,
  action: [number, number],
): Promise<GameStateResponse> {
  const response = await fetch(`${API_BASE}/games/${sessionId}/actions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  });
  return handleResponse<GameStateResponse>(response);
}

export async function getReplay(
  sessionId: string,
): Promise<ReplayResponse> {
  const response = await fetch(`${API_BASE}/games/${sessionId}/replay`);
  return handleResponse<ReplayResponse>(response);
}

export async function getDecision(
  sessionId: string,
  decisionId: string,
): Promise<DecisionResponse> {
  const response = await fetch(
    `${API_BASE}/games/${sessionId}/decisions/${decisionId}`,
  );
  return handleResponse<DecisionResponse>(response);
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/health`);
  return handleResponse<{ status: string }>(response);
}
