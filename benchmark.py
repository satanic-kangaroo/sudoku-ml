"""
Benchmark: Backtracking vs DLX on a range of Sudoku puzzles.
"""

import time
import numpy as np
from sudoku_solver.solver import _solve_backtracking
from sudoku_solver.dlx_solver import solve_dlx


# یه سری جدول از آسون تا سخت
PUZZLES = {
    "easy": [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9],
    ],
    "medium": [
        [0,2,0,0,0,0,0,0,0],
        [0,0,0,6,0,0,0,0,3],
        [0,7,4,0,8,0,0,0,0],
        [0,0,0,0,0,3,0,0,2],
        [0,8,0,0,4,0,0,1,0],
        [6,0,0,5,0,0,0,0,0],
        [0,0,0,0,1,0,7,8,0],
        [5,0,0,0,0,9,0,0,0],
        [0,0,0,0,0,0,0,4,0],
    ],
    "hard": [  # "AI Escargot" — یکی از سخت‌ترین جدول‌ها
        [8,0,0,0,0,0,0,0,0],
        [0,0,3,6,0,0,0,0,0],
        [0,7,0,0,9,0,2,0,0],
        [0,5,0,0,0,7,0,0,0],
        [0,0,0,0,4,5,7,0,0],
        [0,0,0,1,0,0,0,3,0],
        [0,0,1,0,0,0,0,6,8],
        [0,0,8,5,0,0,0,1,0],
        [0,9,0,0,0,0,4,0,0],
    ],
    "empty": [
        [0]*9 for _ in range(9)
    ],
}


def bench(puzzle, solver, runs=5):
    times = []
    for _ in range(runs):
        board = np.array(puzzle, dtype=int)
        t0 = time.perf_counter()
        if solver == "backtracking":
            _solve_backtracking(board)
        else:
            solve_dlx(board)
        times.append(time.perf_counter() - t0)
    return min(times) * 1000  # ms


def main():
    print(f"{'Puzzle':<12} {'Backtracking':>15} {'DLX':>15} {'Speedup':>10}")
    print("-" * 55)

    for name, puzzle in PUZZLES.items():
        t_bt = bench(puzzle, "backtracking")
        t_dlx = bench(puzzle, "dlx")
        speedup = t_bt / t_dlx if t_dlx > 0 else float("inf")
        print(f"{name:<12} {t_bt:>13.2f}ms {t_dlx:>13.2f}ms {speedup:>9.1f}x")


if __name__ == "__main__":
    main()