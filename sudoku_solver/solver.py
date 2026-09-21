"""حل سودوکو با Backtracking"""

import numpy as np


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


def is_board_consistent(board):
    """آیا جدول تشخیص‌داده‌شده قوانین سودوکو رو نقض می‌کنه؟"""
    for r in range(9):
        for c in range(9):
            n = board[r, c]
            if n == 0:
                continue
            board[r, c] = 0
            valid = is_valid(board, r, c, n)
            board[r, c] = n
            if not valid:
                return False
    return True