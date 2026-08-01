"""Servidor Flask — Farm RPG API REST.

Ejecutar desde la raíz del proyecto:
    python -m backend.app

O desde backend/:
    python app.py
"""

from flask import Flask, jsonify, request

try:
    from backend.services.farm_service import FarmService
except ImportError:
    from services.farm_service import FarmService


app = Flask(__name__)
game = FarmService()
game.load()


def error(mensaje: str, codigo: int = 400):
    return jsonify({"ok": False, "error": mensaje}), codigo


@app.route("/")
def home():
    return jsonify({
        "ok": True,
        "mensaje": "Farm RPG API corriendo",
        "rutas": [
            "GET  /jugador",
            "GET  /parcelas",
            "GET  /parcelas/<id>",
            "POST /plantar/<id>  body: { semilla: 'trigo' }",
            "POST /cosechar/<id>",
            "GET  /catalogo",
        ],
    })


@app.route("/jugador", methods=["GET"])
def get_jugador():
    return jsonify({
        "ok": True,
        "jugador": {
            "id": game.player_id,
            "nombre": game.player_name,
            "oro": game.gold,
        },
    })


@app.route("/parcelas", methods=["GET"])
def get_parcelas():
    return jsonify({
        "ok": True,
        "parcelas": game.all_plots_to_dict(),
    })


@app.route("/parcelas/<int:parcela_id>", methods=["GET"])
def get_parcela(parcela_id: int):
    if parcela_id not in game.plots:
        return error(f"Parcela {parcela_id} no existe. Válidas: 1, 2, 3", 404)

    return jsonify({"ok": True, "parcela": game.plot_to_dict(parcela_id)})


@app.route("/plantar/<int:parcela_id>", methods=["POST"])
def plantar(parcela_id: int):
    data = request.get_json(silent=True) or {}
    semilla = data.get("semilla", "").lower().strip()

    if not semilla:
        return error("Falta el campo 'semilla' en el body JSON.")

    result = game.plant(parcela_id, semilla)
    if not result.ok:
        status = 404 if "no existe" in result.message and "Semilla" not in result.message else 400
        return error(result.message, status)

    return jsonify({
        "ok": True,
        "mensaje": result.message,
        "oro": game.gold,
        "parcela": result.plot,
    }), 201


@app.route("/cosechar/<int:parcela_id>", methods=["POST"])
def cosechar(parcela_id: int):
    result = game.harvest(parcela_id)
    if not result.ok:
        status = 404 if "no existe" in result.message else 400
        return error(result.message, status)

    return jsonify({
        "ok": True,
        "mensaje": result.message,
        "recompensa_oro": result.reward_gold,
        "oro": game.gold,
        "parcela": result.plot,
    })


@app.route("/catalogo", methods=["GET"])
def get_catalogo():
    return jsonify({
        "ok": True,
        "semillas": game.catalog_to_list(),
    })


if __name__ == "__main__":
    app.run(debug=True)
