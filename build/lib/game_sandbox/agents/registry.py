"""Lightweight registry for built-in agent implementations."""

from __future__ import annotations

from typing import Callable

from game_sandbox.agents.alphabeta import AlphaBetaAgent
from game_sandbox.agents.human import HumanAgent
from game_sandbox.agents.minimax import MinimaxAgent
from game_sandbox.agents.random_agent import RandomAgent
from game_sandbox.core.agent import Agent

AgentFactory = Callable[[bool], Agent]


def _human_agent(maximizing_player: bool) -> Agent:
    return HumanAgent()


def _random_agent(maximizing_player: bool) -> Agent:
    return RandomAgent()


def _minimax_agent(maximizing_player: bool) -> Agent:
    return MinimaxAgent(maximizing_player)


def _alphabeta_agent(maximizing_player: bool) -> Agent:
    return AlphaBetaAgent(maximizing_player)


AGENT_REGISTRY: dict[str, AgentFactory] = {
    "human": _human_agent,
    "random": _random_agent,
    "minimax": _minimax_agent,
    "alphabeta": _alphabeta_agent,
}


def create_agent(name: str, maximizing_player: bool) -> Agent:
    try:
        return AGENT_REGISTRY[name](maximizing_player)
    except KeyError as exc:
        known_agents = ", ".join(sorted(AGENT_REGISTRY))
        raise ValueError(f"Unknown agent '{name}'. Known agents: {known_agents}.") from exc


def is_human_agent(name: str) -> bool:
    return name == "human"
