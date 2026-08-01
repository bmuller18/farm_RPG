import time

import flet as ft

from backend.services.farm_service import FarmService

game = FarmService()
game.load()

SEED_OPTIONS = [
    ft.dropdown.Option(key=s["id"], text=f"{s['nombre']} ({s['coste_semilla']} oro)")
    for s in game.catalog_to_list()
]


def main(page: ft.Page):
    page.title = "Farm RPG"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    gold_text = ft.Text(f"Oro: {game.gold}", size=20, weight=ft.FontWeight.BOLD)
    message_text = ft.Text("", color=ft.Colors.GREEN_700)

    plot_widgets: dict[int, dict] = {}

    def show_message(text: str, error: bool = False):
        message_text.value = text
        message_text.color = ft.Colors.RED_700 if error else ft.Colors.GREEN_700

    def refresh_plot(plot_id: int):
        data = game.plot_to_dict(plot_id)
        widgets = plot_widgets[plot_id]
        widgets["status"].value = _status_label(data)
        widgets["progress"].value = data["progreso"] or 0
        widgets["timer"].value = _timer_label(data)
        widgets["harvest_btn"].disabled = data["estado"] != "lista"
        widgets["plant_btn"].disabled = data["estado"] != "vacia"
        widgets["seed_dropdown"].disabled = data["estado"] != "vacia"

    def refresh_all():
        gold_text.value = f"Oro: {game.gold}"
        for plot_id in game.plots:
            refresh_plot(plot_id)

    def _status_label(data: dict) -> str:
        estado = data["estado"]
        if estado == "vacia":
            return "Vacía"
        if estado == "creciendo":
            return f"Creciendo: {data['nombre_cultivo']}"
        return f"Lista: {data['nombre_cultivo']}"

    def _timer_label(data: dict) -> str:
        if data["estado"] == "creciendo":
            return f"{int(data['segundos_restantes'])} s restantes"
        if data["estado"] == "lista":
            return "Listo para cosechar"
        return "Elige semilla y planta"

    def make_plant_handler(plot_id: int):
        def handler(_):
            semilla = plot_widgets[plot_id]["seed_dropdown"].value
            if not semilla:
                show_message("Elige una semilla.", error=True)
                page.update()
                return
            result = game.plant(plot_id, semilla)
            if not result.ok:
                show_message(result.message, error=True)
            else:
                show_message(result.message)
            refresh_all()
            page.update()

        return handler

    def make_harvest_handler(plot_id: int):
        def handler(_):
            result = game.harvest(plot_id)
            if not result.ok:
                show_message(result.message, error=True)
            else:
                show_message(result.message)
            refresh_all()
            page.update()

        return handler

    plot_cards = []
    for plot_id in sorted(game.plots):
        status = ft.Text("")
        timer = ft.Text("")
        progress = ft.ProgressBar(value=0, width=260)
        seed_dropdown = ft.Dropdown(
            options=SEED_OPTIONS,
            value="trigo",
            width=260,
            label="Semilla",
        )
        plant_btn = ft.ElevatedButton("Plantar", on_click=make_plant_handler(plot_id))
        harvest_btn = ft.ElevatedButton("Cosechar", on_click=make_harvest_handler(plot_id))

        plot_widgets[plot_id] = {
            "status": status,
            "timer": timer,
            "progress": progress,
            "seed_dropdown": seed_dropdown,
            "plant_btn": plant_btn,
            "harvest_btn": harvest_btn,
        }

        plot_cards.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"Parcela {plot_id}", weight=ft.FontWeight.BOLD),
                            status,
                            progress,
                            timer,
                            seed_dropdown,
                            ft.Row([plant_btn, harvest_btn]),
                        ],
                        spacing=8,
                    ),
                    padding=16,
                )
            )
        )

    catalog_lines = [
        ft.Text(
            f"{s['nombre']}: {s['grow_seconds']}s → +{s['reward_oro']} oro "
            f"(semilla {s['coste_semilla']} oro)",
            size=12,
        )
        for s in game.catalog_to_list()
    ]

    page.add(
        ft.Text("Farm RPG", size=28, weight=ft.FontWeight.BOLD),
        gold_text,
        message_text,
        ft.Row(plot_cards, wrap=True, spacing=16),
        ft.Divider(),
        ft.Text("Catálogo de semillas", weight=ft.FontWeight.BOLD),
        *catalog_lines,
    )

    def update_ui():
        while True:
            refresh_all()
            page.update()
            time.sleep(1)

    refresh_all()
    page.run_thread(update_ui)


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
