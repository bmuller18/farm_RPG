"""Cultivos: usan TimedAction para el crecimiento (misma pieza que cocina/fundición)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

try:
    from backend.timed_action import TimedAction
except ImportError:
    from timed_action import TimedAction


class Crop:
    def __init__(self, name, grow_seconds, reward):
        self.name = name
        self.reward = reward
        self._grow_seconds = float(grow_seconds)
        self._growth = TimedAction(duration_seconds=self._grow_seconds)

    @property
    def grow_seconds(self) -> float:
        return self._grow_seconds

    @property
    def started_at(self) -> Optional[datetime]:
        return self._growth.started_at

    @property
    def is_idle(self):
        return self._growth.is_idle

    @property
    def is_growing(self):
        return self._growth.is_active()

    def plant(self):
        return self._growth.start()

    def restore_planted(self, started_at: datetime) -> None:
        """Restaura un cultivo ya plantado (carga desde SQLite)."""
        self._growth.started_at = started_at

    def is_ready(self, now: Optional[datetime] = None):
        return self._growth.is_ready(now)

    def harvest(self, now: Optional[datetime] = None):
        if self._growth.finish_if_ready(now):
            return self.reward
        return None

    def time_remaining(self, now: Optional[datetime] = None):
        return self._growth.time_remaining_seconds(now)

    def progress_ratio(self, now: Optional[datetime] = None):
        return self._growth.progress_ratio(now)
