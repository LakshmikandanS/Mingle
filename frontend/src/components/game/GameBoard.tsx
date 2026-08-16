import {
  mapBoard,
  mapLegalActions,
  getWinningCells,
  positionInList,
} from '../../features/tic-tac-toe/mapping';
import type { Position } from '../../features/tic-tac-toe/types';
import type { MoveRecord } from '../../types/api';
import { GameCell } from './GameCell';
import './GameBoard.css';

interface GameBoardProps {
  board: string[][];
  legalActions: [number, number][];
  onCellClick: (action: [number, number]) => void;
  disabled: boolean;
  lastMove: MoveRecord | null;
  isGameOver: boolean;
}

export function GameBoard({
  board,
  legalActions,
  onCellClick,
  disabled,
  lastMove,
  isGameOver,
}: GameBoardProps) {
  const typedBoard = mapBoard(board);
  const typedActions = disabled ? [] : mapLegalActions(legalActions);
  const winningCells = isGameOver ? getWinningCells(typedBoard) : null;
  const lastMovePos: Position | null = lastMove
    ? (lastMove.action as Position)
    : null;

  return (
    <div className={`game-board ${disabled ? 'board-disabled' : ''}`} role="grid" aria-label="Tic-Tac-Toe board">
      {typedBoard.map((row, i) =>
        row.map((cell, j) => {
          const pos: Position = [i, j];
          const isClickable =
            !disabled &&
            positionInList(pos, typedActions);

          return (
            <GameCell
              key={`${i}-${j}`}
              value={cell}
              position={pos}
              isClickable={isClickable}
              isLastMove={
                lastMovePos !== null &&
                lastMovePos[0] === i &&
                lastMovePos[1] === j
              }
              isWinning={positionInList(pos, winningCells)}
              onClick={onCellClick}
            />
          );
        }),
      )}
    </div>
  );
}
