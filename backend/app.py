"""Servidor Flask — Farm RPG API REST
Ejecutar desde la carpeta `backend/`:
    python app.py

Rutas disponibles:
    GET  /parcelas              → estado de todas las parcelas
    POST /plantar/<parcela_id>  → plantar un cultivo en una parcela
    POST /cosechar/<parcela_id> → cosechar si está listo
"""

from flask import Flask, jsonify, request

try:
    from backend.cropsystem.crops import Crop
except ImportError:
    from cropsystem.crops import Crop


app = Flask(__name__)


# ---------------------------------------------------------------------------
# Estado del juego (en memoria por ahora — Fase 2 lo persistimos en SQLite)
# ---------------------------------------------------------------------------

# Catálogo de semillas disponibles: nombre → (grow_seconds, reward_oro)
CATALOGO = {
    "trigo":     Crop("Trigo",     grow_seconds=5,  reward=10),
    "maiz":      Crop("Maíz",      grow_seconds=10, reward=20),
    "zanahoria": Crop("Zanahoria", grow_seconds=15, reward=35),
}

# 3 parcelas independientes, cada una puede tener un cultivo distinto
# Estructura: { id: { "crop": Crop | None, "semilla": str | None } }
parcelas = {
    1: {"crop": None, "semilla": None},
    2: {"crop": None, "semilla": None},
    3: {"crop": None, "semilla": None},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parcela_a_dict(parcela_id: int) -> dict:
    """Convierte el estado de una parcela a un dict serializable en JSON."""
    p = parcelas[parcela_id]
    crop = p["crop"]

    if crop is None:
        return {
            "id": parcela_id,
            "estado": "vacia",
            "semilla": None,
            "segundos_restantes": None,
            "progreso": None,
        }

    if crop.is_ready():
        estado = "lista"
    elif crop.is_growing:
        estado = "creciendo"
    else:
        estado = "vacia"

    return {
        "id": parcela_id,
        "estado": estado,
        "semilla": p["semilla"],
        "segundos_restantes": round(crop.time_remaining(), 1),
        "progreso": round(crop._growth.progress_ratio(), 2),
    }


def error(mensaje: str, codigo: int = 400):
    return jsonify({"ok": False, "error": mensaje}), codigo


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "ok": True,
        "mensaje": "Farm RPG API corriendo",
        "rutas": [
            "GET  /parcelas",
            "POST /plantar/<parcela_id>  body: { semilla: 'trigo' }",
            "POST /cosechar/<parcela_id>",
        ]
    })


@app.route("/parcelas", methods=["GET"])
def get_parcelas():
    """Devuelve el estado de todas las parcelas."""
    return jsonify({
        "ok": True,
        "parcelas": [parcela_a_dict(pid) for pid in parcelas],
    })


@app.route("/parcelas/<int:parcela_id>", methods=["GET"])
def get_parcela(parcela_id: int):
    """Devuelve el estado de una parcela específica."""
    if parcela_id not in parcelas:
        return error(f"Parcela {parcela_id} no existe. Válidas: 1, 2, 3", 404)

    return jsonify({"ok": True, "parcela": parcela_a_dict(parcela_id)})


@app.route("/plantar/<int:parcela_id>", methods=["POST"])
def plantar(parcela_id: int):
    """Planta un cultivo en la parcela indicada.

    Body JSON esperado:
        { "semilla": "trigo" }   (o "maiz", "zanahoria")
    """
    if parcela_id not in parcelas:
        return error(f"Parcela {parcela_id} no existe. Válidas: 1, 2, 3", 404)

    data = request.get_json(silent=True) or {}
    semilla = data.get("semilla", "").lower().strip()

    if not semilla:
        return error("Falta el campo 'semilla' en el body JSON.")

    if semilla not in CATALOGO:
        opciones = ", ".join(CATALOGO.keys())
        return error(f"Semilla '{semilla}' no existe. Opciones: {opciones}")

    p = parcelas[parcela_id]
    if p["crop"] is not None and not p["crop"].is_idle:
        return error(f"Parcela {parcela_id} ya tiene un cultivo en curso.")

    # Crear una instancia nueva de Crop para esta parcela
    # (el catálogo es la plantilla, no la usamos directamente)
    plantilla = CATALOGO[semilla]
    nuevo_crop = Crop(plantilla.name, plantilla._growth.duration_seconds, plantilla.reward)
    nuevo_crop.plant()

    parcelas[parcela_id] = {"crop": nuevo_crop, "semilla": semilla}

    return jsonify({
        "ok": True,
        "mensaje": f"{plantilla.name} plantado en parcela {parcela_id}.",
        "parcela": parcela_a_dict(parcela_id),
    }), 201


@app.route("/cosechar/<int:parcela_id>", methods=["POST"])
def cosechar(parcela_id: int):
    """Cosecha el cultivo de la parcela si ya está listo."""
    if parcela_id not in parcelas:
        return error(f"Parcela {parcela_id} no existe. Válidas: 1, 2, 3", 404)

    p = parcelas[parcela_id]
    crop = p["crop"]

    if crop is None or crop.is_idle:
        return error(f"Parcela {parcela_id} está vacía, no hay nada que cosechar.")

    if not crop.is_ready():
        restantes = round(crop.time_remaining(), 1)
        return error(f"Todavía no está listo. Faltan {restantes} segundos.")

    recompensa = crop.harvest()  # limpia el estado internamente
    parcelas[parcela_id] = {"crop": None, "semilla": None}  # parcela libre

    return jsonify({
        "ok": True,
        "mensaje": f"Cosechaste {p['semilla']} en parcela {parcela_id}.",
        "recompensa_oro": recompensa,
        "parcela": parcela_a_dict(parcela_id),
    })


# ---------------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------------

@app.route("/catalogo", methods=["GET"])
def get_catalogo():
    """Devuelve las semillas disponibles y sus características."""
    return jsonify({
        "ok": True,
        "semillas": [
            {
                "nombre": nombre,
                "grow_seconds": crop._growth.duration_seconds,
                "reward_oro": crop.reward,
            }
            for nombre, crop in CATALOGO.items()
        ]
    })


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)