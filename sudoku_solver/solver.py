"""
Sudoku solvers with instrumentation.
Each solver returns stats: nodes, backtracks, time.
"""

from __future__ import annotations
import time
import numpy as np
from dataclasses import dataclass, field, asdict


# ============================================================
# Stats container
# ============================================================

@dataclass
class SolveStats:
    """Uniform stats returned by every solver."""
    algorithm: str = ""
    solved: bool = False
    time_ms: float = 0.0
    nodes: int = 0           # recursive calls
    backtracks: int = 0      # dead-ends / rollbacks
    max_depth: int = 0       # max recursion depth
    extra: dict = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)


# ============================================================
# Backtracking (instrumented)
# ============================================================

class _BacktrackingSolver:
    def __init__(self):
        self.nodes = 0
        self.backtracks = 0
        self.max_depth = 0

    def is_valid(self, board, r, c, num):
        if num in board[r]:
            return False
        if num in board[:, c]:
            return False
        br, bc = 3 * (r // 3), 3 * (c // 3)
        if num in board[br:br + 3, bc:bc + 3]:
            return False
        return True

    def find_empty(self, board):
        for r in range(9):
            for c in range(9):
                if board[r, c] == 0:
                    return (r, c)
        return None

    def solve(self, board, depth=0):
        self.nodes += 1
        if depth > self.max_depth:
            self.max_depth = depth

        empty = self.find_empty(board)
        if empty is None:
            return True

        r, c = empty
        for num in range(1, 10):
            if self.is_valid(board, r, c, num):
                board[r, c] = num
                if self.solve(board, depth + 1):
                    return True
                board[r, c] = 0
                self.backtracks += 1

        return False


def solve_backtracking(board: np.ndarray) -> tuple[bool, np.ndarray, SolveStats]:
    """Solve with simple backtracking; return stats."""
    board_copy = board.copy()
    solver = _BacktrackingSolver()

    t0 = time.perf_counter()
    solved = solver.solve(board_copy)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    stats = SolveStats(
        algorithm="backtracking",
        solved=solved,
        time_ms=elapsed_ms,
        nodes=solver.nodes,
        backtracks=solver.backtracks,
        max_depth=solver.max_depth,
    )
    return solved, board_copy, stats


# ============================================================
# DLX (wraps dlx_solver)
# ============================================================

def solve_dlx(board: np.ndarray) -> tuple[bool, np.ndarray, SolveStats]:
    """Solve with DLX; return stats."""
    from .dlx_solver import solve_dlx as _solve_dlx

    t0 = time.perf_counter()
    solved, solution, raw_stats = _solve_dlx(board)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    stats = SolveStats(
        algorithm="dlx",
        solved=solved,
        time_ms=elapsed_ms,
        nodes=raw_stats.get("nodes", 0),
        backtracks=raw_stats.get("dead_ends", 0),
        max_depth=raw_stats.get("max_depth", 0),
        extra={
            "forbidden_rows": raw_stats.get("forbidden_rows", 0),
            "given_rows":     raw_stats.get("given_rows", 0),
        },
    )
    return solved, solution, stats


# ============================================================
# Dispatcher
# ============================================================

SOLVERS = {
    "backtracking": solve_backtracking,
    "dlx":          solve_dlx,
}


def solve(board, algorithm="dlx"):
    """Return (solved, solution, stats)."""
    if algorithm not in SOLVERS:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    return SOLVERS[algorithm](board)


def is_board_consistent(board: np.ndarray) -> bool:
    """Check a partially filled board for rule violations."""
    checker = _BacktrackingSolver()
    for r in range(9):
        for c in range(9):
            n = board[r, c]
            if n == 0:
                continue
            board[r, c] = 0
            valid = checker.is_valid(board, r, c, n)
            board[r, c] = n
            if not valid:
                return False
    return True