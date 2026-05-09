"""Temporizador basado en tiempo real (wall clock).

Sirve para cualquier acción con duración fija: cultivo, cocina, fundición, etc.
El progreso se calcula con datetime.now() (o un `now` inyectado en tests).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TimedAction:
    duration_seconds: float
    started_at: Optional[datetime] = field(default=None, repr=False)

    def start(self, when: Optional[datetime] = None) -> bool:
        """Inicia la acción. Si ya había una en curso, no hace nada y devuelve False."""
        if self.started_at is not None:
            return False
        self.started_at = when or datetime.now()
        return True

    def cancel(self) -> None:
        """Detiene la acción sin dar recompensa (ej. cancelar crafting)."""
        self.started_at = None

    @property
    def is_idle(self) -> bool:
        return self.started_at is None

    def is_active(self, now: Optional[datetime] = None) -> bool:
        """Hay un temporizador corriendo y aún no cumplió la duración."""
        if self.started_at is None:
            return False
        return not self.is_ready(now)

    def is_ready(self, now: Optional[datetime] = None) -> bool:
        """La duración ya transcurrió desde started_at."""
        if self.started_at is None:
            return False
        n = now or datetime.now()
        elapsed = (n - self.started_at).total_seconds()
        return elapsed >= self.duration_seconds

    def time_remaining_seconds(self, now: Optional[datetime] = None) -> float:
        """Segundos hasta completar; 0 si está listo o idle."""
        if self.started_at is None:
            return 0.0
        n = now or datetime.now()
        elapsed = (n - self.started_at).total_seconds()
        return max(0.0, self.duration_seconds - elapsed)

    def progress_ratio(self, now: Optional[datetime] = None) -> float:
        """Valor entre 0 y 1; 1 si está listo o idle sin acción."""
        if self.duration_seconds <= 0:
            return 1.0
        if self.started_at is None:
            return 0.0
        if self.is_ready(now):
            return 1.0
        n = now or datetime.now()
        elapsed = (n - self.started_at).total_seconds()
        return min(1.0, max(0.0, elapsed / self.duration_seconds))

    def finish_if_ready(self, now: Optional[datetime] = None) -> bool:
        """Si está listo, limpia el estado y devuelve True (listo para recompensa)."""
        if not self.is_ready(now):
            return False
        self.started_at = None
        return True
