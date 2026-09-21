"""تشخیص ارقام با مدل CNN"""

import cv2
import numpy as np


def clean_cell(cell):
    """پاکسازی هر خونه و آماده‌سازی برای مدل (28×28)"""
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

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

    s = max(w, h)
    canvas = np.zeros((s, s), dtype=np.uint8)
    canvas[(s - h) // 2:(s - h) // 2 + h,
           (s - w) // 2:(s - w) // 2 + w] = digit

    digit = cv2.resize(canvas, (20, 20))
    final = np.zeros((28, 28), dtype=np.uint8)
    final[4:24, 4:24] = digit
    return final


def predict_board(cells, model, confidence_threshold=0.7):
    """پیش‌بینی کل جدول"""
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