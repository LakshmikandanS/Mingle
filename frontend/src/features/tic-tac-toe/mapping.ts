/**
 * Mapping between backend API responses and frontend domain types.
 * Prevents raw backend structures from leaking into every UI component.
 */

import type { GameStateResponse } from '../../types/api';
import type { Board, CellValue, GameStatus, Position } from './types';
import { AGENT_LABELS, type AgentType } from './types';

/** Map raw API board (string[][]) to typed Board (CellValue[][]). */
export function mapBoard(apiBoard: string[][]): Board {
  return apiBoard.map((row) =>
    row.map((cell) => (cell === '' ? '' : cell) as CellValue),
  );
}

/** Map raw API legal actions to typed Positions. */
export function mapLegalActions(actions: number[][]): Position[] {
  return actions.map((a) => [a[0], a[1]] as Position);
}

/** Cast raw status string to typed GameStatus. */
export function mapStatus(status: string): GameStatus {
  return status as GameStatus;
}

/** Check if the current turn belongs to a human player. */
export function isHumanTurn(
  gameState: GameStateResponse,
  players: Record<string, string>,
): boolean {
  return players[gameState.current_player] === 'human';
}

/** Get display-friendly agent name. */
export function formatAgentName(agentKey: string): string {
  return AGENT_LABELS[agentKey as AgentType] ?? agentKey;
}

/** Determine winning cells from a board, if any. */
export function getWinningCells(board: Board): Position[] | null {
  // Check rows
  for (let i = 0; i < 3; i++) {
    if (board[i][0] && board[i][0] === board[i][1] && board[i][1] === board[i][2]) {
      return [[i, 0], [i, 1], [i, 2]];
    }
  }
  // Check columns
  for (let j = 0; j < 3; j++) {
    if (board[0][j] && board[0][j] === board[1][j] && board[1][j] === board[2][j]) {
      return [[0, j], [1, j], [2, j]];
    }
  }
  // Check diagonals
  if (board[0][0] && board[0][0] === board[1][1] && board[1][1] === board[2][2]) {
    return [[0, 0], [1, 1], [2, 2]];
  }
  if (board[0][2] && board[0][2] === board[1][1] && board[1][1] === board[2][0]) {
    return [[0, 2], [1, 1], [2, 0]];
  }
  return null;
}

/** Check if a position is in a list of positions. */
export function positionInList(
  pos: Position,
  list: Position[] | null,
): boolean {
  if (!list) return false;
  return list.some(([r, c]) => r === pos[0] && c === pos[1]);
}

/** Get human-friendly game status text. */
export function getStatusText(
  status: GameStatus,
  currentPlayer: string,
  players: Record<string, string>,
  isSubmitting: boolean,
): string {
  if (isSubmitting) {
    const agentName = players[currentPlayer];
    return agentName === 'human'
      ? 'Processing…'
      : `${formatAgentName(agentName)} thinking…`;
  }

  switch (status) {
    case 'PLAYER_X_WINS':
      return 'X wins!';
    case 'PLAYER_O_WINS':
      return 'O wins!';
    case 'DRAW':
      return 'Draw';
    case 'IN_PROGRESS': {
      const bothHuman = players['X'] === 'human' && players['O'] === 'human';
      return bothHuman ? `${currentPlayer}'s turn` : 'Your turn';
    }
    default:
      return status;
  }
}

/** Check if the game is finished. */
export function isGameOver(status: GameStatus): boolean {
  return status !== 'IN_PROGRESS';
}
