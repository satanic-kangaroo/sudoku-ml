"""
حل سودوکو از روی عکس — کل pipeline
ورودی: یه عکس سودوکو
خروجی: جدول حل‌شده
"""

import os
import cv2
import numpy as np
import tensorflow as tf


# ============================================================
# بخش ۱: پیدا کردن جدول سودوکو در عکس
# ============================================================

def find_sudoku_grid(image_path):
    """بزرگ‌ترین کانتور چهارضلعی رو پیدا می‌کنه"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"عکس پیدا نشد: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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
        if len(approx) == 4 and cv2.contourArea(approx) > 10000:
            return img, approx

    return img, None


# ============================================================
# بخش ۲: تصحیح پرسپکتیو
# ============================================================

def warp_perspective(img, corners, size=450):
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
    warped = cv2.warpPerspective(img, M, (size, size))
    return warped


# ============================================================
# بخش ۳: استخراج خونه‌ها
# ============================================================

def extract_cells(warped, grid_size=9):
    size = warped.shape[0] // grid_size
    cells = []
    for row in range(grid_size):
        for col in range(grid_size):
            y1, y2 = row * size, (row + 1) * size
            x1, x2 = col * size, (col + 1) * size
            cell = warped[y1:y2, x1:x2]
            cells.append(cell)
    return cells


# ============================================================
# بخش ۴: پاکسازی هر خونه
# ============================================================

def clean_cell(cell):
    """حذف خطوط جدول و آماده‌سازی برای مدل (28×28)"""
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    # حذف حاشیه (خطوط جدول)
    h, w = thresh.shape
    margin = int(0.15 * h)
    thresh[:margin, :] = 0
    thresh[-margin:, :] = 0
    thresh[:, :margin] = 0
    thresh[:, -margin:] = 0

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return None

    c = max(contours, key=cv2.contourArea)
    if cv2.contourArea(c) < 50:
        return None

    x, y, w, h = cv2.boundingRect(c)
    digit = thresh[y:y + h, x:x + w]

    # مربعی کردن با padding
    s = max(w, h)
    canvas = np.zeros((s, s), dtype=np.uint8)
    canvas[(s - h) // 2:(s - h) // 2 + h,
           (s - w) // 2:(s - w) // 2 + w] = digit

    # تبدیل به 28×28 با حاشیه (مثل دیتاست آموزش)
    digit = cv2.resize(canvas, (20, 20))
    final = np.zeros((28, 28), dtype=np.uint8)
    final[4:24, 4:24] = digit
    return final


# ============================================================
# بخش ۵: تشخیص ارقام
# ============================================================

def predict_board(cells, model, confidence_threshold=0.7):
    board = np.zeros((9, 9), dtype=int)
    confidences = np.zeros((9, 9), dtype=float)

    for i, cell in enumerate(cells):
        cleaned = clean_cell(cell)
        if cleaned is None:
            continue

        x = cleaned.astype("float32") / 255.0
        x = x.reshape(1, 28, 28, 1)

        probs = model.predict(x, verbose=0)[0]
        confidence = float(probs.max())
        digit = int(probs.argmax()) + 1

        r, c = i // 9, i % 9
        confidences[r, c] = confidence
        if confidence > confidence_threshold:
            board[r, c] = digit

    return board, confidences


# ============================================================
# بخش ۶: حل سودوکو (Backtracking)
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


def solve(board):
    empty = find_empty(board)
    if empty is None:
        return True

    r, c = empty
    for num in range(1, 10):
        if is_valid(board, r, c, num):
            board[r, c] = num
            if solve(board):
                return True
            board[r, c] = 0
    return False


# ============================================================
# بخش ۷: نمایش نتیجه
# ============================================================

def print_board(board, title="جدول"):
    print(f"\n{title}:")
    print("┌───────┬───────┬───────┐")
    for r in range(9):
        if r == 3 or r == 6:
            print("├───────┼───────┼───────┤")
        row_str = "│ "
        for c in range(9):
            if board[r, c] == 0:
                row_str += ". "
            else:
                row_str += f"{board[r, c]} "
            if c == 2 or c == 5:
                row_str += "│ "
        row_str += "│"
        print(row_str)
    print("└───────┴───────┴───────┘")


def draw_solution(warped, original, solution, save_path="solved.png"):
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

    cv2.imwrite(save_path, output)
    print(f"\n💾 تصویر حل‌شده ذخیره شد: {save_path}")

    # نمایش (اختیاری - اگه گrafیک داری)
    try:
        cv2.imshow("Solution", output)
        print("🖼️  پنجره رو ببین و یه کلید بزن...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except cv2.error:
        pass  # اگه headless بود، skip کن


# ============================================================
# بخش ۸: Pipeline کامل
# ============================================================

def solve_sudoku_from_image(image_path,
                            model_path="digit_model.keras",
                            confidence_threshold=0.7):
    print(f"📂 لود عکس: {image_path}")

    # ۱. لود مدل
    print(f"🧠 لود مدل: {model_path}")
    model = tf.keras.models.load_model(model_path)

    # ۲. پیدا کردن جدول
    print("🔍 جستجوی جدول...")
    img, corners = find_sudoku_grid(image_path)
    if corners is None:
        print("❌ جدول پیدا نشد!")
        return None

    # ۳. Warp
    print("📐 تصحیح پرسپکتیو...")
    warped = warp_perspective(img, corners)

    # ۴. استخراج خونه‌ها
    cells = extract_cells(warped)

    # ۵. تشخیص
    print("🔢 تشخیص ارقام...")
    board, confidences = predict_board(cells, model, confidence_threshold)

    # ۶. بررسی اطمینان پایین
    low_conf = np.sum((board == 0) & (confidences > 0.1))
    if low_conf > 0:
        print(f"⚠️  {low_conf} خونه با اطمینان پایین (نادیده گرفته شدن)")

    print_board(board, "جدول تشخیص‌داده‌شده")

    # ۷. اعتبارسنجی اولیه
    if not is_board_consistent(board):
        print("⚠️  جدول تشخیص‌داده‌شده متناقضه! یه رقم اشتباه تشخیص داده شده.")
        print("   راه‌حل: confidence_threshold رو بالاتر ببر یا عکس واضح‌تری بده.")

    # ۸. حل
    print("\n🧩 در حال حل...")
    solution = board.copy()
    if solve(solution):
        print_board(solution, "جواب نهایی")
        draw_solution(warped, board, solution, "solved.png")
        return solution
    else:
        print("❌ جدول حل نشد! (احتمالاً یه رقم اشتباه تشخیص داده شده)")
        print_board(board, "جدول تشخیص‌داده‌شده (مشکل‌دار)")
        draw_solution(warped, board, board, "detected.png")
        return None


def is_board_consistent(board):
    """چک می‌کنه آیا جدول تشخیص‌داده‌شده قوانین سودوکو رو نقض می‌کنه"""
    for r in range(9):
        for c in range(9):
            n = board[r, c]
            if n == 0:
                continue
            # موقتاً خالی کن و چک کن
            board[r, c] = 0
            valid = is_valid(board, r, c, n)
            board[r, c] = n
            if not valid:
                return False
    return True


# ============================================================
# اجرای اصلی
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("استفاده: uv run python test_image.py <path_to_image>")
        print("مثال:   uv run python test_image.py sudoku1.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    solve_sudoku_from_image(image_path)