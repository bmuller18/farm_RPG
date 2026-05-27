import flet as ft
import time

from backend.cropsystem.crops import wheat
from backend.timed_action import TimedAction

cooking = TimedAction(duration_seconds=8.0)


def main(page: ft.Page):

    estado_text = ft.Text("Estado: No plantado")
    timer_text = ft.Text("")
    cooking_text = ft.Text("Cocina: idle (ejemplo)")
    texto_pantalla = ft.Text("0")

    def refresh_labels():
        if wheat.is_ready():
            estado_text.value = "Estado: Listo para cosechar"
        elif wheat.is_idle:
            estado_text.value = "Estado: No plantado"
        else:
            estado_text.value = "Estado: Creciendo"
        if wheat.is_growing:
            timer_text.value = f"Trigo — restante: {int(wheat.time_remaining())} s"
        elif wheat.is_ready():
            timer_text.value = "Trigo — listo para cosechar"
        else:
            timer_text.value = "Trigo — sin plantar"
        if cooking.is_idle:
            cooking_text.value = "Cocina (ejemplo): idle — botón Cocinar para iniciar 8s"
        elif cooking.is_ready():
            cooking_text.value = "Cocina (ejemplo): listo — Completar"
        else:
            cooking_text.value = f"Cocina (ejemplo): {int(cooking.time_remaining_seconds())} s restantes"

    def update_ui():
        segundos = 0
        while True:
            segundos += 1
            texto_pantalla.value = str(segundos)
            refresh_labels()
            page.update()
            time.sleep(1)

    def plant(_):
        wheat.plant()
        refresh_labels()
        page.update()

    def harvest(_):
        reward = wheat.harvest()
        if reward is not None:
            estado_text.value = f"Cosechaste: {reward}"
        refresh_labels()
        page.update()

    def start_cooking(_):
        cooking.start()

    def finish_cooking(_):
        if cooking.finish_if_ready():
            cooking_text.value = "Cocina (ejemplo): servido"
            page.update()

    page.add(
        estado_text,
        timer_text,
        ft.Row(
            [
                ft.ElevatedButton("Plantar trigo", on_click=plant),
                ft.ElevatedButton("Cosechar", on_click=harvest),
            ]
        ),
        ft.Divider(),
        cooking_text,
        ft.Row(
            [
                ft.ElevatedButton("Cocinar (8s)", on_click=start_cooking),
                ft.ElevatedButton("Servir si listo", on_click=finish_cooking),
            ]
        ),
        ft.Divider(),
        ft.Text("Reloj UI:"),
        texto_pantalla,
    )

    refresh_labels()
    page.run_thread(update_ui)


ft.app(target=main, view=ft.AppView.WEB_BROWSER)
