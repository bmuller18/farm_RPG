import flet as ft
from backend.cropsystem.crops import Crop

def main(page: ft.Page):
    wheat = Crop("Trigo", 5, 10)

    page.add(
         ft.Button(
            content="Mi botón",
            on_click=wheat.plant()
        )
    )

ft.app(target=main)