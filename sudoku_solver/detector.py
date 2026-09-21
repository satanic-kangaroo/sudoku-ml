"""تشخیص جدول سودوکو در عکس"""

import cv2
import numpy as np


def find_sudoku_grid(img_bgr, min_area=10000):
    """بزرگ‌ترین کانتور ۴ضلعی رو پیدا می‌کنه"""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in contours[:10]:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(approx) > min_area:
            return approx

    return None


def warp_perspective(img, corners, size=450):
    """تصحیح پرسپکتیو و تبدیل به مربع"""
    corners = corners.reshape(4, 2).astype("float32")
    s = corners.sum(axis=1)
    diff = np.diff(corners, axis=1)

    tl = corners[np.argmin(s)]
    br = corners[np.argmax(s)]
    tr = corners[np.argmin(diff)]
    bl = corners[np.argmax(diff)]

    src = np.array([tl, tr, br, bl], dtype="float32")
    dst = np.array([
        [0, 0], [size - 1, 0],
        [size - 1, size - 1], [0, size - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(img, M, (size, size))


def extract_cells(warped, grid_size=9):
    """تقسیم جدول به 81 خونه"""
    size = warped.shape[0] // grid_size
    cells = []
    for row in range(grid_size):
        for col in range(grid_size):
            y1, y2 = row * size, (row + 1) * size
            x1, x2 = col * size, (col + 1) * size
            cells.append(warped[y1:y2, x1:x2])
    return cells