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
from .pipeline import solve_sudoku_from_image, board_to_text
from .history import SolveRecord, HistoryStore, make_thumbnail, relative_time
from .pdf_export import build_solution_pdf, build_history_pdf

__all__ = ["solve_sudoku_from_image", "board_to_text", "SolveRecord", "HistoryStore", "make_thumbnail", "relative_time", "build_solution_pdf", "build_history_pdf"]
__version__ = "1.0.0"