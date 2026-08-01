"""Casos de uso del loop de farming."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from backend.cropsystem.crops import Crop
    from backend.domain.crop_definition import CROP_CATALOG, CropDefinition
    from backend.domain.plot import Plot
    from backend.infra.game_repository import (
        DEFAULT_PLAYER_ID,
        NUM_PLOTS,
        GameRepository,
        STARTING_GOLD,
    )
except ImportError:
    from cropsystem.crops import Crop
    from domain.crop_definition import CROP_CATALOG, CropDefinition
    from domain.plot import Plot
    from infra.game_repository import (
        DEFAULT_PLAYER_ID,
        NUM_PLOTS,
        GameRepository,
        STARTING_GOLD,
    )


@dataclass
class ActionResult:
    ok: bool
    message: str
    reward_gold: Optional[int] = None
    plot: Optional[dict] = None


class FarmService:
    def __init__(
        self,
        repository: Optional[GameRepository] = None,
        db_path: Optional[Path] = None,
        player_id: int = DEFAULT_PLAYER_ID,
    ):
        self.repo = repository or GameRepository(db_path)
        self.player_id = player_id
        self.player_name = "Jugador"
        self.gold = STARTING_GOLD
        self.plots: dict[int, Plot] = {i: Plot(i) for i in range(1, NUM_PLOTS + 1)}

    def load(self) -> None:
        self.repo.init_schema()
        player = self.repo.get_or_create_player(self.player_id)
        self.player_name = player["name"]
        self.gold = player["money"]

        saved_plots = self.repo.load_plots(self.player_id)
        for slot, data in saved_plots.items():
            if data is None:
                self.plots[slot] = Plot(slot)
                continue

            semilla = data["semilla"]
            if semilla not in CROP_CATALOG:
                self.plots[slot] = Plot(slot)
                continue

            crop = Crop(
                data["crop_name"],
                data["grow_seconds"],
                data["reward_gold"],
            )
            crop.restore_planted(datetime.fromisoformat(data["started_at"]))

            plot = Plot(slot)
            plot.crop = crop
            plot.semilla = semilla
            self.plots[slot] = plot

    def save(self) -> None:
        self.repo.save_player(self.player_id, self.player_name, self.gold)
        self.repo.save_all_plots(self.player_id, self.plots)

    def get_plot(self, plot_id: int) -> Optional[Plot]:
        return self.plots.get(plot_id)

    def plot_to_dict(self, plot_id: int) -> dict:
        plot = self.plots[plot_id]
        return plot.to_dict()

    def all_plots_to_dict(self) -> list[dict]:
        return [self.plots[i].to_dict() for i in sorted(self.plots)]

    def catalog_to_list(self) -> list[dict]:
        return [
            {
                "id": defn.id,
                "nombre": defn.name,
                "grow_seconds": defn.grow_seconds,
                "reward_oro": defn.reward_gold,
                "coste_semilla": defn.seed_cost,
            }
            for defn in CROP_CATALOG.values()
        ]

    def get_definition(self, semilla: str) -> Optional[CropDefinition]:
        return CROP_CATALOG.get(semilla.lower().strip())

    def plant(self, plot_id: int, semilla: str) -> ActionResult:
        if plot_id not in self.plots:
            return ActionResult(False, f"Parcela {plot_id} no existe.")

        definition = self.get_definition(semilla)
        if definition is None:
            opciones = ", ".join(CROP_CATALOG.keys())
            return ActionResult(False, f"Semilla '{semilla}' no existe. Opciones: {opciones}")

        plot = self.plots[plot_id]
        if plot.is_occupied():
            if plot.crop and plot.crop.is_ready():
                return ActionResult(False, f"Parcela {plot_id}: cosecha antes de plantar de nuevo.")
            return ActionResult(False, f"Parcela {plot_id} ya tiene un cultivo en curso.")

        if self.gold < definition.seed_cost:
            return ActionResult(
                False,
                f"No tienes oro suficiente. Necesitas {definition.seed_cost}, tienes {self.gold}.",
            )

        self.gold -= definition.seed_cost
        crop = Crop(definition.name, definition.grow_seconds, definition.reward_gold)
        crop.plant()
        plot.crop = crop
        plot.semilla = definition.id
        self.save()

        return ActionResult(
            True,
            f"{definition.name} plantado en parcela {plot_id}.",
            plot=plot.to_dict(),
        )

    def harvest(self, plot_id: int) -> ActionResult:
        if plot_id not in self.plots:
            return ActionResult(False, f"Parcela {plot_id} no existe.")

        plot = self.plots[plot_id]
        if plot.is_empty():
            return ActionResult(False, f"Parcela {plot_id} está vacía.")

        crop = plot.crop
        assert crop is not None

        if not crop.is_ready():
            restantes = round(crop.time_remaining(), 1)
            return ActionResult(False, f"Todavía no está listo. Faltan {restantes} segundos.")

        reward = crop.harvest()
        if reward is None:
            return ActionResult(False, "No se pudo cosechar.")

        semilla = plot.semilla
        self.gold += reward
        plot.crop = None
        plot.semilla = None
        self.save()

        return ActionResult(
            True,
            f"Cosechaste {semilla} en parcela {plot_id}. +{reward} oro",
            reward_gold=reward,
            plot=plot.to_dict(),
        )
