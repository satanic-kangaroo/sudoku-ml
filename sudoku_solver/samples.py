"""
Sample Sudoku puzzles.

Two sources:
  1. Shipped images in `assets/samples/` — real photos (optional)
  2. On-the-fly puzzle generation — random, clean, digital
"""

from __future__ import annotations
import random
from pathlib import Path

import cv2
import numpy as np

from .dlx_solver import solve_dlx


# ============================================================
# Shipped samples (optional — only used if assets exist)
# ============================================================

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "assets" / "samples"

SHIPPED = [
    {
        "id": "easy",
        "label": "Easy",
        "emoji": "🟢",
        "description": "Clean digital puzzle",
        "path": SAMPLES_DIR / "sample_easy.png",
    },
    {
        "id": "medium",
        "label": "Medium",
        "emoji": "🟡",
        "description": "Printed on paper",
        "path": SAMPLES_DIR / "sample_medium.jpg",
    },
    {
        "id": "hard",
        "label": "Hard",
        "emoji": "🟠",
        "description": "Angled photo with shadows",
        "path": SAMPLES_DIR / "sample_hard.jpg",
    },
]


def get_available_samples():
    """Return only the samples whose files actually exist."""
    return [s for s in SHIPPED if s["path"].exists()]


def load_sample_image(sample_id: str):
    """Load a shipped sample image as BGR, or None."""
    for s in SHIPPED:
        if s["id"] == sample_id:
            if not s["path"].exists():
                return None
            return cv2.imread(str(s["path"]))
    return None


# ============================================================
# Puzzle generation
# ============================================================

def generate_solved_board(seed: int | None = None) -> np.ndarray:
    """Generate a fully solved 9×9 Sudoku board."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    empty = np.zeros((9, 9), dtype=int)
    _, solved_board, _ = solve_dlx(empty)
    return solved_board.copy()


def punch_holes(board: np.ndarray, n_holes: int,
                seed: int | None = None) -> np.ndarray:
    """
    Remove n_holes random cells from a solved board.
    Does NOT guarantee a unique solution.
    """
    if seed is not None:
        random.seed(seed)

    out = board.copy()
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    for r, c in cells[:n_holes]:
        out[r, c] = 0

    return out


def has_unique_solution(board: np.ndarray) -> bool:
    """
    Check whether a puzzle has exactly one solution.

    Uses DLX's count_solutions() which stops counting after 2.
    """
    from .dlx_solver import count_solutions
    return count_solutions(board, limit=2) == 1


def generate_puzzle_with_unique_solution(
    n_holes: int,
    seed: int | None = None,
) -> np.ndarray:
    """
    Generate a puzzle with a guaranteed unique solution.

    Uses incremental hole-punching:
      1. Start with a fully solved board.
      2. Shuffle the 81 cells.
      3. For each cell, try to remove it. If the puzzle still has a
         unique solution, keep the hole; otherwise, restore the cell.
      4. Stop when we've removed `n_holes` cells (or run out of cells).

    This is dramatically faster than "try N times" because each
    uniqueness check runs on a nearly-complete puzzle (fast DLX).

    Args:
        n_holes: target number of holes. The final puzzle may have
                 fewer if the target can't be reached with this
                 solution's symmetry.
        seed:    optional random seed.

    Returns:
        np.ndarray (9, 9) with a unique solution.
    """
    from .dlx_solver import count_solutions

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    solved = generate_solved_board()
    puzzle = solved.copy()

    # Try multiple shuffles until we hit the target — but each attempt
    # is fast, so we can afford a few.
    for _ in range(5):
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)

        puzzle = solved.copy()
        holes_placed = 0

        for r, c in cells:
            if holes_placed >= n_holes:
                break

            original = int(puzzle[r, c])
            puzzle[r, c] = 0

            if count_solutions(puzzle, limit=2) == 1:
                holes_placed += 1
            else:
                puzzle[r, c] = original  # restore

        if holes_placed >= n_holes:
            return puzzle

    # If we didn't hit target after 5 shuffles, return the best attempt
    return puzzle

# ============================================================
# Rendering
# ============================================================

def _render_board(board: np.ndarray, cell_size: int) -> np.ndarray:
    """Render a 9×9 board as a clean BGR image."""
    padding = 2 * cell_size
    size = 9 * cell_size + 2 * padding
    img = np.full((size, size, 3), 255, dtype=np.uint8)

    grid_color = (180, 180, 180)
    thick_color = (40, 40, 40)
    text_color = (15, 15, 15)
    border_color = (0, 0, 0)

    # Outer border
    cv2.rectangle(
        img,
        (padding, padding),
        (padding + 9 * cell_size, padding + 9 * cell_size),
        border_color,
        4,
    )

    # Grid lines
    for i in range(1, 9):
        x = padding + i * cell_size
        y = padding + i * cell_size

        thickness = 1 if i % 3 else 3
        color = grid_color if i % 3 else thick_color

        cv2.line(img, (x, padding), (x, padding + 9 * cell_size),
                 color, thickness)
        cv2.line(img, (padding, y), (padding + 9 * cell_size, y),
                 color, thickness)

    # Digits
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = cell_size / 32
    thickness = max(1, int(cell_size / 24))

    for r in range(9):
        for c in range(9):
            d = int(board[r, c])
            if d == 0:
                continue

            text = str(d)
            (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)

            x = padding + c * cell_size + (cell_size - tw) // 2
            y = padding + r * cell_size + (cell_size + th) // 2

            cv2.putText(img, text, (x, y), font, font_scale,
                        text_color, thickness, cv2.LINE_AA)

    return img


def generate_random_puzzle_image(
    n_holes: int = 55,
    cell_size: int = 48,
    seed: int | None = None,
) -> np.ndarray:
    """Generate a random Sudoku puzzle image with a unique solution."""
    board = generate_puzzle_with_unique_solution(n_holes, seed=seed)
    return _render_board(board, cell_size)


# ============================================================
# Difficulty helpers
# ============================================================

def get_difficulty_from_holes(n_holes: int) -> tuple[str, str]:
    """Return (label, emoji) for a given hole count."""
    if n_holes <= 45:
        return ("Easy", "🟢")
    if n_holes <= 52:
        return ("Medium", "🟡")
    if n_holes <= 58:
        return ("Hard", "🟠")
    return ("Expert", "🔴")