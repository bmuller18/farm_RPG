import flet as ft
import time
import asyncio

from backend.cropsystem.crops import Crop

wheat = Crop("Trigo", 5, 10)

def main(page: ft.Page):

    def plant(e):
        wheat.plant()

    def harvest(e):
        wheat.harvest()

    page.add(
        ft.Button(content="Cosechar", on_click=harvest),
        ft.Button(content="Plantar", on_click=plant)
    )

ft.app(target=main)