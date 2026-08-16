"""Game session routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from game_sandbox.api.schemas import (
    ActionRequest,
    CreateGameRequest,
    DecisionResponse,
    GameStateResponse,
    ReplayResponse,
)
from game_sandbox.session import GameSession, create_session
from game_sandbox.session.game_session import decision_to_dict

router = APIRouter()
_sessions: dict[str, GameSession] = {}


@router.post("/games", response_model=GameStateResponse)
def create_game_endpoint(request: CreateGameRequest) -> dict:
    try:
        session = create_session(request.game, request.players)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _sessions[session.session_id] = session
    return session.state()


@router.get("/games/{session_id}", response_model=GameStateResponse)
def get_game_endpoint(session_id: str) -> dict:
    return _get_session(session_id).state()


@router.post("/games/{session_id}/actions", response_model=GameStateResponse)
def submit_action_endpoint(session_id: str, request: ActionRequest) -> dict:
    try:
        return _get_session(session_id).submit_action(request.action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/games/{session_id}/replay", response_model=ReplayResponse)
def get_replay_endpoint(session_id: str) -> dict:
    return _get_session(session_id).get_replay()


@router.get("/games/{session_id}/decisions/{decision_id}", response_model=DecisionResponse)
def get_decision_endpoint(session_id: str, decision_id: str) -> dict:
    try:
        decision = _get_session(session_id).get_decision(decision_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return decision_to_dict(decision)


def _get_session(session_id: str) -> GameSession:
    try:
        return _sessions[session_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown session '{session_id}'.") from exc
