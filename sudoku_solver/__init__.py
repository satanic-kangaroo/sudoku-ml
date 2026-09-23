"""Sudoku Solver — main package."""
from .detector import find_sudoku_grid, warp_perspective, extract_cells
from .digits import clean_cell, predict_board
from .solver import (
    solve,
    solve_backtracking,
    solve_dlx,
    is_board_consistent,
    SolveStats,
)
from .dlx_solver import solve_dlx as solve_dlx_raw, validate_solution
from .benchmark import benchmark_puzzle, difficulty_label
from .pipeline import solve_sudoku_from_image

__version__ = "1.0.0"
