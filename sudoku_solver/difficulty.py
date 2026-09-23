"""
Scientific difficulty rating for Sudoku puzzles.

Key insight: The ONLY reliable difficulty signal is how much work
the backtracking solver has to do. Other signals (depth, DLX nodes,
number of empty cells) all just count "how many holes" — they don't
capture how HARD those holes are.

We use:
  - BT nodes (log-scaled)  60%
  - BT backtracks (log)    25%
  - Givens count (weak)    15%
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np

from .solver import solve_backtracking, solve_dlx


# ============================================================
# Data model
# ============================================================

@dataclass
class DifficultyScore:
    """Detailed difficulty breakdown."""
    score: int
    label: str
    emoji: str
    color: str

    # Raw signals
    givens_count: int
    backtracking_nodes: int
    backtracking_backtracks: int
    backtracking_depth: int
    dlx_nodes: int

    # Normalized signals (0..1) — useful for debugging
    norm_givens: float
    norm_bt_nodes: float
    norm_bt_backtracks: float

    def as_dict(self) -> dict:
        return asdict(self)


# ============================================================
# Calibration caps (log scale boundaries)
# ============================================================
#
# These are the "min" and "max" values of BT nodes we expect across
# a wide range of puzzles. Adjust if your dataset differs.

BT_NODES_LO    = 20          # Trivial puzzles: ~20-50
BT_NODES_HI    = 100_000     # Very hard: >100K
BT_BACKS_LO    = 1           # Easier puzzles rarely backtrack
BT_BACKS_HI    = 50_000      # Very hard: lots of backtracks

GIVENS_MIN     = 17          # Theoretical minimum
GIVENS_MAX     = 50          # Very easy puzzles


# ============================================================
# Log-scale normalization
# ============================================================

def _log_norm(value: float, lo: float, hi: float) -> float:
    """
    Map a positive value to [0, 1] using log scale.

    Log scale is essential for BT node counts because difficulty
    grows exponentially with search effort.
    """
    value = max(value, lo)  # clamp at lower bound
    if value >= hi:
        return 1.0
    return math.log(value / lo) / math.log(hi / lo)


def _linear_norm(value: float, lo: float, hi: float) -> float:
    """Map value to [0, 1] linearly."""
    if hi <= lo:
        return 0.0
    x = (value - lo) / (hi - lo)
    return float(np.clip(x, 0.0, 1.0))


# ============================================================
# Main rating function
# ============================================================

def rate_difficulty(board: np.ndarray) -> DifficultyScore:
    """
    Rate a puzzle's difficulty.

    Args:
        board: 9×9 numpy array (0 = empty)

    Returns:
        DifficultyScore with detailed breakdown.
    """
    givens_count = int(np.sum(board > 0))

    # ---- Run both solvers ----
    _, _, bt_stats = solve_backtracking(board)
    _, _, dlx_stats = solve_dlx(board)

    bt_nodes = int(bt_stats.nodes)
    bt_backtracks = int(bt_stats.backtracks)
    bt_depth = int(bt_stats.max_depth)
    dlx_nodes = int(dlx_stats.nodes)

    # ---- Normalize signals ----
    # Givens: more givens = easier → invert
    norm_givens = 1.0 - _linear_norm(givens_count, GIVENS_MIN, GIVENS_MAX)

    # BT nodes: log scale
    norm_bt_nodes = _log_norm(bt_nodes, BT_NODES_LO, BT_NODES_HI)

    # BT backtracks: log scale
    norm_bt_backtracks = _log_norm(bt_backtracks, BT_BACKS_LO, BT_BACKS_HI)

    # ---- Weighted combination ----
    raw_score = (
        0.15 * norm_givens +
        0.60 * norm_bt_nodes +
        0.25 * norm_bt_backtracks
    )

    # ---- Map to 1..10 ----
    score = max(1, min(10, int(round(raw_score * 9 + 1))))

    label, emoji, color = _label_for_score(score)

    return DifficultyScore(
        score=score,
        label=label,
        emoji=emoji,
        color=color,
        givens_count=givens_count,
        backtracking_nodes=bt_nodes,
        backtracking_backtracks=bt_backtracks,
        backtracking_depth=bt_depth,
        dlx_nodes=dlx_nodes,
        norm_givens=norm_givens,
        norm_bt_nodes=norm_bt_nodes,
        norm_bt_backtracks=norm_bt_backtracks,
    )


def _label_for_score(score: int) -> tuple[str, str, str]:
    """Map 1..10 to (label, emoji, color)."""
    if score <= 3:
        return ("Easy",    "🟢", "#059669")
    if score <= 5:
        return ("Medium",  "🟡", "#d97706")
    if score <= 7:
        return ("Hard",    "🟠", "#ea580c")
    if score <= 9:
        return ("Expert",  "🔴", "#dc2626")
    return ("Evil",        "⚫", "#1e293b")