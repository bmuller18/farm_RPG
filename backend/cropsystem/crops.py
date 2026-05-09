"""Cultivos: usan TimedAction para el crecimiento (misma pieza que cocina/fundición)."""

from ..timed_action import TimedAction


class Crop:
    def __init__(self, name, grow_seconds, reward):
        self.name = name
        self.reward = reward
        self._growth = TimedAction(duration_seconds=float(grow_seconds))

    @property
    def is_idle(self):
        return self._growth.is_idle

    @property
    def is_growing(self):
        return self._growth.is_active()

    def plant(self):
        if self._growth.start():
            print(f"{self.name} plantado")

    def is_ready(self):
        return self._growth.is_ready()

    def harvest(self):
        if self._growth.finish_if_ready():
            print(f"Recolectaste {self.reward}")
            return self.reward
        print("Todavia no esta listo")
        return None

    def time_remaining(self):
        return self._growth.time_remaining_seconds()
