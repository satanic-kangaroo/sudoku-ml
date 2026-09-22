"""End-to-end pipeline: image → detection → digits → solver."""

import cv2
import numpy as np

from .detector import find_sudoku_grid, warp_perspective, extract_cells
from .digits import predict_board
from .solver import solve, is_board_consistent
from .benchmark import benchmark_puzzle, difficulty_label


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
    """
    def report(msg, pct):
        if progress_callback:
            progress_callback(msg, pct)

    # 1. Detect grid
    report("Detecting grid…", 10)
    corners = find_sudoku_grid(img_bgr)
    if corners is None:
        return {"error": "Could not find a Sudoku grid in the image.",
                "solved": False}

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
        solved, solution, stats = solve(board, algorithm="dlx")
        used = "dlx"
    else:
        solved, solution, stats = solve(board, algorithm=algorithm)
        used = algorithm

    # 7. Difficulty
    diff_label, diff_emoji, diff_color = difficulty_label(board)

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
        "difficulty": {
            "label": diff_label,
            "emoji": diff_emoji,
            "color": diff_color,
        },
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
