"""End-to-end pipeline: image → detection → digits → solver."""

import cv2
import numpy as np

from .detector import find_sudoku_grid, warp_perspective, extract_cells
from .digits import predict_board
from .solver import solve, is_board_consistent
from .benchmark import benchmark_puzzle
from .difficulty import rate_difficulty

def solve_sudoku_from_image(
    img_bgr,
    model,
    confidence_threshold: float = 0.70,
    algorithm: str = "dlx",
    compare_mode: bool = False,
    benchmark_runs: int = 5,
    progress_callback=None,
):
    """
    Full pipeline from image to solution.

    Args:
        img_bgr:               input image (BGR numpy array)
        model:                 loaded Keras model
        confidence_threshold:  digit acceptance threshold (0..1)
        algorithm:             "backtracking" | "dlx"
        compare_mode:          if True, run both and compare timings
        benchmark_runs:        runs per solver in compare mode
        progress_callback:     function(step_msg, percent)

    Returns:
        dict with keys:
            board, solution, warped, warped_solved,
            confidences, solved,
            solver_algorithm, solver_time_ms, solver_stats,
            difficulty,
            comparison (only when compare_mode=True)
            error (only on failure)
    """
    def report(msg, pct):
        if progress_callback:
            progress_callback(msg, pct)

    # 1. Detect grid
    report("Detecting grid…", 10)
    corners = find_sudoku_grid(img_bgr)
    if corners is None:
        return {
            "error": "Could not find a Sudoku grid in the image.",
            "solved": False,
        }

    # 2. Warp
    report("Correcting perspective…", 30)
    warped = warp_perspective(img_bgr, corners)

    # 3. Extract cells
    report("Extracting cells…", 50)
    cells = extract_cells(warped)

    # 4. Recognize digits
    report("Recognizing digits…", 70)
    board, confidences = predict_board(cells, model, confidence_threshold)

    # 5. Sanity check
    if not is_board_consistent(board):
        return {
            "error": "Detected board contains a conflict. "
                     "Try adjusting the confidence threshold.",
            "board": board,
            "solved": False,
        }

    # 6. Solve
    report("Solving…", 90)

    comparison = None
    if compare_mode:
        report(f"Benchmarking ({benchmark_runs} runs each)…", 90)
        comparison = benchmark_puzzle(board, runs=benchmark_runs)
        # Use DLX as canonical solution
        solved, solution, stats = solve(board, algorithm="dlx")
        used = "dlx"
    else:
        solved, solution, stats = solve(board, algorithm=algorithm)
        used = algorithm

    # 7. Difficulty — scientific rating
    diff_score = rate_difficulty(board)

    # 8. Draw
    report("Rendering result…", 100)
    warped_solved = (
        draw_solution(warped, board, solution) if solved else warped
    )

    out = {
        "board":            board,
        "solution":         solution,
        "warped":           warped,
        "warped_solved":    warped_solved,
        "confidences":      confidences,
        "solved":           solved,
        "solver_algorithm": used,
        "solver_time_ms":   stats.time_ms,
        "solver_stats":     stats.as_dict(),
        "difficulty":       diff_score.as_dict(),
    }
    if comparison is not None:
        out["comparison"] = comparison
    return out


def draw_solution(warped, original, solution):
    """Overlay the solution (in red) on the warped grid image."""
    cell = warped.shape[0] // 9
    output = warped.copy()
    for r in range(9):
        for c in range(9):
            if original[r, c] == 0 and solution[r, c] != 0:
                y = r * cell + cell // 2
                x = c * cell + cell // 2
                cv2.putText(
                    output, str(solution[r, c]),
                    (x - 10, y + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                    (0, 0, 255), 3,
                )
    return output


# ============================================================
# Board serialization helpers
# ============================================================

def board_to_text(board, style: str = "dots") -> str:
    """
    Convert a 9×9 board to text in various formats.

    Args:
        board: np.ndarray (9, 9) ints 0-9 (0 = empty)
        style: one of "dots", "zeros", "grid", "compact"

    Returns:
        Formatted string.
    """
    if style == "compact":
        return "".join(str(int(board[r, c])) for r in range(9) for c in range(9))

    if style == "dots":
        lines = []
        for r in range(9):
            row = [
                str(int(board[r, c])) if board[r, c] != 0 else "."
                for c in range(9)
            ]
            lines.append(" ".join(row))
        return "\n".join(lines)

    if style == "zeros":
        lines = []
        for r in range(9):
            lines.append(" ".join(str(int(x)) for x in board[r]))
        return "\n".join(lines)

    if style == "grid":
        def cell(v):
            return str(int(v)) if v != 0 else "."

        lines = ["+-------+-------+-------+"]

        for r in range(9):
            cells = [cell(board[r, c]) for c in range(9)]
            row = "| " + " ".join(cells[0:3]) + " | " \
                       + " ".join(cells[3:6]) + " | " \
                       + " ".join(cells[6:9]) + " |"
            lines.append(row)

            if r in (2, 5):
                lines.append("+-------+-------+-------+")

        lines.append("+-------+-------+-------+")
        return "\n".join(lines)

    raise ValueError(
        f"Unknown style: {style!r}. "
        f"Expected one of: dots, zeros, grid, compact"
    )