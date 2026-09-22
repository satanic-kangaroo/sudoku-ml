"""
Sudoku solvers — Backtracking and DLX.

This module is a *dispatcher*: it exposes a uniform `solve()` function
that routes to the requested algorithm and returns timing info.
"""

from __future__ import annotations
import time
import numpy as np

from .dlx_solver import solve_dlx


# ============================================================
# Backtracking (simple, educational)
# ============================================================

def is_valid(board, r, c, num):
    if num in board[r]:
        return False
    if num in board[:, c]:
        return False
    br, bc = 3 * (r // 3), 3 * (c // 3)
    if num in board[br:br + 3, bc:bc + 3]:
        return False
    return True


def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r, c] == 0:
                return (r, c)
    return None


def _solve_backtracking(board):
    empty = find_empty(board)
    if empty is None:
        return True
    r, c = empty
    for num in range(1, 10):
        if is_valid(board, r, c, num):
            board[r, c] = num
            if _solve_backtracking(board):
                return True
            board[r, c] = 0
    return False


def solve_backtracking(board: np.ndarray) -> tuple[bool, np.ndarray, float]:
    """
    Solve using simple backtracking.

    Returns:
        (solved, solution, elapsed_seconds)
    """
    board_copy = board.copy()
    t0 = time.perf_counter()
    solved = _solve_backtracking(board_copy)
    elapsed = time.perf_counter() - t0
    return solved, board_copy, elapsed


# ============================================================
# DLX (Knuth's Algorithm X + Dancing Links)
# ============================================================

def solve_dlx_timed(board: np.ndarray) -> tuple[bool, np.ndarray, float]:
    """
    Solve using DLX. Wraps solve_dlx() and adds timing.

    Returns:
        (solved, solution, elapsed_seconds)
    """
    t0 = time.perf_counter()
    solved, solution, _stats = solve_dlx(board)
    elapsed = time.perf_counter() - t0
    return solved, solution, elapsed


# ============================================================
# Dispatcher
# ============================================================

SOLVERS = {
    "backtracking": solve_backtracking,
    "dlx":          solve_dlx_timed,
}


def solve(board: np.ndarray, algorithm: str = "dlx"):
    """
    Uniform entry point.

    Args:
        board:     np.ndarray (9,9) ints 0-9 (0 = empty)
        algorithm: "backtracking" or "dlx"

    Returns:
        (solved, solution, elapsed_seconds, algorithm_used)
    """
    if algorithm not in SOLVERS:
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. "
            f"Available: {list(SOLVERS)}"
        )

    solved, solution, elapsed = SOLVERS[algorithm](board)
    return solved, solution, elapsed, algorithm


def solve_compare(board: np.ndarray):
    """
    Run *both* solvers and return a comparison dict.

    Returns:
        {
            "backtracking": {"solved": bool, "solution": arr, "time_ms": float},
            "dlx":          {"solved": bool, "solution": arr, "time_ms": float},
            "fastest":      "dlx" | "backtracking",
            "speedup":      float,  # backtracking_time / dlx_time
        }
    """
    result = {}
    for name, fn in SOLVERS.items():
        solved, solution, elapsed = fn(board)
        result[name] = {
            "solved": solved,
            "solution": solution,
            "time_ms": elapsed * 1000,
        }

    t_bt = result["backtracking"]["time_ms"]
    t_dlx = result["dlx"]["time_ms"]

    result["fastest"] = "dlx" if t_dlx < t_bt else "backtracking"
    result["speedup"] = (t_bt / t_dlx) if t_dlx > 0 else float("inf")

    return result


# ============================================================
# Validation
# ============================================================

def is_board_consistent(board: np.ndarray) -> bool:
    """Check that a partially filled board doesn't violate Sudoku rules."""
    for r in range(9):
        for c in range(9):
            n = board[r, c]
            if n == 0:
                continue
            board[r, c] = 0
            valid = is_valid(board, r, c, n)
            board[r, c] = n
            if not valid:
                return False
    return True