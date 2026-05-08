from tkinter import CENTER
from turtle import color
import flet as ft
import time
from backend.cropsystem.crops import Crop

wheat = Crop("Trigo", 5, 10)

def main(page: ft.Page):

    estado_text = ft.Text("Estado: No plantado")
    timer_text = ft.Text("")
    reward_text = ft.Text("")
    texto_pantalla = ft.Text("0")  # 👈 ahora sí existe

    # 🔁 Loop que actualiza cada 1 segundo
    def update_ui():
        a = 0
        while True:
            a += 1
            texto_pantalla.value = str(a)  # 👈 actualizamos el texto
            page.update()
            time.sleep(1)

    def plant(e):
        wheat.plant()

    def harvest(e):
        reward = wheat.harvest()
        if reward:
            reward_text.value = f"Ganaste: {reward}"

    page.add(
        ft.Button(content="Click", on_click=plant(wheat)),
        texto_pantalla
    )

    page.run_thread(update_ui)

ft.app(target=main)