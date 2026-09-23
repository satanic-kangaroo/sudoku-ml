"""
DLX Solver — Dancing Links / Algorithm X
Implementation of Knuth's Algorithm X for Exact Cover, applied to Sudoku.
"""

from __future__ import annotations
from typing import Optional
import numpy as np


# ============================================================
# Data Structure: Circular Doubly-Linked 2D Node
# ============================================================

class Node:
    """A node in the DLX 2D linked structure."""
    __slots__ = ("L", "R", "U", "D", "C", "row_id", "size")

    def __init__(self):
        self.L = self
        self.R = self
        self.U = self
        self.D = self
        self.C = self
        self.row_id = -1
        self.size = 0


# ============================================================
# Constants: Sudoku → Exact Cover mapping
# ============================================================

N = 9
NUM_COLS = 4 * N * N
NUM_ROWS = N * N * N


def _col_cell(r: int, c: int) -> int:
    return r * N + c


def _col_row(r: int, d: int) -> int:
    return N * N + r * N + (d - 1)


def _col_col(c: int, d: int) -> int:
    return 2 * N * N + c * N + (d - 1)


def _col_box(r: int, c: int, d: int) -> int:
    box = (r // 3) * 3 + (c // 3)
    return 3 * N * N + box * N + (d - 1)


def _row_id(r: int, c: int, d: int) -> int:
    return (r * N + c) * N + (d - 1)


def _decode_row(row_id: int):
    d = row_id % N + 1
    cell = row_id // N
    r, c = divmod(cell, N)
    return r, c, d


# ============================================================
# DLX Build
# ============================================================

def _build_dlx():
    """Build the DLX structure for a 9×9 Sudoku."""
    root = Node()

    cols = []
    for _ in range(NUM_COLS):
        col = Node()
        col.C = col
        col.size = 0

        col.L = root.L
        col.R = root
        root.L.R = col
        root.L = col

        cols.append(col)

    for r in range(N):
        for c in range(N):
            for d in range(1, N + 1):
                row_id = _row_id(r, c, d)
                col_indices = (
                    _col_cell(r, c),
                    _col_row(r, d),
                    _col_col(c, d),
                    _col_box(r, c, d),
                )
                _add_row(cols, col_indices, row_id)

    return root, cols


def _add_row(cols, col_indices, row_id):
    first: Optional[Node] = None
    for idx in col_indices:
        col = cols[idx]
        node = Node()
        node.C = col
        node.row_id = row_id

        node.U = col.U
        node.D = col
        col.U.D = node
        col.U = node

        if first is None:
            first = node
        else:
            node.L = first.L
            node.R = first
            first.L.R = node
            first.L = node

        col.size += 1


# ============================================================
# Cover / Uncover
# ============================================================

def _cover(col: Node) -> None:
    col.R.L = col.L
    col.L.R = col.R

    i = col.D
    while i is not col:
        j = i.R
        while j is not i:
            j.D.U = j.U
            j.U.D = j.D
            j.C.size -= 1
            j = j.R
        i = i.D


def _uncover(col: Node) -> None:
    i = col.U
    while i is not col:
        j = i.L
        while j is not i:
            j.C.size += 1
            j.D.U = j
            j.U.D = j
            j = j.L
        i = i.U

    col.R.L = col
    col.L.R = col


# ============================================================
# Algorithm X (recursive search with instrumentation)
# ============================================================

def _search(root: Node, solution: list, out: list, stats: dict, depth: int = 0) -> bool:
    """Recursive Algorithm X search with stats."""
    stats["nodes"] = stats.get("nodes", 0) + 1
    if depth > stats.get("max_depth", 0):
        stats["max_depth"] = depth

    if root.R is root:
        out.append(solution.copy())
        return True

    # MRV heuristic
    c = root.R
    min_size = c.size
    j = c.R
    while j is not root:
        if j.size < min_size:
            min_size = j.size
            c = j
            if min_size == 1:
                break
        j = j.R

    if min_size == 0:
        stats["dead_ends"] = stats.get("dead_ends", 0) + 1
        return False

    _cover(c)

    r = c.D
    while r is not c:
        solution.append(r.row_id)

        j = r.R
        while j is not r:
            _cover(j.C)
            j = j.R

        if _search(root, solution, out, stats, depth + 1):
            return True

        j = r.L
        while j is not r:
            _uncover(j.C)
            j = j.L

        solution.pop()
        r = r.D
        stats["backtracks"] = stats.get("backtracks", 0) + 1

    _uncover(c)
    return False


# ============================================================
# Public API
# ============================================================

def solve_dlx(board: np.ndarray):
    """
    Solve a Sudoku board using DLX.

    Returns:
        (solved, solution_board, stats_dict)
    """
    root, cols = _build_dlx()

    # Forbidden rows based on given clues
    forbidden = set()
    given_rows = []

    for r in range(9):
        for c in range(9):
            d = int(board[r, c])
            if d == 0:
                continue
            given_rows.append(_row_id(r, c, d))
            for d2 in range(1, 10):
                if d2 != d:
                    forbidden.add(_row_id(r, c, d2))
            for cc in range(9):
                if cc != c:
                    forbidden.add(_row_id(r, cc, d))
            for rr in range(9):
                if rr != r:
                    forbidden.add(_row_id(rr, c, d))
            br, bc = 3 * (r // 3), 3 * (c // 3)
            for rr in range(br, br + 3):
                for cc in range(bc, bc + 3):
                    if (rr, cc) != (r, c):
                        forbidden.add(_row_id(rr, cc, d))

    def _unlink_forbidden(node: Node) -> None:
        j = node
        while True:
            j.D.U = j.U
            j.U.D = j.D
            j.C.size -= 1
            j = j.R
            if j is node:
                break

    for col in cols:
        i = col.D
        while i is not col:
            nxt = i.D
            if i.row_id in forbidden:
                _unlink_forbidden(i)
            i = nxt

    # Pin given rows
    seen_rows = []
    for row_id in given_rows:
        r, c, d = _decode_row(row_id)
        col = cols[_col_cell(r, c)]
        i = col.D
        while i is not col and i.row_id != row_id:
            i = i.D
        if i is col:
            continue
        j = i.R
        while j is not i:
            _cover(j.C)
            j = j.R
        _cover(i.C)
        seen_rows.append(i)

    stats = {
        "forbidden_rows": len(forbidden),
        "given_rows": len(given_rows),
        "nodes": 0,
        "backtracks": 0,
        "dead_ends": 0,
        "max_depth": 0,
    }

    solution: list = []
    solved = _search(root, [], solution, stats)

    if not solved:
        return False, board.copy(), stats

    result = np.zeros((9, 9), dtype=int)
    for row_id in solution[0]:
        r, c, d = _decode_row(row_id)
        result[r, c] = d

    for r in range(9):
        for c in range(9):
            if board[r, c] != 0:
                result[r, c] = board[r, c]

    stats["solution_size"] = len(solution[0])
    return True, result, stats


def validate_solution(board: np.ndarray) -> bool:
    """Check that a completed board satisfies all Sudoku rules."""
    target = set(range(1, 10))
    for i in range(9):
        if set(board[i, :]) != target:
            return False
        if set(board[:, i]) != target:
            return False
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            if set(board[br:br + 3, bc:bc + 3].flatten()) != target:
                return False
    return True

def count_solutions(board: np.ndarray, limit: int = 2) -> int:
    """
    Count the number of solutions up to `limit`, using DLX.

    Args:
        board: 9×9 puzzle (0 = empty)
        limit: stop counting after finding this many solutions

    Returns:
        Number of solutions found (at most `limit`).
    """
    root, cols = _build_dlx()

    # ---- Forbid rows that conflict with givens ----
    forbidden = set()

    for r in range(9):
        for c in range(9):
            d = int(board[r, c])
            if d == 0:
                continue

            for d2 in range(1, 10):
                if d2 != d:
                    forbidden.add(_row_id(r, c, d2))

            for cc in range(9):
                if cc != c:
                    forbidden.add(_row_id(r, cc, d))

            for rr in range(9):
                if rr != r:
                    forbidden.add(_row_id(rr, c, d))

            br, bc = 3 * (r // 3), 3 * (c // 3)
            for rr in range(br, br + 3):
                for cc in range(bc, bc + 3):
                    if (rr, cc) != (r, c):
                        forbidden.add(_row_id(rr, cc, d))

    def _unlink_forbidden(node: Node) -> None:
        j = node
        while True:
            j.D.U = j.U
            j.U.D = j.D
            j.C.size -= 1
            j = j.R
            if j is node:
                break

    for col in cols:
        i = col.D
        while i is not col:
            nxt = i.D
            if i.row_id in forbidden:
                _unlink_forbidden(i)
            i = nxt

    # ---- Pin given rows by covering their columns ----
    for r in range(9):
        for c in range(9):
            d = int(board[r, c])
            if d == 0:
                continue
            row_id = _row_id(r, c, d)
            col = cols[_col_cell(r, c)]
            i = col.D
            while i is not col and i.row_id != row_id:
                i = i.D
            if i is col:
                continue

            j = i.R
            while j is not i:
                _cover(j.C)
                j = j.R
            _cover(i.C)

    # ---- Count solutions ----
    counter = [0]

    def _search_count(root: Node, depth: int = 0) -> None:
        if counter[0] >= limit:
            return

        if root.R is root:
            counter[0] += 1
            return

        # MRV heuristic
        c = root.R
        min_size = c.size
        j = c.R
        while j is not root:
            if j.size < min_size:
                min_size = j.size
                c = j
                if min_size == 1:
                    break
            j = j.R

        if min_size == 0:
            return

        _cover(c)

        r = c.D
        while r is not c:
            if counter[0] >= limit:
                break

            j = r.R
            while j is not r:
                _cover(j.C)
                j = j.R

            _search_count(root, depth + 1)

            j = r.L
            while j is not r:
                _uncover(j.C)
                j = j.L

            r = r.D

        _uncover(c)

    _search_count(root)
    return counter[0]