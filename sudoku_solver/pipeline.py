"""اتصال کل مراحل"""

import cv2
import numpy as np

from .detector import find_sudoku_grid, warp_perspective, extract_cells
from .digits import predict_board
from .solver import solve


def solve_sudoku_from_image(img_bgr, model,
                            confidence_threshold=0.7,
                            progress_callback=None):
    """
    Pipeline کامل — خروجی: dict
    
    کلیدهای خروجی:
      - board: جدول تشخیص‌داده‌شده
      - solution: جواب نهایی
      - warped: تصویر صاف‌شده‌ی جدول
      - warped_solved: تصویر با جواب قرمز
      - confidences: اطمینان هر خونه
      - solved: bool
    """
    def report(step, pct):
        if progress_callback:
            progress_callback(step, pct)

    # ۱. پیدا کردن جدول
    report("جستجوی جدول...", 10)
    corners = find_sudoku_grid(img_bgr)
    if corners is None:
        return {"error": "جدول سودوکو پیدا نشد", "solved": False}

    # ۲. Warp
    report("تصحیح پرسپکتیو...", 30)
    warped = warp_perspective(img_bgr, corners)

    # ۳. استخراج خونه‌ها
    report("استخراج خونه‌ها...", 50)
    cells = extract_cells(warped)

    # ۴. تشخیص
    report("تشخیص ارقام...", 70)
    board, confidences = predict_board(cells, model, confidence_threshold)

    # ۵. حل
    report("حل سودوکو...", 90)
    solution = board.copy()
    solved = solve(solution)

    # ۶. رسم جواب
    report("آماده‌سازی نتیجه...", 100)
    warped_solved = draw_solution(warped, board, solution) if solved else warped

    return {
        "board": board,
        "solution": solution,
        "warped": warped,
        "warped_solved": warped_solved,
        "confidences": confidences,
        "solved": solved,
    }


def draw_solution(warped, original, solution):
    """جواب رو با رنگ قرمز روی تصویر می‌کشه"""
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
                    (0, 0, 255), 3
                )
    return output