"""Estado de una parcela de cultivo."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from backend.cropsystem.crops import Crop


class Plot:
    def __init__(self, plot_id: int):
        self.plot_id = plot_id
        self.crop: Optional["Crop"] = None
        self.semilla: Optional[str] = None

    def is_empty(self) -> bool:
        return self.crop is None or self.crop.is_idle

    def is_occupied(self) -> bool:
        return self.crop is not None and not self.crop.is_idle

    def to_dict(self) -> dict:
        if not self.is_occupied():
            return {
                "id": self.plot_id,
                "estado": "vacia",
                "semilla": None,
                "nombre_cultivo": None,
                "segundos_restantes": None,
                "progreso": None,
            }

        crop = self.crop
        assert crop is not None

        if crop.is_ready():
            estado = "lista"
        elif crop.is_growing:
            estado = "creciendo"
        else:
            estado = "vacia"

        return {
            "id": self.plot_id,
            "estado": estado,
            "semilla": self.semilla,
            "nombre_cultivo": crop.name,
            "segundos_restantes": round(crop.time_remaining(), 1),
            "progreso": round(crop.progress_ratio(), 2),
        }
