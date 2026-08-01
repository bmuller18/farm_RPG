import sys
from pathlib import Path

import pytest

_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from services.farm_service import FarmService
import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_game = FarmService(db_path=tmp_path / "api_test.db")
    test_game.load()
    monkeypatch.setattr(app, "game", test_game)
    return app.app.test_client()


def test_home():
    client = app.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True


def test_plant_and_harvest_flow(client):
    response = client.post("/plantar/1", json={"semilla": "trigo"})
    assert response.status_code == 201

    plot = client.get("/parcelas/1").get_json()["parcela"]
    assert plot["estado"] in {"creciendo", "lista"}

    from datetime import datetime, timedelta

    crop = app.game.get_plot(1).crop
    crop.restore_planted(datetime.now() - timedelta(seconds=10))

    response = client.post("/cosechar/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["recompensa_oro"] == 10
