"""Definiciones fijas de cultivos (catálogo de semillas)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CropDefinition:
    id: str
    name: str
    grow_seconds: float
    reward_gold: int
    seed_cost: int = 0


CROP_CATALOG: dict[str, CropDefinition] = {
    "trigo": CropDefinition("trigo", "Trigo", 5.0, 10, seed_cost=5),
    "maiz": CropDefinition("maiz", "Maíz", 10.0, 20, seed_cost=8),
    "zanahoria": CropDefinition("zanahoria", "Zanahoria", 15.0, 35, seed_cost=12),
}
