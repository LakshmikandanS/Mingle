"""Human-readable reporting for collected match metrics."""

from __future__ import annotations

from game_sandbox.observability.metrics import MatchMetrics


def _status_name(status: object) -> str:
    return getattr(status, "name", str(status))


def _pruning_efficiency(pruning_cutoffs: int, branches_considered: int) -> float:
    if branches_considered == 0:
        return 0.0
    return pruning_cutoffs / branches_considered * 100


def format_match_metrics(metrics: MatchMetrics) -> str:
    lines = [
        "",
        "=" * 70,
        "MATCH REPORT",
        "=" * 70,
        f"PLAYER X     : {metrics.player_x_agent}",
        f"PLAYER O     : {metrics.player_o_agent}",
        f"WINNER       : {_status_name(metrics.winner)}",
        f"MOVES        : {metrics.no_of_moves}",
        f"DURATION     : {metrics.duration_ms:.2f} ms",
        f"DURATION     : {metrics.duration_ms / 1000:.3f} s",
        "",
        "-" * 70,
        "DECISIONS",
        "-" * 70,
    ]

    for i, decision in enumerate(metrics.decisions, start=1):
        search = decision.search_metrics
        pruning_efficiency = _pruning_efficiency(
            search.pruning_cutoffs,
            search.branches_considered,
        )
        lines.extend(
            [
                "",
                f"Decision {i}",
                f"  Player          : {decision.player}",
                f"  Agent           : {decision.agent}",
                f"  Action          : {decision.chosen_action}",
                f"  Duration        : {decision.duration_ms:.3f} ms",
                "  Search:",
                f"    Nodes explored : {search.nodes_explored:,}",
                f"    Terminal nodes : {search.terminal_nodes:,}",
                f"    Deep copies    : {search.deep_copies:,}",
                f"    Max depth      : {search.max_depth}",
                f"    Branches considered: {search.branches_considered:,}",
                f"    Pruning cutoffs    : {search.pruning_cutoffs:,}",
                f"    Pruning efficiency : {pruning_efficiency:.2f}%",
            ]
        )

    lines.extend(["", "=" * 70])
    return "\n".join(lines)


def print_match_metrics(metrics: MatchMetrics) -> None:
    print(format_match_metrics(metrics))
