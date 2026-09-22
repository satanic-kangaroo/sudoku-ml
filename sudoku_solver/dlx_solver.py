"""
DLX Solver — Dancing Links / Algorithm X
Implementation of Knuth's Algorithm X for Exact Cover, applied to Sudoku.

Reference:
    Knuth, D. E. (2000). "Dancing links."
    Millennial Perspectives in Computer Science, 187-214.
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
        self.L = self      # left
        self.R = self      # right
        self.U = self      # up
        self.D = self      # down
        self.C = self      # column header this node belongs to
        self.row_id = -1   # which candidate row (0..728)
        self.size = 0      # only used on column headers


# ============================================================
# Constants: Sudoku → Exact Cover mapping
# ============================================================

N = 9
NUM_COLS = 4 * N * N       # 324
NUM_ROWS = N * N * N       # 729


def _col_cell(r: int, c: int) -> int:
    """Constraint: cell (r, c) has exactly one digit."""
    return r * N + c


def _col_row(r: int, d: int) -> int:
    """Constraint: row r contains digit d (1..9)."""
    return N * N + r * N + (d - 1)


def _col_col(c: int, d: int) -> int:
    """Constraint: column c contains digit d."""
    return 2 * N * N + c * N + (d - 1)


def _col_box(r: int, c: int, d: int) -> int:
    """Constraint: 3×3 box containing (r, c) has digit d."""
    box = (r // 3) * 3 + (c // 3)
    return 3 * N * N + box * N + (d - 1)


def _row_id(r: int, c: int, d: int) -> int:
    """Convert (r, c, d) into a candidate row id in [0, 729)."""
    return (r * N + c) * N + (d - 1)


def _decode_row(row_id: int) -> tuple[int, int, int]:
    """Inverse of _row_id."""
    d = row_id % N + 1
    cell = row_id // N
    r, c = divmod(cell, N)
    return r, c, d


# ============================================================
# DLX Build
# ============================================================

def _build_dlx() -> tuple[Node, list[Node]]:
    """
    Build the DLX structure for a 9×9 Sudoku.
    Returns (root, column_headers).
    """
    root = Node()

    # ----- 324 column headers -----
    cols: list[Node] = []
    for _ in range(NUM_COLS):
        col = Node()
        col.C = col          # header points to itself
        col.size = 0

        # insert at end of horizontal list
        col.L = root.L
        col.R = root
        root.L.R = col
        root.L = col

        cols.append(col)

    # ----- 729 candidate rows -----
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


def _add_row(cols: list[Node], col_indices: tuple, row_id: int) -> None:
    """Insert a new row (4 nodes) into the DLX structure."""
    first: Optional[Node] = None
    for idx in col_indices:
        col = cols[idx]
        node = Node()
        node.C = col
        node.row_id = row_id

        # insert at bottom of column
        node.U = col.U
        node.D = col
        col.U.D = node
        col.U = node

        # insert at end of row
        if first is None:
            first = node
        else:
            node.L = first.L
            node.R = first
            first.L.R = node
            first.L = node

        col.size += 1


# ============================================================
# Cover / Uncover (the "dancing" operations)
# ============================================================

def _cover(col: Node) -> None:
    """Remove column `col` and all its rows from the structure."""
    # Unlink column header horizontally
    col.R.L = col.L
    col.L.R = col.R

    # For each row in this column...
    i = col.D
    while i is not col:
        # ...unlink every node in that row vertically
        j = i.R
        while j is not i:
            j.D.U = j.U
            j.U.D = j.D
            j.C.size -= 1
            j = j.R
        i = i.D


def _uncover(col: Node) -> None:
    """Reverse _cover — restore column `col` and all its rows."""
    i = col.U
    while i is not col:
        j = i.L
        while j is not i:
            j.C.size += 1
            j.D.U = j
            j.U.D = j
            j = j.L
        i = i.U

    # Relink header back
    col.R.L = col
    col.L.R = col


# ============================================================
# Algorithm X (recursive search)
# ============================================================

def _search(root: Node, solution: list[int], out: list[list[int]],
            stats: dict, depth: int = 0) -> bool:
    """Recursive Algorithm X search with instrumentation."""
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
# Public API: solve a Sudoku board
# ============================================================

def solve_dlx(board: np.ndarray) -> tuple[bool, np.ndarray, dict]:
    """
    Solve a Sudoku board using DLX.

    Args:
        board: np.ndarray (9, 9) ints 0-9 (0 = empty)

    Returns:
        (solved, solution_board, stats)
            solved:         bool
            solution_board: np.ndarray (9,9) — valid only if solved
            stats:          dict with counters (nodes, steps, etc.)
    """
    # ---- Build DLX ----
    root, cols = _build_dlx()

    # ---- Disable candidates that conflict with given clues ----
    # For each given cell, cover the columns of the "correct" row so that
    # only that row remains, and remove all other rows in those columns.
    given_rows: list[int] = []
    for r in range(9):
        for c in range(9):
            d = int(board[r, c])
            if d != 0:
                given_rows.append(_row_id(r, c, d))

    # Mark all rows not in the given set for removal, by covering the
    # columns of the given rows' other digits... Actually simpler: just
    # forbid all rows that conflict with givens.
    #
    # We do this efficiently by covering the constraint columns for
    # givens, which removes conflicting rows automatically.

    # Approach: iterate through the DLX structure and identify rows that
    # violate givens. We can do this by checking each given (r, c, d):
    # all rows (r, c, d') with d' != d must go; all rows (r', c, d) with
    # r' != r must go; same for column and box.

    # For performance we just leave them in the DLX and handle conflicts
    # via a "forbidden rows" set.
    forbidden: set[int] = set()

    for r in range(9):
        for c in range(9):
            d = int(board[r, c])
            if d == 0:
                continue
            # Forbid all other digits in this cell
            for d2 in range(1, 10):
                if d2 != d:
                    forbidden.add(_row_id(r, c, d2))
            # Forbid same digit in same row / col / box (other cells)
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

    # ---- Remove forbidden rows from the structure ----
    # To do this cleanly: we cover the columns of *all* forbidden rows
    # in a way that permanently removes them. But that would break
    # backtracking. Instead, we can filter the columns' vertical lists.
    #
    # Simplest: after building, "cover" forbidden rows by walking each
    # column and unlinking forbidden nodes. Then we run search on the
    # modified structure — no backtracking needed since givens are fixed.

    def _unlink_forbidden(node: Node) -> None:
        """Permanently remove a row (all 4 nodes) from the structure."""
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

    # ---- Also "pin" the given rows by covering their columns ----
    # Since givens are fixed, we cover all their constraint columns so
    # the search never revisits them.
    seen_rows: list[Node] = []
    for row_id in given_rows:
        # Find the first node of this row: we stored it in cols[...] but
        # we didn't keep a pointer. Walk from a column: every given row
        # belongs to col_cell(r, c). Let's reconstruct (r, c, d).
        r, c, d = _decode_row(row_id)
        col = cols[_col_cell(r, c)]
        # Find node with matching row_id in this column
        i = col.D
        while i is not col and i.row_id != row_id:
            i = i.D
        if i is col:
            continue  # shouldn't happen

        # Cover all 4 columns touched by this row
        j = i.R
        while j is not i:
            _cover(j.C)
            j = j.R
        _cover(i.C)  # the cell column itself
        seen_rows.append(i)

    # ---- Run search on the reduced structure ----
    stats = {
        "forbidden_rows": len(forbidden),
        "given_rows": len(given_rows),
        "nodes": 0,
        "backtracks": 0,
        "dead_ends": 0,
        "max_depth": 0,
    }

    solution: list[list[int]] = []
    solved = _search(root, [], solution, stats)   # ← stats پاس داده می‌شه

    if not solved:
        return False, board.copy(), stats

    # ---- Reconstruct board from solution ----
    result = np.zeros((9, 9), dtype=int)
    for row_id in solution[0]:
        r, c, d = _decode_row(row_id)
        result[r, c] = d

    # ---- Fill in givens (they may have been "pinned" so absent) ----
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