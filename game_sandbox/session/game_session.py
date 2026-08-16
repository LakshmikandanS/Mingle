"""Runtime orchestration for one running game."""

from __future__ import annotations

import time
from dataclasses import asdict
from copy import copy
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4

from game_sandbox.agents.registry import create_agent, is_human_agent
from game_sandbox.core.agent import Agent
from game_sandbox.core.game import Action, Game
from game_sandbox.games.registry import create_game
from game_sandbox.observability.history import DecisionRecord, GameHistory, MoveRecord
from game_sandbox.observability.metrics import SearchMetrics


@dataclass
class PlayerConfig:
    player: Any
    agent_name: str
    agent: Agent


@dataclass
class GameSession:
    session_id: str
    game_name: str
    game: Game
    players: dict[Any, PlayerConfig]
    history: GameHistory
    decisions: dict[str, DecisionRecord] = field(default_factory=dict)

    def state(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "game": self.game_name,
            "state": self.game.get_state(),
            "current_player": _player_token(self.game.get_current_player()),
            "legal_actions": [_json_action(action) for action in self.game.get_legal_actions()],
            "status": _status_token(self.game.get_status()),
        }

    def submit_action(self, action: Action) -> dict[str, Any]:
        if self.game.is_game_over():
            return self.state()

        current_player = self.game.get_current_player()
        player_config = self._player_config(current_player)
        if not is_human_agent(player_config.agent_name):
            raise ValueError("Current player is controlled by an agent.")

        self._apply_action(action)
        self.run_agent_turns()
        return self.state()

    def run_agent_turns(self) -> dict[str, Any]:
        while not self.game.is_game_over():
            current_player = self.game.get_current_player()
            player_config = self._player_config(current_player)
            if is_human_agent(player_config.agent_name):
                break

            decision_id = self._record_agent_decision(player_config)
            decision = self.decisions[decision_id]
            if decision.chosen_action is None:
                break
            self._apply_action(decision.chosen_action, decision_id)
        return self.state()

    def get_replay(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "game": self.game_name,
            "initial_state": self.history.initial_state,
            "moves": [_move_to_dict(move) for move in self.history.moves],
            "final_state": self.history.final_state,
        }

    def get_decision(self, decision_id: str) -> DecisionRecord:
        try:
            return self.decisions[decision_id]
        except KeyError as exc:
            raise ValueError(f"Unknown decision '{decision_id}'.") from exc

    def _player_config(self, player: Any) -> PlayerConfig:
        try:
            return self.players[player]
        except KeyError as exc:
            raise ValueError(f"No agent is assigned for player {_player_token(player)}.") from exc

    def _record_agent_decision(self, player_config: PlayerConfig) -> str:
        decision_id = str(uuid4())
        start = time.perf_counter()
        chosen_action = player_config.agent.choose_action(self.game)
        end = time.perf_counter()
        metrics = getattr(player_config.agent, "last_search_metrics", None)

        self.decisions[decision_id] = DecisionRecord(
            decision_id=decision_id,
            player=_player_token(player_config.player),
            agent=player_config.agent_name,
            chosen_action=_json_action(chosen_action),
            duration_ms=(end - start) * 1000,
            metrics=copy(metrics) if metrics is not None else SearchMetrics(),
        )
        return decision_id

    def _apply_action(self, action: Action, decision_id: Optional[str] = None) -> None:
        player = _player_token(self.game.get_current_player())
        normalized_action = _normalize_action(action)
        try:
            self.game.apply_action(normalized_action)
        except Exception as exc:
            raise ValueError(str(exc)) from exc
        self.history.moves.append(
            MoveRecord(
                move_number=len(self.history.moves) + 1,
                player=player,
                action=_json_action(normalized_action),
                resulting_state=self.game.get_state(),
                decision_id=decision_id,
            )
        )
        if self.game.is_game_over():
            self.history.final_state = self.game.get_state()


def create_session(game_name: str, player_agents: dict[str, str]) -> GameSession:
    game = create_game(game_name)
    players: dict[Any, PlayerConfig] = {}
    initial_player = game.get_current_player()

    player_order = [initial_player]
    for action in game.get_legal_actions()[:1]:
        probe = create_game(game_name)
        probe.apply_action(action)
        player_order.append(probe.get_current_player())

    for index, player in enumerate(player_order):
        player_key = _player_token(player)
        agent_name = player_agents.get(player_key)
        if agent_name is None:
            raise ValueError(f"Missing agent assignment for player '{player_key}'.")
        players[player] = PlayerConfig(
            player=player,
            agent_name=agent_name,
            agent=create_agent(agent_name, maximizing_player=index == 0),
        )

    session = GameSession(
        session_id=str(uuid4()),
        game_name=game_name,
        game=game,
        players=players,
        history=GameHistory(initial_state=game.get_state()),
    )
    session.run_agent_turns()
    return session


def _normalize_action(action: Any) -> Any:
    if isinstance(action, list):
        return tuple(action)
    return action


def _json_action(action: Any) -> Any:
    if isinstance(action, tuple):
        return list(action)
    return action


def _player_token(player: Any) -> str:
    value = getattr(player, "value", player)
    nested_value = getattr(value, "value", value)
    return str(nested_value).strip()


def _status_token(status: Any) -> str:
    return getattr(status, "name", str(status))


def _move_to_dict(move: MoveRecord) -> dict[str, Any]:
    return {
        "move_number": move.move_number,
        "player": move.player,
        "action": move.action,
        "resulting_state": move.resulting_state,
        "decision_id": move.decision_id,
    }


def decision_to_dict(decision: DecisionRecord) -> dict[str, Any]:
    return {
        "decision_id": decision.decision_id,
        "player": decision.player,
        "agent": decision.agent,
        "chosen_action": decision.chosen_action,
        "duration_ms": decision.duration_ms,
        "metrics": asdict(decision.metrics),
    }
