"""Session history for solved puzzles."""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np


# ============================================================
# Data model
# ============================================================

@dataclass
class SolveRecord:
    """One completed solve."""

    board:           np.ndarray
    solution:        np.ndarray
    solved:          bool
    difficulty:      dict           # {"label", "emoji", "color"}
    solver_used:     str            # "dlx" | "backtracking"
    solver_time_ms:  float
    source:          str = "upload" # upload | sample | generated | camera
    thumbnail_png:   Optional[bytes] = None
    timestamp:       datetime = field(default_factory=datetime.now)
    id:              str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def to_dict(self) -> dict:
        return {
            "board":          self.board,
            "solution":       self.solution,
            "solved":         self.solved,
            "difficulty":     self.difficulty,
            "solver_used":    self.solver_used,
            "solver_time_ms": self.solver_time_ms,
            "source":         self.source,
            "thumbnail_png":  self.thumbnail_png,
            "timestamp":      self.timestamp,
            "id":             self.id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SolveRecord":
        return cls(**d)


# ============================================================
# Store
# ============================================================

class HistoryStore:
    """A bounded FIFO store of SolveRecords."""

    def __init__(self, max_items: int = 20):
        self.max_items = max_items
        self._items: list[SolveRecord] = []

    def add(self, record: SolveRecord) -> None:
        # Avoid duplicates: if the last record has the same board, replace it
        if self._items:
            last = self._items[-1]
            if np.array_equal(last.board, record.board):
                self._items[-1] = record
                return

        self._items.append(record)
        # Enforce FIFO cap
        if len(self._items) > self.max_items:
            self._items = self._items[-self.max_items:]

    def all(self) -> list[SolveRecord]:
        return list(self._items)

    def latest(self) -> Optional[SolveRecord]:
        return self._items[-1] if self._items else None

    def get(self, record_id: str) -> Optional[SolveRecord]:
        for r in self._items:
            if r.id == record_id:
                return r
        return None

    def remove(self, record_id: str) -> None:
        self._items = [r for r in self._items if r.id != record_id]

    def clear(self) -> None:
        self._items = []

    def __len__(self) -> int:
        return len(self._items)


# ============================================================
# Thumbnail helper
# ============================================================

def make_thumbnail(img_bgr, size: int = 80) -> Optional[bytes]:
    """Generate a small PNG thumbnail from a BGR image."""
    if img_bgr is None:
        return None
    try:
        import cv2
        h, w = img_bgr.shape[:2]
        scale = size / max(h, w)
        if scale < 1:
            img_bgr = cv2.resize(
                img_bgr, (int(w * scale), int(h * scale)),
                interpolation=cv2.INTER_AREA,
            )
        ok, buf = cv2.imencode(".png", img_bgr)
        return buf.tobytes() if ok else None
    except Exception:
        return None


# ============================================================
# Relative time helper
# ============================================================

def relative_time(dt: datetime) -> str:
    """Format a timestamp as 'just now', '2 min ago', etc."""
    delta = datetime.now() - dt
    secs = int(delta.total_seconds())
    if secs < 5:
        return "just now"
    if secs < 60:
        return f"{secs}s ago"
    mins = secs // 60
    if mins < 60:
        return f"{mins} min ago"
    hours = mins // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"