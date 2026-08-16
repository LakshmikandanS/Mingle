# Mingle Game Sandbox

This package is the reusable foundation for small game and AI experiments in Mingle.

Tic-Tac-Toe is the first game implementation, not the framework itself. The package is split into:

- `core`: minimal generic game and agent contracts.
- `games`: game-specific state, rules, and game implementations.
- `agents`: action-selection agents and search algorithms.
- `observability`: search, decision, and match metrics plus human-readable reports.
- `runner`: reusable match execution.
- `examples`: runnable examples.
- `notebooks`: exploratory notebooks that import the package.

Adding a second game should primarily mean adding a new folder under `games/` and reusing the runner, observability, and any compatible agents.
