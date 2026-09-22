"""
Benchmark runner — runs each solver N times and returns statistics.
"""

from __future__ import annotations
import time
import numpy as np
from statistics import mean, median, stdev

from .solver import solve_backtracking, solve_dlx
from .dlx_solver import validate_solution


def benchmark_puzzle(board: np.ndarray, runs: int = 5):
    """
    Run each solver `runs` times on the same board.

    Returns:
        {
            "backtracking": {
                "time_ms":  {"min": ..., "median": ..., "mean": ..., "max": ..., "std": ...},
                "nodes":    {"min": ..., "median": ..., ...},
                "backtracks": {...},
                "solved":   bool,
            },
            "dlx": { ... same ... },
            "winner": "dlx" | "backtracking" | "tie",
            "speedup": float,
        }
    """
    result = {}

    for name, fn in [("backtracking", solve_backtracking), ("dlx", solve_dlx)]:
        times, nodes, bts, depths = [], [], [], []
        solved_flag = False

        # 1 warm-up run (excluded from stats)
        fn(board)

        for _ in range(runs):
            solved, solution, stats = fn(board)
            solved_flag = solved
            times.append(stats.time_ms)
            nodes.append(stats.nodes)
            bts.append(stats.backtracks)
            depths.append(stats.max_depth)

        result[name] = {
            "solved": solved_flag,
            "time_ms":    _agg(times),
            "nodes":      _agg(nodes),
            "backtracks": _agg(bts),
            "max_depth":  _agg(depths),
        }

    # Determine winner
    t_bt  = result["backtracking"]["time_ms"]["median"]
    t_dlx = result["dlx"]["time_ms"]["median"]

    if abs(t_dlx - t_bt) < 0.1:
        result["winner"] = "tie"
        result["speedup"] = 1.0
    elif t_dlx < t_bt:
        result["winner"] = "dlx"
        result["speedup"] = t_bt / t_dlx if t_dlx > 0 else float("inf")
    else:
        result["winner"] = "backtracking"
        result["speedup"] = t_dlx / t_bt if t_bt > 0 else float("inf")

    return result


def _agg(values: list[float]) -> dict:
    """Aggregate a list into min/median/mean/max/std."""
    if not values:
        return {"min": 0, "median": 0, "mean": 0, "max": 0, "std": 0}
    return {
        "min":    float(min(values)),
        "median": float(median(values)),
        "mean":   float(mean(values)),
        "max":    float(max(values)),
        "std":    float(stdev(values)) if len(values) > 1 else 0.0,
    }


def difficulty_label(board: np.ndarray) -> tuple[str, str, str]:
    """
    Quick heuristic difficulty based on number of givens.
    Returns (label, emoji, color).
    """
    givens = int(np.sum(board > 0))
    if givens >= 36:
        return ("Easy", "🟢", "#059669")
    if givens >= 30:
        return ("Medium", "🟡", "#d97706")
    if givens >= 25:
        return ("Hard", "🟠", "#ea580c")
    return ("Expert", "🔴", "#dc2626")